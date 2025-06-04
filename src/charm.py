#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from ops.model import ActiveStatus

import logging
import ops
import subprocess

# Log messages can be retrieved using juju debug-log
logger = logging.getLogger(__name__)


class LanguageToolCharm(ops.CharmBase):


    def __init__(self, framework: ops.Framework) -> None:
        super().__init__(framework)
        self.pebble_service_name = "fastapi-service"
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.start, self._on_start)


    def _on_install(self, event):
        # Install dependencies
        subprocess.check_call(['apt-get', 'update'])
        subprocess.check_call(['apt-get', 'install', '-y', 'openjdk-17-jre'])

        # Install build tools
        subprocess.check_call(['apt-get', 'install', '-y', 'unzip'])
        subprocess.check_call(['apt-get', 'install', '-y', 'wget'])
        subprocess.check_call(['apt-get', 'install', '-y', 'git'])
        subprocess.check_call(['apt-get', 'install', '-y', 'make'])
        subprocess.check_call(['apt-get', 'install', '-y', 'g++-10'])
        subprocess.check_call(['apt-get', 'install', '-y', 'build-essential'])

        # Download LanguageTool
        subprocess.check_call([
            'wget',
            'https://languagetool.org/download/LanguageTool-6.6.zip',
            '-O',
            '/opt/LanguageTool-6.6.zip'
        ])
        subprocess.check_call(['unzip', '/opt/LanguageTool-6.6.zip', '-d', '/opt/'])

        # Build and install fast text
        subprocess.check_call([
            'git',
            'clone',
            'https://github.com/facebookresearch/fastText.git',
            '/opt/fastTextGit'
        ])
        subprocess.check_call([
            'make',
            '-C',
            '/opt/fastTextGit'
        ])
        subprocess.check_call([
            'cp',
            '/opt/fastTextGit/fasttext',
            '/opt/fasttext'
        ])

        # Download fastText language model
        subprocess.check_call([
            'wget',
            'https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin',
            '-O',
            '/opt/lid.176.bin'
        ])

        # Create server properties file
        subprocess.check_call([
            'bash', '-c',
            'echo -e "fasttextModel=/opt/lid.176.bin\\nfasttextBinary=/opt/fasttext" > /opt/server.properties'
        ])


    def _on_start(self, event):
        # Start the LanguageTool HTTP server
        subprocess.Popen([
            'java',
            '-cp',
            '/opt/LanguageTool-6.6/languagetool-server.jar',
            'org.languagetool.server.HTTPServer',
            '--port',
            '8081',
            '--config',
            '/opt/server.properties',
            '--allow-origin'
        ])
        self.unit.status = ActiveStatus("LanguageTool HTTP server is running")


if __name__ == "__main__":  # pragma: nocover
    ops.main(LanguageToolCharm)
