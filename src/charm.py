#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import ops

# Log messages can be retrieved using juju debug-log
logger = logging.getLogger(__name__)


class LanguageToolCharm(ops.CharmBase):


    def __init__(self, framework: ops.Framework) -> None:
        super().__init__(framework)
        self.pebble_service_name = "language-tool"
        framework.observe(self.on.language_tool_pebble_ready, self._on_language_tool_pebble_ready)

    def _on_language_tool_pebble_ready(self, event: ops.PebbleReadyEvent) -> None:
        """Define and start a workload using the Pebble API.

        Change this example to suit your needs. You'll need to specify the right entrypoint and
        environment configuration for your specific workload.

        Learn more about interacting with Pebble at https://juju.is/docs/sdk/pebble
        Learn more about Pebble layers at
            https://canonical-pebble.readthedocs-hosted.com/en/latest/reference/layers/
        """
        # Get a reference the container attribute on the PebbleReadyEvent
        container = event.workload
        # Add initial Pebble config layer using the Pebble API
        container.add_layer("language_tool", self._pebble_layer, combine=True)
        # Make Pebble reevaluate its plan, ensuring any services are started if enabled.
        container.replan()
        # Learn more about statuses in the SDK docs:
        # https://juju.is/docs/sdk/constructs#heading--statuses
        self.unit.status = ops.ActiveStatus()


    @property
    def _pebble_layer(self) -> ops.pebble.Layer:
        # Start the LanguageTool HTTP server
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
