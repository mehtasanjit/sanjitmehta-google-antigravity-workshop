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

"""Refuse a built-in that cannot work without ADK.

`eval dataset synthesize` and `eval optimize` drive the agent through ADK, so
they die on a missing `google.adk` import or a missing `adk` binary. Refusing
with the reason beats a traceback. The manifest points each command here by name.
"""

from __future__ import annotations

import sys

_REASONS = {
    "eval dataset": (
        "it runs the agent through ADK's user simulator, which needs google-adk "
        "in this project's venv."
    ),
    "eval optimize": "it shells out to the `adk` binary, which this project does not use.",
}


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "this command"
    reason = _REASONS.get(
        command, "it depends on ADK, which this project does not use."
    )
    print(
        f"agents-cli {command} is not supported by the langchain extension: {reason}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
