.PHONY:lint-chat
lint-chat:
	uv run ruff check --fix ./apps/chat
	uv run mypy ./apps/chat

.PHONY:lint-common
lint-common:
	uv run ruff check --fix ./apps/common
	uv run mypy ./apps/common

.PHONY:lint-telegram_connector
lint-telegram_connector:
	uv run ruff check --fix ./apps/telegram_connector
	uv run mypy ./apps/telegram_connector

.PHONY:lint-email_connector
lint-email_connector:
	uv run ruff check --fix ./apps/email_connector
	uv run mypy ./apps/email_connector

.PHONY:lint
lint:
	uv run ruff check --fix ./apps
	uv run mypy ./apps


.PHONY:logs-email_connector
logs-email_connector:
	docker compose logs -f email_connector

.PHONY:logs-telegram_connector
logs-telegram_connector:
	docker compose logs -f telegram_connector

.PHONY:logs-chat
logs-chat:
	docker compose logs -f chat
