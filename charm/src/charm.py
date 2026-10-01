#!/usr/bin/env python3
"""Spring Boot Charm entrypoint."""

import logging
import typing

import ops

import paas_charm.springboot
from paas_charm.app import App

logger = logging.getLogger(__name__)

INFERENCE_RELATION = "inference-api"


class ChatClientCharm(paas_charm.springboot.Charm):
    """Spring Boot Charm service."""

    def __init__(self, *args: typing.Any) -> None:
        super().__init__(*args)
        self.framework.observe(
            self.on[INFERENCE_RELATION].relation_changed, self._on_inference_changed
        )
        self.framework.observe(
            self.on[INFERENCE_RELATION].relation_broken, self._on_inference_changed
        )

    def _on_inference_changed(self, _: ops.RelationEvent) -> None:
        # Rebuilds the Pebble layer (via _create_app) and replans.
        self.restart()

    def _inference_env(self) -> dict[str, str]:
        rel = self.model.get_relation(INFERENCE_RELATION)
        if rel is None or rel.app is None:
            return {}
        data = rel.data[rel.app]  # provider's application databag
        url, model = data.get("url"), data.get("model")
        if not (url and model):
            logger.info("inference-api related but url/model not published yet")
            return {}
        return {"INFERENCE_URL": url, "INFERENCE_MODEL": model}

    EXTRA_ENV = {
        "management.endpoints.web.exposure.include": "prometheus,health,metrics",
    }

    def _create_app(self) -> App:
        app = super()._create_app()
        base_gen = app.gen_environment
        extra = {**self.EXTRA_ENV, **self._inference_env()}
        app.gen_environment = lambda: {**base_gen(), **extra}  # type: ignore[method-assign]
        return app


if __name__ == "__main__":
    ops.main(ChatClientCharm)
