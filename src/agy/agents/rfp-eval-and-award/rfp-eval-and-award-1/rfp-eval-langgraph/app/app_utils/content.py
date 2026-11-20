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

"""Normalize LangChain message content to plain text for A2A text parts."""

from __future__ import annotations


def content_to_text(content: object) -> str:
    """Return a message's ``content`` as plain text.

    LangChain 1.x messages carry ``content`` either as a string or as a list of
    content blocks (e.g. ``[{"type": "text", "text": "hi"}]``). An A2A text ``Part``
    requires a string, so flatten the block form here.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out: list[str] = []
        for block in content:
            if isinstance(block, dict):
                out.append(str(block.get("text", "")))
            elif isinstance(block, str):
                out.append(block)
        return "".join(out)
    return ""
