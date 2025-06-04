#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import ops

logger = logging.getLogger(__name__)


class LanguageToolCharm(ops.CharmBase):


    def __init__(self, framework: ops.Framework) -> None:
        super().__init__(framework)
        self.pebble_service_name = "language-tool"
        framework.observe(self.on.language_tool_pebble_ready, self._on_language_tool_pebble_ready)


    def _on_language_tool_pebble_ready(self, event: ops.PebbleReadyEvent) -> None:
        container = event.workload
        container.add_layer("language_tool", self._pebble_layer, combine=True)
        container.replan()
        self.unit.status = ops.ActiveStatus()


    @property
    def _pebble_layer(self) -> ops.pebble.Layer:
        command = " ".join(
            [
                'java',
                '-cp',
                '/opt/LanguageTool-6.6/languagetool-server.jar',
                'org.languagetool.server.HTTPServer',
                '--port',
                '8081',
                '--config',
                '/opt/server.properties',
                '--allow-origin'
            ]
        )
        pebble_layer: ops.pebble.LayerDict = {
            "summary": "Language tool http server",
            "description": "pebble config layer for Language tool http server",
            "services": {
                self.pebble_service_name: {
                    "override": "replace",
                    "summary": "language tool http server",
                    "command": command,
                    "startup": "enabled",
                }
            },
        }
        return ops.pebble.Layer(pebble_layer)


if __name__ == "__main__":  # pragma: nocover
    ops.main(LanguageToolCharm)
