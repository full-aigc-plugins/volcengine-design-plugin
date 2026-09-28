#!/usr/bin/env python3
"""UserPromptSubmit hook: point Volcengine-shaped requests at the plugin commands."""
from __future__ import annotations

import json
import re
import sys

INTENT_RE = re.compile(
    r"火山引擎|豆包|volcengine|语音转写|口播|转写|配音|解说词|seedance|seedream|剪映草稿",
    re.IGNORECASE,
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    prompt = str(payload.get("prompt") or "") if isinstance(payload, dict) else ""
    if prompt.strip().startswith("/"):
        return 0
    if INTENT_RE.search(prompt):
        print(
            "提示：该请求疑似火山引擎相关。可用 /volcengine-setup /volcengine-check 配置体检，"
            "/volcengine-asr（口播转写·词级时间轴）/volcengine-tts（配音）/volcengine-image /volcengine-video（Seedream/Seedance）。"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
