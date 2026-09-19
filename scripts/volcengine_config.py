"""Shared credentials/config for the Volcengine deterministic clients.

Two credential families live side by side:
- ARK (方舟 v3: chat / images / video tasks) — single API key.
- Speech (豆包 ASR / TTS, openspeech.bytedance.com) — app_id + access_token.

Resolution order for every setting: CLI flag > environment > config file
(~/.volcengine-design/config.json, {"VOLCENGINE_ARK_API_KEY": ..., ...}).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

CONFIG_FILE = Path.home() / ".volcengine-design" / "config.json"

ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
SPEECH_BASE_URL = "https://openspeech.bytedance.com"


def _config_file() -> Path:
    return CONFIG_FILE


def _parse_env_file(path: Path) -> dict:
    out: dict = {}
    if not path.is_file():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    return out


def _user_credentials() -> dict:
    data: dict = {}
    env_file = Path(os.environ.get("VOLCENGINE_ENV_FILE", "")) if os.environ.get("VOLCENGINE_ENV_FILE") else Path.cwd() / ".env"
    data.update(_parse_env_file(env_file))
    config_file = _config_file()
    if config_file.is_file():
        try:
            stat_result = config_file.stat()
            if os.name == "posix":
                if stat_result.st_uid != os.geteuid():
                    raise RuntimeError(f"凭据文件所有者不安全：{config_file}；请改为当前用户所有")
                if stat_result.st_mode & 0o077:
                    raise RuntimeError(f"凭据文件权限过宽：{config_file}；请执行 chmod 600 {config_file}")
            parsed = json.loads(config_file.read_text(encoding="utf-8"))
            if not isinstance(parsed, dict):
                raise RuntimeError(f"凭据文件必须是 JSON 对象：{config_file}")
            data.update(parsed)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"凭据文件 JSON 无效：{config_file}（{exc.msg}）") from exc
        except OSError as exc:
            raise RuntimeError(f"无法读取凭据文件：{config_file}（{exc}）") from exc
    return data


def get_setting(name: str) -> tuple[str | None, str]:
    """Return (value, source) for one credential setting."""
    for source, pool in (("flag-env", os.environ), ("config", _user_credentials())):
        value = pool.get(name)
        if value:
            return value, source
    return None, "missing"


def fail_missing(message: str) -> "NoReturn":  # type: ignore[name-defined]
    print(message, file=sys.stderr)
    sys.exit(2)


def ark_api_key() -> str:
    key, source = get_setting("ARK_API_KEY")
    if not key:
        fail_missing(
            "缺 ARK_API_KEY（方舟 v3：chat/images/video）。获取: "
            "https://console.volcengine.com/ark → API Key 管理；"
            "环境变量、.env 或 ~/.volcengine-design/config.json 均可。"
        )
    return key


def speech_credentials() -> tuple[str, str]:
    app_id, s1 = get_setting("VOLCENGINE_APP_ID")
    token, s2 = get_setting("VOLCENGINE_ACCESS_TOKEN")
    if not app_id or not token:
        fail_missing(
            "缺语音凭据（豆包 ASR/TTS）。需要 VOLCENGINE_APP_ID 与 VOLCENGINE_ACCESS_TOKEN——"
            "获取: https://console.volcengine.com/speech/app （语音技术应用 AppID + Access Token）；"
            "环境变量、.env 或 ~/.volcengine-design/config.json 均可。"
        )
    return app_id, token  # type: ignore[return-value]


def ark_headers(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def ark_base_url() -> str:
    base, _ = get_setting("ARK_BASE_URL")
    return (base or ARK_BASE_URL).rstrip("/")
