#!/usr/bin/env python3
"""세팅 마법사 — 토큰만 있으면 광고계정·페이지·픽셀·인스타를 자동으로 찾아 config.json을 만든다.

Claude가 실행하는 것을 전제로 대화형 입력을 쓰지 않는다. 3단계로 나뉜다.

  1) python setup_wizard.py check                 토큰이 쓸 수 있는지 확인
  2) python setup_wizard.py discover              계정·페이지·픽셀·인스타 목록을 JSON으로 출력
  3) python setup_wizard.py write --account 123 --page 456 [--pixel 789] [--ig 111]
                                                  고른 값으로 config.json 생성

  python setup_wizard.py verify                   만들어진 설정이 실제로 동작하는지 확인

Claude 사용법:
  discover 결과를 사람에게 보여주고 어느 계정·페이지를 쓸지 물어본 뒤 write 를 실행한다.
  후보가 하나뿐이면 물어보지 말고 그대로 쓴다.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from config import (BASE_URL, CONFIG_PATH, TOKEN_PATHS, currency_multiplier,  # noqa: E402
                    get_token)

TIMEOUT = 60


def api(path, params=None, token=None):
    p = dict(params or {})
    p["access_token"] = token
    url = f"{BASE_URL}/{path}?" + urllib.parse.urlencode(p)
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read())
        except Exception:
            return {"error": {"message": str(e)}}
    except Exception as e:
        return {"error": {"message": str(e)}}


# ─────────────────────────── 1) check ───────────────────────────
NEEDED = ["ads_management"]          # 이게 없으면 광고를 못 만든다
NICE = ["ads_read", "ads_mcp_management", "pages_show_list", "pages_manage_ads"]


def probe_mcp(token):
    """MCP 서버가 실제로 응답하는지 확인. (권한만 봐서는 알 수 없다 —
    앱에 '광고 MCP 서버' 이용 사례가 없으면 권한이 있어도 401이 난다)"""
    body = json.dumps({"jsonrpc": "2.0", "method": "tools/list", "id": 1}).encode()
    req = urllib.request.Request(
        MCP_URL, data=body,
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read().decode()
        if raw.startswith("data: "):
            raw = raw[6:]
        n = len(json.loads(raw).get("result", {}).get("tools", []))
        return True, f"도구 {n}개 사용 가능"
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return False, "401 — 앱에 '광고 MCP 서버' 이용 사례가 없거나 ads_mcp_management 권한 없음"
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)[:80]


def probe_graph(token):
    """Graph API로 광고계정이 보이는지 확인."""
    r = api("me/adaccounts", {"fields": "id", "limit": 1}, token)
    if "error" in r:
        return False, r["error"].get("message", "")[:90]
    return True, f"광고계정 {len(r.get('data', []))}개 이상 조회됨"


def cmd_check(token, quiet=False):
    d = api("debug_token", {"input_token": token}, token).get("data", {})
    if not d:
        print("[X] 토큰을 확인할 수 없습니다. 값이 잘못됐거나 만료됐습니다.")
        return 1

    scopes = d.get("scopes", [])
    typ = d.get("type")

    print(f"  종류   : {typ}")
    print(f"  유효   : {'O' if d.get('is_valid') else 'X'}")
    exp = d.get("data_access_expires_at")
    if exp:
        import datetime
        left = (datetime.datetime.fromtimestamp(exp) - datetime.datetime.now()).days
        print(f"  만료   : {datetime.datetime.fromtimestamp(exp):%Y-%m-%d} ({left}일 남음)")

    # ── 두 경로를 실제로 찔러본다 ──
    graph_ok, graph_msg = probe_graph(token)
    mcp_ok, mcp_msg = probe_mcp(token)

    print("\n  [경로 확인]")
    print(f"   Graph API : {'O' if graph_ok else 'X'}  {graph_msg}")
    print(f"   MCP 서버  : {'O' if mcp_ok else 'X'}  {mcp_msg}")

    if not graph_ok:
        print("\n[X] Graph API 가 막혀 있으면 아무것도 할 수 없습니다.")
        print("    - 토큰에 ads_management 권한이 있는지")
        print("    - 그 페이스북 계정에 광고계정 접근 권한이 있는지 확인하세요.")
        return 1

    missing = [s for s in NEEDED if s not in scopes]
    if missing:
        print(f"\n[X] 광고 생성에 꼭 필요한 권한이 없습니다: {' '.join(missing)}")
        print("    Graph API Explorer에서 아래를 넣어 다시 발급하세요:")
        print(f"    {' '.join(NEEDED + NICE)}")
        return 1

    if typ != "USER" and not mcp_ok:
        print(f"\n[!] 이 토큰은 {typ} 입니다. MCP 서버는 USER 토큰만 받습니다.")

    if not mcp_ok:
        print("\n[!] MCP 서버를 쓸 수 없습니다 — 하지만 광고 제작은 가능합니다.")
        print("    못 하는 것 : 광고 미리보기, MCP 경유 성과조회")
        print("    되는 것   : 소재 업로드 · 캠페인 · 광고세트 · 크리에이티브 · 광고 생성 · 라이브")
        print("               (전부 Graph API 경로로 처리됩니다)")
        print("    풀려면    : 개발자 앱 → 이용 사례에 '광고 MCP 서버로 광고 만들기 및 관리하기' 추가")
        print("               후 ads_mcp_management 권한을 넣어 토큰 재발급")

    lack = [s for s in NICE if s not in scopes and s != "ads_mcp_management"]
    if lack:
        print(f"\n[!] 없어도 되지만 있으면 편한 권한: {' '.join(lack)}")
        if "pages_show_list" in lack:
            print("    (pages_show_list 가 없으면 페이지 목록 자동조회가 안 돼 직접 입력해야 합니다)")
        if "ads_read" in lack:
            print("    (ads_read 가 없으면 성과 조회가 안 됩니다)")

    print("\n[O] 사용 가능한 토큰입니다." + ("" if mcp_ok else "  (MCP 없이 Graph API 경로로 동작)"))
    return 0


# ─────────────────────────── 2) discover ───────────────────────────
def cmd_discover(token, as_json=False):
    out = {"ad_accounts": [], "pages": [], "instagram": [], "pixels": []}

    # 광고계정
    r = api("me/adaccounts",
            {"fields": "id,account_id,name,currency,account_status", "limit": 100}, token)
    if "error" in r:
        print("[X] 광고계정 조회 실패:", r["error"].get("message"))
        return 1
    for a in r.get("data", []):
        out["ad_accounts"].append({
            "id": a.get("account_id") or str(a.get("id", "")).replace("act_", ""),
            "label": a.get("name", ""),
            "currency": a.get("currency", ""),
            "active": a.get("account_status") == 1,
        })

    # 페이지
    r = api("me/accounts", {"fields": "id,name", "limit": 100}, token)
    for p in r.get("data", []):
        out["pages"].append({"id": p.get("id"), "label": p.get("name", "")})

    # 인스타그램 (페이지에 연결된 것)
    for p in out["pages"]:
        r = api(p["id"], {"fields": "instagram_business_account{id,username}"}, token)
        iba = r.get("instagram_business_account")
        if iba and iba.get("id"):
            out["instagram"].append({
                "id": iba["id"],
                "label": iba.get("username", ""),
                "page_id": p["id"],
            })

    # 픽셀 (계정별)
    for a in out["ad_accounts"]:
        r = api(f"act_{a['id']}/adspixels", {"fields": "id,name", "limit": 25}, token)
        for px in r.get("data", []):
            out["pixels"].append({
                "id": px.get("id"), "label": px.get("name", ""), "account_id": a["id"],
            })

    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    def show(title, rows, extra=None):
        print(f"\n[{title}] {len(rows)}개")
        if not rows:
            print("   (없음)")
        for x in rows:
            tail = f"  {extra(x)}" if extra else ""
            print(f"   {x['id']}  {x.get('label','')}{tail}")

    show("광고계정", out["ad_accounts"],
         lambda x: f"({x['currency']}){'' if x['active'] else ' *비활성'}")
    show("페이지", out["pages"])
    show("인스타그램", out["instagram"])
    show("픽셀", out["pixels"])

    print("\n다음 단계:")
    print("  python setup_wizard.py write --account <광고계정ID> --page <페이지ID> "
          "[--pixel <픽셀ID>] [--ig <인스타ID>]")
    return 0


# ─────────────────────────── 3) write ───────────────────────────
def cmd_write(token, a):
    disc = {}
    r = api("me/adaccounts", {"fields": "id,account_id,name,currency", "limit": 100}, token)
    accounts = []
    for x in r.get("data", []):
        accounts.append({
            "id": x.get("account_id") or str(x.get("id", "")).replace("act_", ""),
            "label": x.get("name", ""),
            "currency": x.get("currency", ""),
        })
    chosen = next((x for x in accounts if x["id"] == a.account), None)
    if not chosen:
        print(f"[X] 광고계정 {a.account} 을 찾을 수 없습니다. discover 로 목록을 확인하세요.")
        return 1

    page_label = ""
    r = api(a.page, {"fields": "name"}, token)
    if "error" not in r:
        page_label = r.get("name", "")

    conf = {
        "company": a.company or "",
        "ad_accounts": accounts,
        "default_account_id": chosen["id"],
        "currency": chosen["currency"],
        "budget_multiplier": currency_multiplier(chosen["currency"]),
        "page_id": a.page,
        "page_label": page_label,
        "instagram_user_id": a.ig or None,
        "pixel_id": a.pixel or None,
        "display_link": a.display_link or "",
        "default_daily_budget": a.budget,
        "default_cta": a.cta,
        "default_age_min": 18,
        "default_age_max": 65,
        "country": a.country,
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(conf, f, ensure_ascii=False, indent=2)
    print(f"[O] config.json 생성 완료 → {CONFIG_PATH}\n")
    print(json.dumps(conf, ensure_ascii=False, indent=2))
    if not conf["pixel_id"]:
        print("\n[!] 픽셀이 비어 있습니다. 전환(구매) 최적화 광고를 만들려면 픽셀이 필요합니다.")
    if not conf["instagram_user_id"]:
        print("[!] 인스타그램 계정이 비어 있습니다. 없으면 인스타 지면 노출이 제한될 수 있습니다.")
    return 0


# ─────────────────────────── verify ───────────────────────────
def cmd_verify(token):
    from config import cfg, cfg_optional
    ok = True
    acct = cfg("default_account_id")

    r = api(f"act_{acct}", {"fields": "name,currency,account_status"}, token)
    if "error" in r:
        print("[X] 광고계정 접근 불가:", r["error"].get("message"))
        ok = False
    else:
        print(f"[O] 광고계정 : {r.get('name')} ({r.get('currency')})")

    r = api(cfg("page_id"), {"fields": "name"}, token)
    if "error" in r:
        print("[X] 페이지 접근 불가:", r["error"].get("message"))
        ok = False
    else:
        print(f"[O] 페이지   : {r.get('name')}")

    px = cfg_optional("pixel_id")
    if px:
        r = api(px, {"fields": "name"}, token)
        print(f"[{'O' if 'error' not in r else 'X'}] 픽셀     : {r.get('name', r.get('error', {}).get('message'))}")

    ig = cfg_optional("instagram_user_id")
    if ig:
        r = api(ig, {"fields": "username"}, token)
        print(f"[{'O' if 'error' not in r else 'X'}] 인스타   : {r.get('username', r.get('error', {}).get('message'))}")

    print("\n" + ("[O] 세팅이 정상입니다." if ok else "[X] 위 항목을 고쳐야 합니다."))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="메타 광고 도구 세팅")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("check", help="토큰 확인")
    d = sub.add_parser("discover", help="계정·페이지·픽셀·인스타 목록 조회")
    d.add_argument("--json", action="store_true", help="JSON으로 출력")

    w = sub.add_parser("write", help="config.json 생성")
    w.add_argument("--account", required=True, help="광고계정 ID (act_ 없이 숫자만)")
    w.add_argument("--page", required=True, help="페이스북 페이지 ID")
    w.add_argument("--pixel", help="픽셀 ID (전환 광고에 필요)")
    w.add_argument("--ig", help="인스타그램 비즈니스 계정 ID")
    w.add_argument("--company", help="회사/브랜드 이름 (표시용)")
    w.add_argument("--display-link", help="광고에 표시할 도메인 (예: example.com)")
    w.add_argument("--budget", type=int, default=100000, help="기본 일예산 (기본 100000)")
    w.add_argument("--cta", default="SHOP_NOW", help="기본 행동유도 버튼 (기본 SHOP_NOW)")
    w.add_argument("--country", default="KR", help="타겟 국가코드 (기본 KR)")

    sub.add_parser("verify", help="세팅 동작 확인")

    a = ap.parse_args()
    if not a.cmd:
        ap.print_help()
        return 1

    token = get_token()
    if a.cmd == "check":
        return cmd_check(token)
    if a.cmd == "discover":
        return cmd_discover(token, a.json)
    if a.cmd == "write":
        return cmd_write(token, a)
    if a.cmd == "verify":
        return cmd_verify(token)
    return 1


if __name__ == "__main__":
    sys.exit(main())
