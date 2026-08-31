#!/usr/bin/env python3
"""설정 로더 — 회사별 값(광고계정·페이지·픽셀·통화)을 config.json에서 읽는다.

이 파일은 수정할 필요가 없다. 값은 전부 폴더 안 `config.json`에 있고,
`python setup_wizard.py`가 API로 조회해서 자동으로 만들어 준다.

다른 스크립트에서 쓰는 법:
    from config import cfg, get_token
    acct = cfg("default_account_id")
    page = cfg("page_id")
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))       # .../scripts
_ROOT = os.path.dirname(_HERE)                           # .../meta-ad-live

CONFIG_PATH = os.path.join(_ROOT, "config.json")
TOKEN_PATHS = [
    os.path.join(_ROOT, ".token"),
    os.path.join(_HERE, ".token"),
    os.path.expanduser("~/.claude/skills/meta-ad-live/.token"),
    os.path.expanduser("~/.meta-ad-live-token"),
]

API_VERSION = "v23.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
MCP_URL = "https://mcp.facebook.com/ads"

# 통화별 최소단위 배율. Meta는 "최소 화폐 단위"로 예산을 받는다.
#   KRW·JPY = 소수점 없음 → 100,000원이면 그대로 100000
#   USD·EUR = 센트 단위   → $100 이면 10000
# ⛔ 이걸 틀리면 예산이 100배/100분의 1로 잡힌다. setup_wizard가 계정 통화를 읽어 자동 저장한다.
ZERO_DECIMAL = {"KRW", "JPY", "VND", "CLP", "ISK", "UGX", "PYG", "RWF", "XOF", "XAF", "KMF", "DJF", "GNF", "MGA", "VUV"}


def currency_multiplier(currency: str) -> int:
    """예산 입력 배율. KRW → 1, USD → 100."""
    return 1 if (currency or "").upper() in ZERO_DECIMAL else 100


def load() -> dict:
    if not os.path.exists(CONFIG_PATH):
        sys.exit(
            "config.json 이 없습니다.\n"
            "  먼저 세팅을 실행하세요:  python setup_wizard.py\n"
            "  (토큰만 있으면 광고계정·페이지·픽셀을 자동으로 찾아 만들어 줍니다)"
        )
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        sys.exit(f"config.json 형식이 깨졌습니다: {e}\n  다시 만들려면: python setup_wizard.py")


_cache = None


def cfg(key=None, default=None):
    """설정값 하나 읽기. key 없이 부르면 전체 dict."""
    global _cache
    if _cache is None:
        _cache = load()
    if key is None:
        return _cache
    val = _cache.get(key, default)
    if val is None and default is None:
        sys.exit(f"config.json 에 '{key}' 값이 없습니다.  python setup_wizard.py 로 다시 세팅하세요.")
    return val


def cfg_optional(key, default=None):
    """없어도 되는 값 (예: instagram_user_id)."""
    global _cache
    if _cache is None:
        _cache = load()
    return _cache.get(key, default)


def get_token() -> str:
    """액세스 토큰. 환경변수 > 폴더 안 .token 순."""
    t = os.environ.get("META_ADS_TOKEN") or os.environ.get("META_MCP_TOKEN")
    if t:
        return t.strip()
    for p in TOKEN_PATHS:
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                v = f.read().strip()
            if v:
                return v
    sys.exit(
        "액세스 토큰을 찾을 수 없습니다.\n"
        "  1) Graph API Explorer에서 사용자 토큰을 발급받고\n"
        f"  2) 이 파일에 저장하세요:  {os.path.join(_ROOT, '.token')}\n"
        "  자세한 방법은 SETUP.md 를 보거나, Claude에게 'SETUP.md 보고 세팅해줘'라고 하세요."
    )


def account_label(account_id: str) -> str:
    """계정 ID → 사람이 읽는 이름."""
    for a in cfg_optional("ad_accounts", []) or []:
        if str(a.get("id")) == str(account_id):
            return a.get("label") or account_id
    return account_id
