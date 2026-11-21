# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Register with Gemini, except where the contract needs ADK.

On Agent Runtime the built-in registers the agent for native `:streamQuery`,
which only an ADK app serves. Everywhere else it registers over A2A, which this
project does serve, so the built-in is fine and runs unchanged.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

import yaml


def _deployment_target() -> str:
    manifest = pathlib.Path("agents-cli-manifest.yaml")
    if not manifest.exists():
        return ""
    data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    return str(data.get("create_params", {}).get("deployment_target", ""))


def main() -> int:
    if _deployment_target() == "agent_runtime":
        print(
            "Publishing to Gemini is not supported by the langchain extension on "
            "Agent Runtime: registration there invokes the agent with "
            "ADK's :streamQuery contract, which this project does not serve. Deploy "
            "to cloud_run or gke and publish from there, where registration is A2A.",
            file=sys.stderr,
        )
        return 2

    env = {**os.environ, "AGENTS_CLI_DISABLE_OVERRIDES": "1"}
    # The pre-rename name, which every agents-cli version accepts.
    return subprocess.run(
        ["agents-cli", "publish", "gemini-enterprise", *sys.argv[1:]], env=env
    ).returncode


if __name__ == "__main__":
    sys.exit(main())
