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
        container.replan()
        self.unit.status = ops.ActiveStatus()


if __name__ == "__main__":  # pragma: nocover
    ops.main(LanguageToolCharm)
