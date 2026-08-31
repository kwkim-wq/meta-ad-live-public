#!/usr/bin/env python3
"""전 구간 스모크 테스트 — 캠페인을 실제로 만들어보고 지운다.

목적: 새 토큰(최소권한)으로 SKILL.md §5 절차가 처음부터 끝까지 되는지 배포 전에 확인.

⛔ 돈은 나가지 않는다: 전부 PAUSED로만 만들고(activate 안 함) 마지막에 캠페인을 삭제한다.
   캠페인을 지우면 광고세트·광고까지 함께 사라진다.
   (테스트용 이미지 1장은 계정 이미지 라이브러리에 남는다 — 무해)

사용:
  python smoke_test.py                       # 기본 계정(config.json의 default_account_id)
  python smoke_test.py --account <광고계정ID>
  python smoke_test.py --keep                # 삭제하지 않고 남겨서 광고관리자에서 눈으로 확인
"""
import argparse
import binascii
import datetime
import json
import os
import struct
import sys
import urllib.error
import urllib.request
import zlib

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from config import cfg, cfg_optional                    # noqa: E402
from mcp import MCP_URL, get_token                      # noqa: E402
from upload_media import BASE_URL, upload_image         # noqa: E402

PAGE_ID = cfg("page_id")
PIXEL_ID = cfg_optional("pixel_id")
DEFAULT_ACCOUNT = cfg("default_account_id")
_display_link = cfg_optional("display_link")
LANDING = f"https://{_display_link}" if _display_link else "https://example.com"


# ---------------------------------------------------------------- 유틸
def make_png(path, w=600, h=600, rgb=(230, 230, 230)):
    """의존성 없이 단색 PNG를 만든다 (Pillow 불필요)."""
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", binascii.crc32(c) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 6))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return path


def call(tool, args, token):
    """MCP 도구 호출. 실패하면 RuntimeError — 정리(cleanup)를 위해 sys.exit 안 함."""
    args.setdefault("advertiser_request", "권한 스모크 테스트")
    body = {"jsonrpc": "2.0", "method": "tools/call", "id": 1,
            "params": {"name": tool, "arguments": args}}
    req = urllib.request.Request(
        MCP_URL, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream"})
    try:
        raw = urllib.request.urlopen(req, timeout=180).read().decode()
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:300]
        raise RuntimeError(f"HTTP {e.code} — {detail}")
    if raw.startswith("data: "):
        raw = raw[6:]
    d = json.loads(raw)
    if "error" in d:
        raise RuntimeError(json.dumps(d["error"], ensure_ascii=False)[:300])
    out = {}
    for c in d.get("result", {}).get("content", []):
        try:
            j = json.loads(c.get("text", ""))
        except Exception:
            continue
        if isinstance(j, dict):
            if j.get("error_message"):
                raise RuntimeError(str(j["error_message"])[:300])
            out.update(j)
    return out


def pick(d, *keys):
    """응답에서 id를 찾아낸다 (도구가 키 이름을 조금씩 다르게 준다)."""
    for k in keys:
        if d.get(k):
            return str(d[k])
    for v in d.values():                       # 중첩 dict 한 겹 탐색
        if isinstance(v, dict):
            for k in keys:
                if v.get(k):
                    return str(v[k])
    raise RuntimeError("응답에서 %s 를 못 찾음: %s" % ("/".join(keys),
                                                    json.dumps(d, ensure_ascii=False)[:300]))


# ---------------------------------------------------------------- 본체
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", default=DEFAULT_ACCOUNT)
    ap.add_argument("--keep", action="store_true", help="삭제하지 않고 남긴다")
    a = ap.parse_args()

    token = get_token()
    acct = a.account.replace("act_", "")
    ymd = datetime.datetime.now().strftime("%y%m%d")
    camp_name = f"{ymd}_판매_캠페인_권한테스트_테스트"
    ad_name = "테스트_이미지_권한테스트_일반_1"
    utm = (f"{LANDING}?utm_source=meta&utm_medium=cpc"
           f"&utm_campaign={camp_name}&utm_content={ad_name}")

    print(f"\n=== 스모크 테스트 — 계정 {acct} ===")
    print("전부 PAUSED로 만들고 마지막에 삭제합니다. 과금 없음.\n")

    steps, campaign_id, png = [], None, os.path.join(_HERE, "_smoke_test.png")

    def ok(name, detail=""):
        steps.append((name, True, detail))
        print(f"  [O] {name}  {detail}")

    def fail(name, err):
        steps.append((name, False, str(err)))
        print(f"  [X] {name}\n      {err}")

    try:
        # 1) 업로드 (Graph API)
        try:
            make_png(png)
            r = upload_image(png, "act_" + acct, token)
            if not r.get("ok"):
                raise RuntimeError(json.dumps(r.get("error"), ensure_ascii=False)[:300])
            image_hash = r["media_id"]
            ok("1. 소재 업로드 (Graph API)", f"hash={image_hash[:12]}...")
        except Exception as e:
            fail("1. 소재 업로드 (Graph API)", e)
            raise

        # 2) 캠페인
        try:
            r = call("ads_create_campaign", {
                "ad_account_id": acct,
                "campaign_name": camp_name,
                "objective": "OUTCOME_SALES",
                "buying_type": "AUCTION",
                "campaign_daily_budget": 10000000,     # 10만원 (cents)
                "special_ad_categories": "[]",
            }, token)
            campaign_id = pick(r, "campaign_id", "id")
            ok("2. 캠페인 생성", f"id={campaign_id}")
        except Exception as e:
            fail("2. 캠페인 생성", e)
            raise

        # 3) 광고세트
        try:
            ad_set_args = {
                "ad_account_id": acct,
                "campaign_id": campaign_id,
                "ad_set_name": f"{ymd}_어드밴티지_1865_남녀",
                "billing_event": "IMPRESSIONS",
                "targeting": json.dumps({
                    "geo_locations": {"countries": ["KR"]},
                    "age_min": 18, "age_max": 65,
                    "targeting_automation": {"advantage_audience": 1}}),
            }
            if PIXEL_ID:
                ad_set_args["optimization_goal"] = "OFFSITE_CONVERSIONS"
                ad_set_args["promoted_object"] = json.dumps({
                    "pixel_id": PIXEL_ID, "custom_event_type": "PURCHASE"})
            else:
                # 픽셀이 없는 회사는 전환 최적화 대신 링크 클릭으로 진행(promoted_object 생략)
                ad_set_args["optimization_goal"] = "LINK_CLICKS"
                print("  (i) pixel_id 설정 없음 — 전환 최적화 대신 LINK_CLICKS로 진행합니다.")
            r = call("ads_create_ad_set", ad_set_args, token)
            ad_set_id = pick(r, "ad_set_id", "adset_id", "id")
            ok("3. 광고세트 생성", f"id={ad_set_id}")
        except Exception as e:
            fail("3. 광고세트 생성", e)
            raise

        # 4) 크리에이티브 (페이지 연결 — pages_* 권한이 여기서 검증된다)
        try:
            r = call("ads_create_creative", {
                "ad_account_id": acct,
                "page_id": PAGE_ID,
                "image_hash": image_hash,
                "link_url": utm,
                "message": "권한 테스트용 본문입니다.",
                "headline": "권한 테스트",
                "call_to_action_type": "SHOP_NOW",
                "name": ad_name,
            }, token)
            creative_id = pick(r, "creative_id", "id")
            ok("4. 크리에이티브 생성", f"id={creative_id}")
        except Exception as e:
            fail("4. 크리에이티브 생성", e)
            raise

        # 5) 광고
        try:
            r = call("ads_create_ad", {
                "ad_account_id": acct,
                "ad_set_id": ad_set_id,
                "ad_name": ad_name,
                "creative": json.dumps({"creative_id": creative_id}),
            }, token)
            ad_id = pick(r, "ad_id", "id")
            ok("5. 광고 생성", f"id={ad_id}")
        except Exception as e:
            fail("5. 광고 생성", e)
            raise

        # 6) 미리보기
        try:
            r = call("ads_get_ad_preview", {"ad_id": ad_id}, token)
            ok("6. 미리보기", str(r.get("preview_url", ""))[:60] + "...")
        except Exception as e:
            fail("6. 미리보기", e)

        # 7) 성과 조회 (ads_read 검증)
        try:
            call("ads_get_ad_entities", {
                "ad_account_id": acct, "level": "campaign",
                "fields": ["name", "amount_spent"], "date_preset": "last_7d", "limit": 3}, token)
            ok("7. 성과 조회 (ads_read)")
        except Exception as e:
            fail("7. 성과 조회 (ads_read)", e)

    except Exception:
        pass       # 실패 지점은 이미 기록됨 — 아래 정리로 넘어간다
    finally:
        if os.path.exists(png):
            os.remove(png)
        if campaign_id and not a.keep:
            try:
                u = f"{BASE_URL}/{campaign_id}?access_token={token}"
                req = urllib.request.Request(u, method="DELETE")
                urllib.request.urlopen(req, timeout=60).read()
                ok("8. 정리 — 캠페인 삭제", f"id={campaign_id} (하위 전부 삭제)")
            except Exception as e:
                fail("8. 정리 — 캠페인 삭제", e)
                print(f"\n  ⛔ 수동 삭제 필요: 캠페인 {campaign_id}")
        elif campaign_id:
            print(f"\n  --keep 지정 — 캠페인 {campaign_id} 남겨둠 (PAUSED, 과금 없음). 확인 후 직접 삭제하세요.")

    bad = [s for s in steps if not s[1]]
    print("\n" + "=" * 52)
    if bad:
        print("결과: 실패 %d개 — 권한이 부족하거나 절차가 깨졌습니다." % len(bad))
        for n, _, e in bad:
            print(f"  - {n}: {e[:160]}")
        print("\n힌트: 4번(크리에이티브)에서 막히면 pages_manage_ads,")
        print("      2·3번에서 막히면 ads_management / business_management 를 붙여 재발급.")
        sys.exit(1)
    print("결과: 전 구간 통과 — 이 토큰으로 배포해도 됩니다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
