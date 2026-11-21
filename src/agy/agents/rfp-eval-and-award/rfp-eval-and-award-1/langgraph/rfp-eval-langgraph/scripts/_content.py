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


"""Message-content normalization shared by the override scripts."""

from __future__ import annotations


def content_to_text(content: object) -> str:
    """Flatten LangChain 1.x list content blocks to plain text.

    A chat model returns `content` either as a string or as a list of blocks
    (`[{"type": "text", "text": "hi"}]`). Printing or writing the list form
    leaks `{'type': ..., 'extras': ...}` noise into `run` output and makes
    `eval grade` reject the trace, so both callers flatten first. The template
    keeps its own copy in `app/app_utils/content.py` for the A2A path, which
    runs inside the user's project rather than here.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            str(block.get("text", "")) if isinstance(block, dict) else block
            for block in content
            if isinstance(block, (dict, str))
        ]
        return "".join(parts)
    return ""
