from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def use_middlewares(app: FastAPI, allow_origins: list[str]) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
