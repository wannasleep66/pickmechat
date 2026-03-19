import asyncio
import email
import inspect
from contextlib import suppress
from email.header import decode_header
from email.message import Message
from email.utils import parseaddr
from typing import (
    Any,
    AsyncContextManager,
    Callable,
    Self,
    TypeVar,
)

import aioimaplib
from dishka import AsyncContainer, Provider, Scope, from_context
from dishka.integrations.base import wrap_injection
from loguru import logger
from pydantic import BaseModel, EmailStr

from app.settings import EmailSettings

DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])


class EmailSender(BaseModel):
    name: str | None = None
    address: EmailStr


class EmailMessage(BaseModel):
    subject: str
    sender: EmailSender
    content: str


class PollerProvider(Provider):
    scope = Scope.REQUEST

    message = from_context(EmailMessage)


class Route:
    def __init__(
        self: Self,
        handler: Callable[..., Any],
        sender: str = "",
        subject: str = "",
    ) -> None:
        self.handler = handler
        self.sender = sender
        self.subject = subject

    def match(self: Self, message: EmailMessage) -> bool:
        return all(
            [
                not self.sender or self.sender == message.sender,
                not self.subject or self.subject == message.subject,
            ]
        )


class Router:
    def __init__(
        self: Self,
    ) -> None:
        self._routes: list[Route] = []

    @property
    def routes(self: Self) -> list[Route]:
        return self._routes

    def message(
        self: Self, subject: str = "", sender=""
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.add_route(func, subject=subject, sender=sender)
            return func

        return decorator

    def add_route(
        self: Self, handler: Callable[..., Any], subject: str = "", sender: str = ""
    ) -> None:
        self._routes.append(Route(handler=handler, subject=subject, sender=sender))


class Poller:
    def __init__(
        self: Self,
        *,
        settings: EmailSettings,
        container: AsyncContainer,
        lifespan: Callable[[Self], AsyncContextManager] | None = None,
    ) -> None:
        self.settings = settings
        self.container = container
        self.router = Router()
        self.lifespan = lifespan

    async def run(self: Self) -> None:
        if self.lifespan:
            async with self.lifespan(self):
                await self._loop()

        await self._loop()

    def include_router(self: Self, router: Router) -> None:
        for route in router.routes:
            self.router.add_route(
                route.handler, subject=route.subject, sender=route.sender
            )

    def message(
        self: Self, *, subject: str = "", sender: str = ""
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.router.add_route(func, subject=subject, sender=sender)
            return func

        return decorator

    async def _loop(self: Self) -> None:
        while True:
            try:
                await self._poll()
            except Exception:
                logger.exception("Poller crashed, reconecting in 5s")
                await asyncio.sleep(5)

    async def _poll(self: Self) -> None:
        while True:
            client: aioimaplib.IMAP4_SSL | None = None

            try:
                client = aioimaplib.IMAP4_SSL(
                    host=self.settings.imap_host,
                    port=self.settings.imap_port,
                    timeout=30,
                )

                await asyncio.wait_for(client.wait_hello_from_server(), timeout=15)

                await client.login(self.settings.user, self.settings.password)
                await client.select("INBOX")

                logger.info("Connected to IMAP")

                while True:
                    status, data = await client.search("UNSEEN")
                    if status == "OK" and data and data[0]:
                        seqnums = data[0].decode().split()
                        for seqn in seqnums:
                            await self._process_message(client, seqn)

                    await client.idle_start(timeout=300)
                    with suppress(asyncio.TimeoutError):
                        await asyncio.wait_for(client.wait_server_push(), timeout=10)
                    client.idle_done()
            except Exception as exc:
                logger.error(f"Connection lost or error: {exc}. Retrying in 5s...")
                await asyncio.sleep(5)
            finally:
                if client:
                    await client.logout()

    async def _process_message(
        self: Self, client: aioimaplib.IMAP4_SSL, seqnum: str
    ) -> None:
        msg_obj = await self._fetch_message(client, seqnum)
        if not msg_obj:
            return

        message = EmailMessage(
            subject=self._parse_message_subject(msg_obj),
            sender=EmailSender(
                name=self._parse_message_sender(msg_obj)[0],
                address=self._parse_message_sender(msg_obj)[1],
            ),
            content=self._parse_message_body(msg_obj),
        )

        for route in self.router.routes:
            logger.debug(
                "New message FROM={sender} Subject={subject}",
                sender=message.sender,
                subject=message.subject,
            )

            if route.match(message):
                logger.info(
                    "Processing new message FROM={sender} Subject={subject}",
                    sender=message.sender,
                    subject=message.subject,
                )

                async with self.container(
                    context={EmailMessage: message}, scope=Scope.REQUEST
                ) as request_scope:
                    injected_handler = wrap_injection(
                        func=route.handler,
                        container_getter=lambda args, kwargs: request_scope,
                        is_async=True,
                        remove_depends=True,
                    )
                    sig = inspect.signature(route.handler)
                    kwargs_to_pass = {}
                    for param_name, param in sig.parameters.items():
                        if param.annotation is EmailMessage:
                            kwargs_to_pass[param_name] = message
                    try:
                        await injected_handler(**kwargs_to_pass)
                        logger.info("Processed message {msg}", msg=message.model_dump())
                        await client.store(seqnum, "+FLAGS.SILENT", r"(\Seen)")
                    except Exception:
                        logger.exception(
                            "Handler {handler} failed", handler=route.handler.__name__
                        )

    async def _fetch_message(
        self: Self, client: aioimaplib.IMAP4_SSL, seqnum: str
    ) -> Message | None:
        status, data = await client.fetch(seqnum, "(BODY.PEEK[])")
        if status != "OK" or not data:
            return logger.error("Failed to fetch message {seqn}", seqn=seqnum)

        raw: bytes | None = None
        for item in data:
            if isinstance(item, (bytes, bytearray)) and len(item) > 100:
                raw = bytes(item)
                break

        if not raw:
            return logger.warning("Failed to get email body {seqn}", seqn=seqnum)

        return email.message_from_bytes(raw)

    def _parse_message_sender(self: Self, msg: Message) -> tuple[str, str]:
        raw = msg.get("From", "")
        name_raw, addr = parseaddr(raw)
        name = ""
        if name_raw:
            parts = decode_header(name_raw)
            decoded = []
            for part, enc in parts:
                if isinstance(part, bytes):
                    decoded.append(part.decode(enc or "utf-8", errors="replace"))
                else:
                    decoded.append(part)
            name = "".join(decoded)

        return name, addr

    def _parse_message_subject(self: Self, msg: Message) -> str:
        subject_raw = msg.get("Subject", "")
        subject = "".join(
            part.decode(enc or "utf-8", errors="replace")
            if isinstance(part, bytes)
            else part
            for part, enc in decode_header(subject_raw)
        )
        return subject

    def _parse_message_body(self: Self, msg: Message) -> str:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "utf-8"
                    body = payload.decode(charset, errors="replace")
                    break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                body = payload.decode(charset, errors="replace")

        return body
