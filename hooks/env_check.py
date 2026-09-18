#!/usr/bin/env python3
"""SessionStart hook: report the two Volcengine credential families. Advisory only."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from volcengine_config import get_setting  # noqa: E402


def main() -> int:
    lines = []
    ark, _ = get_setting("ARK_API_KEY")
    app_id, _ = get_setting("VOLCENGINE_APP_ID")
    token, _ = get_setting("VOLCENGINE_ACCESS_TOKEN")
    lines.append("方舟(生图/生视频/对话): ARK_API_KEY ✓" if ark else "方舟: ARK_API_KEY 未设——生图生视频不可用")
    lines.append("豆包语音(ASR/TTS): APP_ID+TOKEN ✓" if app_id and token else "豆包语音: 凭据未设——ASR/TTS 不可用")
    lines.append("计费提醒: ASR≈0.8元/小时档；Seedream 按张、Seedance 按秒")
    try:
        sys.stdin.read()
    except Exception:
        pass
    print("火山引擎插件环境：" + "；".join(lines))
    return 0


if __name__ == "__main__":
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    sys.exit(main())
