#!/usr/bin/env python3
"""메타 광고 MCP 호출기 — 로컬에서 바로 실행 (SSH 불필요).

서버: https://mcp.facebook.com/ads (Meta 호스팅)
인증: 사용자(USER) 액세스 토큰 Bearer. ⛔ 시스템 사용자 토큰은 401로 거부된다.

사용:
  python3 mcp.py tools                                  # 도구 82개 이름
  python3 mcp.py schema ads_create_campaign             # 특정 도구 인자 스펙
  python3 mcp.py call ads_get_ad_accounts '{}'          # 호출
  python3 mcp.py call ads_get_ad_entities '{"ad_account_id":"<광고계정ID>","level":"account","fields":["amount_spent"],"date_preset":"last_7d"}'
  echo '{"...":"..."}' | python3 mcp.py call ads_create_campaign -    # 인자를 stdin으로

토큰 우선순위: config.py get_token() 참고 (env META_ADS_TOKEN/META_MCP_TOKEN → 폴더 안 .token 순)
"""
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import MCP_URL, get_token


def rpc(method: str, params=None, timeout=180):
    body = {"jsonrpc": "2.0", "method": method, "id": 1}
    if params is not None:
        body["params"] = params
    req = urllib.request.Request(
        MCP_URL, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + get_token(),
                 "Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream"})
    try:
        raw = urllib.request.urlopen(req, timeout=timeout).read().decode()
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:500]
        if e.code == 401:
            sys.exit(f"401 인증 실패 — 토큰이 만료됐거나 USER 토큰이 아닙니다.\n{detail}")
        sys.exit(f"HTTP {e.code}: {detail}")
    if raw.startswith("data: "):          # SSE 형식으로 올 때가 있다
        raw = raw[6:]
    d = json.loads(raw)
    if "error" in d:
        sys.exit("RPC 에러: " + json.dumps(d["error"], ensure_ascii=False)[:600])
    return d.get("result", {})


def print_content(result):
    """도구 응답 본문 출력. JSON이면 예쁘게, 아니면 그대로."""
    for c in result.get("content", []):
        t = c.get("text", "")
        try:
            j = json.loads(t)
        except Exception:
            print(t)
            continue
        # ad_entities가 문자열로 중첩돼 오는 경우 풀어준다
        if isinstance(j, dict) and isinstance(j.get("ad_entities"), str):
            try:
                j["ad_entities"] = json.loads(j["ad_entities"])
            except Exception:
                pass
        if isinstance(j, dict) and j.get("error_message"):
            print("⚠ 도구 검증 에러:", j["error_message"][:700])
            continue
        print(json.dumps(j, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]

    if cmd == "tools":
        for t in rpc("tools/list").get("tools", []):
            print(t["name"])
        return

    if cmd == "schema":
        if len(sys.argv) < 3:
            sys.exit("사용: mcp.py schema <도구명>")
        name = sys.argv[2]
        for t in rpc("tools/list").get("tools", []):
            if t["name"] == name:
                sch = t.get("inputSchema", {})
                req = set(sch.get("required", []))
                print("=== %s ===" % name)
                print((t.get("description") or "")[:900])
                print("\n--- 인자 ---")
                for k, v in sch.get("properties", {}).items():
                    mark = "*" if k in req else " "
                    print(" %s %-28s %s" % (mark, k, str(v.get("description", ""))[:100]))
                print("\n(* = 필수)")
                return
        sys.exit("그런 도구 없음: " + name)

    if cmd == "call":
        if len(sys.argv) < 3:
            sys.exit("사용: mcp.py call <도구명> '<JSON인자>'   (인자 자리에 - 주면 stdin)")
        name = sys.argv[2]
        arg_raw = sys.argv[3] if len(sys.argv) > 3 else "{}"
        if arg_raw == "-":
            arg_raw = sys.stdin.read()
        try:
            args = json.loads(arg_raw or "{}")
        except json.JSONDecodeError as e:
            sys.exit(f"인자 JSON 파싱 실패: {e}\n받은 값: {arg_raw[:200]}")
        args.setdefault("advertiser_request", "Claude Code 세션에서 호출")
        print_content(rpc("tools/call", {"name": name, "arguments": args}))
        return

    sys.exit(__doc__)


if __name__ == "__main__":
    main()
