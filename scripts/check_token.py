#!/usr/bin/env python3
"""토큰 검증기 — 이 토큰으로 메타 광고를 만들 수 있는지 확인한다.

setup.ps1 / setup.sh 가 설치 도중에 호출한다. 단독 실행도 된다.

사용:
  python check_token.py                    # env META_MCP_TOKEN 또는 .token 에서 찾음
  python check_token.py EAAxxxxx...        # 토큰을 직접 넘김

확인 항목:
  1) 유효한가 (is_valid)
  2) USER 토큰인가  ← 시스템 사용자 토큰은 MCP에서 401
  3) 필수 권한이 다 있는가
  4) 불필요하게 넓은 권한이 붙어 있지 않은가 (경고만)
  5) 데이터 접근 만료일이 언제인가

종료코드: 0 = 사용 가능 / 1 = 사용 불가
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://graph.facebook.com/v25.0"

# 라이브 절차(SKILL.md §5)에 실제로 필요한 권한
REQUIRED = ["ads_mcp_management", "ads_read", "ads_management", "pages_show_list"]
# 없으면 크리에이티브 생성에서 걸릴 수 있음 (경고)
RECOMMENDED = ["pages_manage_ads"]
# 광고 운영에 불필요 — 붙어 있으면 유출 시 피해 범위가 커진다
EXCESSIVE = {
    "leads_retrieval": "고객 개인정보(리드) 조회",
    "catalog_management": "상품 카탈로그·피드 수정",
    "business_management": "비즈니스 자산 수정",
    "pages_read_engagement": "페이지 게시물·댓글 데이터",
}


def resolve_token() -> str:
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()
    t = os.environ.get("META_MCP_TOKEN")
    if t:
        return t.strip()
    # config.py 의 탐색 순서를 그대로 재사용 (env → 폴더 안 .token 순)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import get_token
    return get_token()


def debug_token(token: str) -> dict:
    q = urllib.parse.urlencode({"input_token": token, "access_token": token})
    try:
        with urllib.request.urlopen(f"{API}/debug_token?{q}", timeout=60) as r:
            return json.loads(r.read()).get("data", {})
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read())["error"]["message"]
        except Exception:
            err = str(e)
        print(f"  [X] 토큰 조회 실패: {err}")
        sys.exit(1)
    except Exception as e:
        print(f"  [X] 네트워크 오류: {e}")
        sys.exit(1)


def main():
    token = resolve_token()
    print("  토큰 확인 중...  (%d자, %s...)" % (len(token), token[:8]))
    d = debug_token(token)
    scopes = set(d.get("scopes") or [])
    problems = []

    # 1) 유효성
    if not d.get("is_valid"):
        problems.append("토큰이 만료되었거나 무효합니다 (is_valid=false) → 재발급 필요")
    # 2) 종류
    ttype = d.get("type")
    if ttype != "USER":
        problems.append(f"USER 토큰이 아닙니다 (type={ttype}) → MCP가 401로 거부합니다")
    # 3) 필수 권한
    missing = [s for s in REQUIRED if s not in scopes]
    if missing:
        problems.append("필수 권한 누락: " + " ".join(missing))

    print("  종류      : %s" % (ttype or "?"))
    print("  유효       : %s" % ("O" if d.get("is_valid") else "X"))
    print("  권한       : %s" % (" ".join(sorted(scopes)) or "(없음)"))

    # 5) 만료일
    dae = d.get("data_access_expires_at")
    if dae:
        exp = datetime.datetime.fromtimestamp(dae)
        left = (exp - datetime.datetime.now()).days
        print("  데이터접근 : %s 까지 (%d일 남음)" % (exp.strftime("%Y-%m-%d"), left))
        if left < 0:
            problems.append("데이터 접근 기간이 이미 지났습니다 → 재발급 필요")
        elif left < 14:
            print("  [!] 만료가 임박했습니다. 미리 재발급하세요.")
    if d.get("expires_at") == 0:
        print("  토큰만료   : 없음 (무기한)")

    # 4) 과다 권한 (경고)
    extra = [s for s in EXCESSIVE if s in scopes]
    if extra:
        print("  [!] 광고 운영에 불필요한 권한이 붙어 있습니다:")
        for s in extra:
            print("      - %-22s %s" % (s, EXCESSIVE[s]))
        print("      유출 시 피해 범위가 커집니다. 최소권한으로 재발급을 권합니다.")
    for s in RECOMMENDED:
        if s not in scopes:
            print("  [!] %s 없음 — 크리에이티브 생성(SKILL.md §5-4)에서 막힐 수 있습니다." % s)

    if problems:
        print("\n  [X] 이 토큰은 사용할 수 없습니다:")
        for p in problems:
            print("      - " + p)
        print("\n  재발급: SKILL.md §1 참고")
        sys.exit(1)

    print("\n  [O] 사용 가능한 토큰입니다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
