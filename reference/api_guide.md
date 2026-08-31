# 메타 광고 API·MCP 참고서

> 이 파일은 **참고용**이다. 실제 실행 절차(승인 흐름·자동화 규칙 등)는 `SKILL.md`를 본다.

메타 광고 성과·소재를 다루는 두 가지 경로 — Graph Marketing API와 Meta 호스팅 MCP 서버 —
를 실측 기준으로 정리한다. 여기 적힌 필드명·파싱 방법·함정은 전부 실제 호출로 확인한 것이다.
추측으로 채운 항목은 "코드상/실측 확인 안 됨"이라고 표시한다.

---

## 0. 두 가지 경로 — 언제 뭘 쓰나

| | Graph API | MCP (`mcp.facebook.com/ads`) |
|---|---|---|
| 성과 조회 | 가능 | 가능 (도구 하나로 전 레벨) |
| 소재(영상) 업로드 | **가능** | ⛔ 업로드 도구 없음 |
| 다중 문구·제목(asset_feed_spec) | **가능** | ⛔ `message`/`headline` 단일값만 |
| 생성(캠페인/세트/광고) | 가능 | 가능(전부 PAUSED로 생성됨) |
| 광고 미리보기 | 별도 구현 필요 | **가능** (`ads_get_ad_preview`) |
| A/B 테스트·컨버전 리프트 | 별도 구현 필요 | **가능** |
| 경쟁사 광고 검색(Ad Library) | 별도 구현 필요 | **가능** |
| 인증 토큰 종류 | 시스템 사용자 토큰 가능 | **사람(USER) 토큰만** — 시스템 사용자 토큰은 401 |
| 값 형식 | 숫자/문자열 원본 그대로 | 포맷 문자열(`"₩3,097,957 KRW"` 등)로 옴 — 파싱 필요 |

**결론**: 업로드·다중 문구가 필요한 소재 생성/라이브는 Graph API, 성과 확인·미리보기·경쟁사 조사 같은
"조회 위주" 작업은 MCP가 더 간편하다. 실제로도 라이브 절차는 이 둘을 섞어 쓴다(SKILL.md 참고).

---

## 1. Graph API

### 1.1 엔드포인트·인증

```
GET https://graph.facebook.com/v25.0/act_<광고계정ID>/insights
```

- API 버전: `v25.0`
- HTTP 메서드: GET
- 조회 대상: `act_<광고계정ID>/insights` (광고 계정 하위 insights 엣지)
- **인증**: 액세스 토큰(access token) 하나를 모든 요청에 쿼리 파라미터 `access_token=...`으로 붙인다.
- **권한**: 광고 계정 insights 조회에는 일반적으로 `ads_read` 권한(또는 해당 광고 계정에 대한
  System User/개인 토큰의 광고 관리자 권한)이 필요하다. 이는 메타 공식 스펙에 대한 일반 지식이며,
  본인 환경에서 실제로 필요한 스코프는 Meta Business Manager → 시스템 사용자에서 토큰 발급 시 확인한다.
- ⛔ 액세스 토큰·앱 시크릿·광고 계정 ID는 절대 공유 코드/문서에 하드코딩하지 않는다. 환경변수나
  별도 비밀 설정 파일에서 읽어오도록 구성한다.

### 1.2 성과 조회 (insights)

같은 엔드포인트를 `level` 파라미터만 바꿔 레벨별로 호출한다.

| 레벨 | `level` 값 | 비고 |
|---|---|---|
| 캠페인 | `campaign` | |
| 광고세트 | `adset` | 특정 캠페인으로 좁히려면 `filtering` 사용 |
| 광고 | `ad` | 특정 캠페인으로 좁히려면 `filtering` 사용 |

광고세트/광고 레벨 호출 시 `filtering` 파라미터로 특정 캠페인 id 목록에 한정할 수 있다:

```
filtering = [{"field": "campaign.id", "operator": "IN", "value": [campaign_id, ...]}]
```

`time_range`는 JSON 문자열로 인코딩해 쿼리 파라미터로 전달한다:

```
time_range = {"since": "YYYY-MM-DD", "until": "YYYY-MM-DD"}
```

`date_preset`(`yesterday`, `last_7d`, `last_30d`, `this_month` 등)으로 대체할 수도 있다.
`time_range`와 `date_preset`을 동시에 주지 않는다.

**다계정 순회**: 광고 계정이 여러 개면 계정마다 별도 API 호출로 순회(병렬 처리 권장)하고 결과를
하나의 리스트로 합친다. 각 행에 어느 계정에서 왔는지 구분하는 라벨을 붙이려면, 그 라벨은
메타 API가 주는 값이 아니라 **호출하는 쪽에서 직접 붙이는 것**임을 구분해서 다뤄야 한다.

**limit**: 캠페인은 200 안팎, 광고세트/광고는 500 안팎이 실전에서 무난하다(계정 규모에 맞게 조정).

### 1.3 성과 지표 매핑표

아래 26개는 실전에서 자주 쓰는 성과 표의 컬럼 구성 예시다. 원본 소스와 계산식을 구분해서 적는다.

| # | 컬럼키 | 이름 | 메타 API 소스 | 계산식 / 비고 |
|---|---|---|---|---|
| 1 | `spend` | 비용 | insights 기본 필드 `spend` | 그대로 사용 |
| 2 | `impressions` | 노출 | insights 기본 필드 `impressions` | 그대로 사용(정수 변환) |
| 3 | `cpm` | CPM | insights 기본 필드 `cpm` | 메타가 계산해 반환하는 값 그대로 사용(직접 재계산 안 함) |
| 4 | `reach` | 도달 | insights 기본 필드 `reach` | 그대로 사용(정수 변환) |
| 5 | `frequency` | 빈도 | insights 기본 필드 `frequency` | 그대로 사용 |
| 6 | `clicks` | 클릭 | insights 기본 필드 `clicks` | 그대로 사용(정수 변환) |
| 7 | `cpc` | CPC | insights 기본 필드 `cpc` | 메타가 계산해 반환하는 값 그대로 사용 |
| 8 | `ctr` | CTR | insights 기본 필드 `ctr` | **메타는 %(예 1.23) 단위로 반환한다.** 소수로 저장하려면 `/100`, 화면 표시 시 다시 `×100`해 `%`로 보여준다 |
| 9 | `purchases` | 구매수 | `actions[]` 배열에서 `action_type == "omni_purchase"`인 항목의 `value` | 배열에서 추출 → 정수 변환 |
| 10 | `cpa` | 구매당 비용 | 파생 | `cpa = spend / purchases` (purchases가 0 이하면 표시 안 함/`null`) |
| 11 | `revenue` | 매출 | `action_values[]` 배열에서 `action_type == "omni_purchase"`인 항목의 `value` | 배열에서 추출 |
| 12 | `cvr` | CVR | 파생 | `cvr = purchases / clicks` (clicks가 0 이하면 0.0) |
| 13 | `roas` | ROAS | insights 기본 필드 `purchase_roas`(배열의 첫 항목 `value`) | 원값을 그대로 쓰거나, 자체 매출 기준으로 재계산하려면 `roas = revenue / spend` (spend>0, revenue>0일 때만) |
| 14 | `video_play` | 동영상 재생 | `video_play_actions[]` 배열의 모든 항목 `value` 합산 | |
| 15 | `video_p3` | 동영상 3초+ 재생 | `actions[]` 배열에서 `action_type == "video_view"`인 항목의 `value` | |
| 16 | `thruplay` | ThruPlay | `video_thruplay_watched_actions[]` 배열의 모든 항목 `value` 합산 | |
| 17 | `video_avg_sec` | 평균 재생 시간 | `video_avg_time_watched_actions[]` 배열의 모든 항목 `value` 합산 | 단일 항목일 때가 보통이라 사실상 그 값 |
| 18 | `view_3s_rate` | 3초 조회율 | 파생 | `view_3s_rate = video_p3 / video_play` (video_play가 0이면 0.0) |
| 19 | `view_15s_rate` | 15초 조회율 | 파생 | `view_15s_rate = thruplay / video_play` (video_play가 0이면 0.0). 이름은 "15초"지만 실제 분자는 ThruPlay(메타의 15초 또는 완주 시청 기준 지표) |
| 20 | `rate_p25` | 25% 재생률 | `video_p25_watched_actions[]` 합산 후 파생 | `rate_p25 = video_p25 / video_play` |
| 21 | `rate_p50` | 50% 재생률 | `video_p50_watched_actions[]` 합산 후 파생 | `rate_p50 = video_p50 / video_play` |
| 22 | `rate_p75` | 75% 재생률 | `video_p75_watched_actions[]` 합산 후 파생 | `rate_p75 = video_p75 / video_play` |
| 23 | `rate_p95` | 95% 재생률 | `video_p95_watched_actions[]` 합산 후 파생 | `rate_p95 = video_p95 / video_play` |
| 24 | `rate_p100` | 100% 재생률 | `video_p100_watched_actions[]` 합산 후 파생 | `rate_p100 = video_p100 / video_play` |
| 25 | `thumb_stops` | ThumbStop | insights 필드 `thumb_stops` | ⚠ 이 필드는 요청 `fields` 목록에 **직접 추가해야만** 값이 온다. 빠뜨리면 항상 0으로 보인다(요청 안 한 필드라 응답에도 없음). 계정/광고에 따라 아예 지원되지 않을 수도 있으니 "invalid field" 에러 시 fields에서 빼고 재시도하는 방어 로직을 둘 것 |
| 26 | `account_label` | 계정 구분 | 메타 API 아님 | 다계정을 순회할 때 호출하는 쪽에서 임의로 붙이는 내부 라벨 |

**요약**: 기본 insights 필드 직접 사용 8개(`spend~ctr`) · actions/video 배열에서 원시 추출·합산 6개
(`purchases, revenue, video_play, video_p3, thruplay, video_avg_sec`) · 파생(비율/나눗셈) 10개
(`cpa, cvr, roas, view_3s_rate, view_15s_rate, rate_p25~p100`) · 요청 fields 누락 시 0이 되는 것 1개
(`thumb_stops`) · API 값이 아닌 내부 라벨 1개(`account_label`).

### 1.4 actions / action_values 파싱

`insights` 응답의 `actions`, `action_values`는 각각 아래 형태의 배열이다:

```json
"actions": [
  {"action_type": "omni_purchase", "value": "42"},
  {"action_type": "video_view", "value": "1830"}
]
```

- 구매수(`purchases`): `actions` 배열에서 `action_type == "omni_purchase"`인 원소의 `value`
- 매출(`revenue`): `action_values` 배열에서 `action_type == "omni_purchase"`인 원소의 `value`
- 3초+ 동영상 재생(`video_p3`): `actions` 배열에서 `action_type == "video_view"`인 원소의 `value`

`video_play_actions`, `video_thruplay_watched_actions`, `video_avg_time_watched_actions`,
`video_p25/50/75/95/100_watched_actions`는 각각 독립된 최상위 필드이며, 형태는 동일하게
`[{"action_type": "...", "value": "..."}]`이다. `action_type`을 구분하지 않고 **해당 필드 배열 안의
모든 원소 `value`를 합산**하는 것이 기본 처리 방식이다.

**요청할 fields 전체 예시**:

```
spend,impressions,cpm,reach,frequency,clicks,cpc,ctr,purchase_roas,action_values,actions,
video_play_actions,video_continuous_2_sec_watched_actions,video_thruplay_watched_actions,
video_avg_time_watched_actions,video_p25_watched_actions,video_p50_watched_actions,
video_p75_watched_actions,video_p95_watched_actions,video_p100_watched_actions
```

레벨별로 위 목록 뒤에 아래를 덧붙인다:

- 캠페인(`level=campaign`): `,campaign_id,campaign_name`
- 광고세트(`level=adset`): `,adset_id,adset_name,campaign_id,campaign_name`
- 광고(`level=ad`): `,ad_id,ad_name,adset_id,campaign_id`

### 1.5 ⚠ 원값과 표시값이 다른 것들 (혼동 주의)

메타 Graph API insights를 그대로 호출하면 위 1.3절 "메타 API 소스" 열에 적힌 대로
`purchases`/`revenue`/`roas`/`cvr`가 나온다(메타 픽셀 기준 `omni_purchase` 액션 기준).
하지만 실전 대시보드에서는 이 원값 위에 아래 같은 후처리를 얹는 경우가 흔하다. **이건 메타 API의
값이 아니라 각 회사 쪽 후처리**이므로, "메타 API 원값"이 필요하면 이 후처리 없이 재현해야 한다.

1. **자사 매출 데이터로 매출·구매수를 덮어쓰는 경우.** 메타 픽셀 귀속이 아니라 자사 주문 시스템
   (자사몰/이커머스 플랫폼) 기준으로 캠페인/광고세트/광고 이름을 매칭해 매출·구매수를 집계하고,
   메타에서 파싱한 원값을 **무조건 덮어쓰는** 방식이다. 이후 `roas`/`cvr`도 이 덮어써진 값 기준으로
   재계산된다.
2. **당일치를 실시간으로 추가 가산하는 경우.** 조회 기간에 오늘이 포함되면, 오늘자 자사 매출 캐시에서
   캠페인명/광고명 기준 매출·구매수를 읽어 위 1번 값에 추가로 더한다.
3. **캠페인명 별칭(alias)을 매핑해 합산하는 경우.** 캠페인명이 바뀌어도 옛 UTM에 박힌 옛 이름으로
   들어오는 자사 매출이 있으면, 정식 캠페인명 ↔ 옛 이름 매핑에 따라 합산한다.

**정리**: 순수 메타 값을 원하면 후처리 없이 API 원값(1.3절 표)만 조립한다. 회사별 표시값이 API 원값과
다르게 보인다면, 대개 위 세 가지 유형(매출 오버레이·당일 가산·이름 별칭 합산) 중 하나가 얹혀 있다는
뜻이다.

### 1.6 파이썬 호출 예시

```python
import requests

API_VERSION = "v25.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

# 본인 환경변수/비밀 설정 파일에서 채울 것 — 절대 공유 코드에 하드코딩하지 말 것
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
AD_ACCOUNT_ID = "act_<광고계정ID>"

INSIGHTS_FIELDS = ",".join([
    "spend", "impressions", "cpm", "reach", "frequency",
    "clicks", "cpc", "ctr",
    "purchase_roas", "action_values", "actions",
    "video_play_actions",
    "video_continuous_2_sec_watched_actions",
    "video_thruplay_watched_actions",
    "video_avg_time_watched_actions",
    "video_p25_watched_actions",
    "video_p50_watched_actions",
    "video_p75_watched_actions",
    "video_p95_watched_actions",
    "video_p100_watched_actions",
    "thumb_stops",  # 값이 필요하면 반드시 fields에 명시해야 함
])


def _extract_action_value(actions_list, action_type):
    for a in (actions_list or []):
        if a.get("action_type") == action_type:
            return float(a.get("value", 0) or 0)
    return 0.0


def _sum_action_values(actions_list):
    return sum(float(x.get("value", 0) or 0) for x in (actions_list or []))


def fetch_insights(level: str, since: str, until: str, campaign_ids: list = None) -> list:
    """level: 'campaign' | 'adset' | 'ad'"""
    fields = INSIGHTS_FIELDS
    if level == "campaign":
        fields += ",campaign_id,campaign_name"
    elif level == "adset":
        fields += ",adset_id,adset_name,campaign_id,campaign_name"
    elif level == "ad":
        fields += ",ad_id,ad_name,adset_id,campaign_id"

    params = {
        "access_token": ACCESS_TOKEN,
        "fields": fields,
        "level": level,
        "time_range": f'{{"since":"{since}","until":"{until}"}}',
        "limit": 200 if level == "campaign" else 500,
    }
    if campaign_ids:
        params["filtering"] = (
            '[{"field":"campaign.id","operator":"IN","value":'
            + str(campaign_ids).replace("'", '"') + "}]"
        )

    resp = requests.get(f"{BASE_URL}/{AD_ACCOUNT_ID}/insights", params=params, timeout=30)
    data = resp.json()
    if "error" in data:
        raise RuntimeError(data["error"])

    rows = []
    for ins in data.get("data", []):
        spend = float(ins.get("spend") or 0)
        impressions = int(ins.get("impressions") or 0)
        clicks = int(ins.get("clicks") or 0)
        reach = int(ins.get("reach") or 0)
        frequency = float(ins.get("frequency") or 0)
        cpm = float(ins.get("cpm") or 0)
        cpc = float(ins.get("cpc") or 0)
        ctr = float(ins.get("ctr") or 0) / 100  # 메타는 %, 소수로 통일

        actions = ins.get("actions", [])
        action_values = ins.get("action_values", [])
        purchases = int(_extract_action_value(actions, "omni_purchase"))
        revenue = _extract_action_value(action_values, "omni_purchase")
        roas_list = ins.get("purchase_roas", [])
        roas = float(roas_list[0].get("value", 0)) if roas_list else 0.0

        video_play = int(_sum_action_values(ins.get("video_play_actions", [])))
        video_p3 = int(_extract_action_value(actions, "video_view"))
        thruplay = int(_sum_action_values(ins.get("video_thruplay_watched_actions", [])))
        video_avg_sec = _sum_action_values(ins.get("video_avg_time_watched_actions", []))
        video_p25 = int(_sum_action_values(ins.get("video_p25_watched_actions", [])))
        video_p50 = int(_sum_action_values(ins.get("video_p50_watched_actions", [])))
        video_p75 = int(_sum_action_values(ins.get("video_p75_watched_actions", [])))
        video_p95 = int(_sum_action_values(ins.get("video_p95_watched_actions", [])))
        video_p100 = int(_sum_action_values(ins.get("video_p100_watched_actions", [])))
        thumb_stops = int(ins.get("thumb_stops") or 0)

        cvr = round(purchases / clicks, 4) if clicks > 0 else 0.0
        cpa = round(spend / purchases, 2) if purchases > 0 else None
        view_3s_rate = round(video_p3 / video_play, 4) if video_play > 0 else 0.0
        view_15s_rate = round(thruplay / video_play, 4) if video_play > 0 else 0.0
        rate_p25 = round(video_p25 / video_play, 4) if video_play > 0 else 0.0
        rate_p50 = round(video_p50 / video_play, 4) if video_play > 0 else 0.0
        rate_p75 = round(video_p75 / video_play, 4) if video_play > 0 else 0.0
        rate_p95 = round(video_p95 / video_play, 4) if video_play > 0 else 0.0
        rate_p100 = round(video_p100 / video_play, 4) if video_play > 0 else 0.0

        row = {
            "spend": spend, "impressions": impressions, "cpm": cpm,
            "reach": reach, "frequency": frequency,
            "clicks": clicks, "cpc": cpc, "ctr": ctr,
            "purchases": purchases, "cpa": cpa, "revenue": revenue,
            "cvr": cvr, "roas": roas,
            "video_play": video_play, "video_p3": video_p3, "thruplay": thruplay,
            "video_avg_sec": video_avg_sec,
            "view_3s_rate": view_3s_rate, "view_15s_rate": view_15s_rate,
            "rate_p25": rate_p25, "rate_p50": rate_p50, "rate_p75": rate_p75,
            "rate_p95": rate_p95, "rate_p100": rate_p100,
            "thumb_stops": thumb_stops,
            "account_label": "YOUR_LABEL",  # 메타 API 아님 — 계정 구분용으로 직접 채움
        }

        if level == "campaign":
            row["id"] = ins.get("campaign_id", "")
            row["name"] = ins.get("campaign_name", "")
        elif level == "adset":
            row["id"] = ins.get("adset_id", "")
            row["name"] = ins.get("adset_name", "")
        elif level == "ad":
            row["id"] = ins.get("ad_id", "")
            row["name"] = ins.get("ad_name", "")

        rows.append(row)

    return rows


if __name__ == "__main__":
    campaigns = fetch_insights("campaign", "2026-06-01", "2026-06-30")
    for c in campaigns:
        print(c["name"], c["spend"], c["purchases"], c["roas"])
```

이 예시는 **순수 메타 API 원값**만 조립한다(1.5절의 매출 오버레이·당일 가산·이름 별칭 합산은
포함하지 않았다). 여러 계정을 순회하려면 `AD_ACCOUNT_ID`를 바꿔가며 위 함수를 반복 호출하고 결과를
합치면 된다.

**부가 참고**:
- "invalid field" 에러 메시지를 감지하면 fields에서 문제 필드를 제거하고 재조회하는 방어 로직을 두면
  계정/광고에 따라 지원 여부가 다른 필드(예: `thumb_stops`) 대응에 도움이 된다.
- 캠페인 레벨 조회 시 같은 `campaign_id`가 중복 응답되면 첫 번째만 채택하고 이후는 스킵하는 방식으로
  중복을 제거할 수 있다.

---

## 2. MCP 서버

정본: Meta 호스팅 MCP 서버 `https://mcp.facebook.com/ads` (자체 구축 서버 아님).

### 2.1 접속·인증 (USER 토큰만 받는다)

| 사실 | 내용 |
|---|---|
| **시스템 사용자 토큰 → ❌ 401** | 스코프가 다 있어도 MCP는 시스템 사용자 토큰을 **받지 않는다** |
| **사용자(USER) 토큰 → ✅ 200** | 사람이 로그인해서 만든 토큰만 받는다 |
| 필수 스코프 | `ads_mcp_management` + `ads_read` + `ads_management` + `catalog_management` + `business_management` + `pages_show_list` + `instagram_basic` |
| **토큰 수명의 한계** | 사용자 토큰은 원리상 만료가 있다. 단기(~2시간) → 장기 교환해도 **최대 60일**, 비밀번호 변경·앱 시크릿 재설정 시 즉시 무효화된다. 값을 문서에 못 박지 말고 **발급 방법**을 박아둘 것 |

전달 방식: `Authorization: Bearer <USER_TOKEN>` + JSON-RPC (streamable HTTP).

**토큰 발급 절차**:
1. Graph API Explorer(https://developers.facebook.com/tools/explorer) 접속
2. 오른쪽 위 Meta App → 본인 앱 선택
3. User or Page → User Token
4. Permissions 칸에 위 필수 스코프 전부 추가
5. Generate Access Token → 로그인 승인 → 나온 토큰 문자열 복사
6. 단기 토큰을 장기 토큰으로 교환(60일)해 저장. 이 폴더에서는 `python setup_wizard.py check`로
   현재 토큰의 유효성·만료를 확인한다.

계정마다 MCP 개방 여부가 다르니, 새 계정을 다루기 전에 `python setup_wizard.py check`로
확인한다.

### 2.2 호출 형식 (JSON-RPC, tools/list, tools/call)

이 폴더에서는 아래 명령으로 MCP를 직접 호출한다(SSH나 별도 서버 불필요):

```bash
python mcp.py tools                              # 도구 이름 전체 목록
python mcp.py schema <도구명>                     # 특정 도구 인자 스펙
python mcp.py call <도구명> '<JSON 인자>'          # 호출
python setup_wizard.py check                     # 토큰 유효성·만료·MCP 스코프 확인
```

내부적으로는 JSON-RPC 2.0 형식으로 `tools/list`(도구 목록), `tools/call`(도구 호출)을
`https://mcp.facebook.com/ads`에 POST하고, 헤더에 `Authorization: Bearer <USER_TOKEN>`을 싣는다.

### 2.3 자주 쓰는 도구

| 용도 | 도구 |
|---|---|
| 계정 목록·개방여부 | `ads_get_ad_accounts` |
| 성과 조회(전 레벨) | `ads_get_ad_entities` |
| 필드 검증 | `ads_get_field_context` |
| 광고 미리보기 | `ads_get_ad_preview` |
| 캠페인 히스토리 | `ads_account_get_activity_logs` |
| 이상징후·추세·벤치마크 | `ads_insights_anomaly_signal`, `ads_insights_performance_trend`, `ads_insights_industry_benchmark` |
| 생성(전부 PAUSED) | `ads_create_campaign` → `ads_create_ad_set` → `ads_create_creative` → `ads_create_ad` → `ads_activate_entity` |
| 수정 | `ads_update_entity` |
| A/B·리프트 테스트 | `ads_experiment_abtest_create_test`, `ads_experiment_lift_create_test` |
| 카탈로그 | `ads_catalog_*` |
| 픽셀·데이터셋 | `ads_pixel_*`, `ads_get_dataset_*` |
| 경쟁사 광고 검색 | `ads_library_search` |
| 도움말 검색 | `ads_get_help_article` |

**성과 조회 실전 예제** (`ads_get_ad_entities` — campaign/adset/ad 전 레벨 하나로 처리):

```bash
python mcp.py call ads_get_ad_entities '{
  "ad_account_id": "<광고계정ID>",
  "level": "campaign",
  "fields": ["id","name","status","amount_spent","impressions","cpm","reach","frequency",
             "clicks","cpc","ctr","actions:omni_purchase","omni_purchase_values",
             "cost_per_omni_purchase","purchase_roas","video_play_actions",
             "3_second_video_plays","video_thruplay_watched_actions","video_avg_time_watched_actions",
             "video_p25_watched_actions","video_p50_watched_actions","video_p75_watched_actions",
             "video_p95_watched_actions","video_p100_watched_actions"],
  "time_range": "{\"since\":\"2026-07-13\",\"until\":\"2026-07-19\"}",
  "sort": "amount_spent_descending",
  "limit": 200,
  "advertiser_request": "최근 7일 캠페인별 성과"
}'
```

**계정 레벨 합계** (`level="account"`) — 계정 통합 지출·매출·ROAS가 한 줄로 온다:

```bash
python mcp.py call ads_get_ad_entities '{
  "ad_account_id": "<광고계정ID>",
  "level": "account",
  "fields": ["amount_spent","impressions","clicks","actions:omni_purchase","omni_purchase_values","purchase_roas"],
  "date_preset": "last_7d",
  "advertiser_request": "계정 합계"
}'
```

### 2.4 MCP 필드명이 Graph API와 다른 점

Graph API의 26개 성과 지표는 `thumb_stops` 하나 빼고 전부 MCP에도 있다(이름만 다름).

| Graph API 필드 | MCP 필드 | 비고 |
|---|---|---|
| `spend` | `amount_spent` | |
| `purchases` | `actions:omni_purchase` | 배열 파싱 불필요, 숫자로 옴 |
| `revenue` | `omni_purchase_values` | |
| `cpa`(계산 필요) | `cost_per_omni_purchase` | **계산 불필요, MCP가 이미 계산해서 줌** |
| `roas` | `purchase_roas` | 값이 포맷 문자열이 아니라 순수 숫자로 오는 몇 안 되는 필드 |
| `ctr` (Graph API는 /100 보정 필요) | `ctr` | 이미 % |
| `video_p3` | `3_second_video_plays` | |
| `video_play` | `video_play_actions` | |
| `thruplay` | `video_thruplay_watched_actions` | |
| `video_p25~p100` | `video_p25_watched_actions`~`p100` | 이름만 다름 |
| `video_avg_sec` | `video_avg_time_watched_actions` | ⚠ **정수로 옴**(2,1,3…). Graph API 원값은 소수 표시가 자연스러움 |
| `impressions·reach·frequency·cpm·cpc·clicks` | 동일 | |
| `thumb_stops` | **없음** | MCP에는 대응 필드가 없다 |
| `campaign_id`/`campaign_name` | `id`/`name` | |

**MCP로 전환 시 사라지는 로직**: actions/action_values 파싱, 배열 합산, `thumb_stops` fields 누락
방어, 다계정 병렬 호출(도구 하나가 다계정을 처리하는 경우가 많음).
**전환해도 남는 로직**: 자사 매출 오버레이, 당일 실시간 가산, 이름 별칭 합산(1.5절) — 화면에
보여줄 실제 매출/구매수/ROAS를 이런 후처리로 덮는 구조라면, MCP로 바꿔도 화면 숫자 자체는 바뀌지
않는다.

### 2.5 MCP 함정

⛔ 전부 실측으로 확인된 함정이다.

- **`fields`는 배열**이다. 문자열로 주면 `expected a list of items` 에러.
- **`time_range`는 JSON "문자열"**(이스케이프 필요)이다. 또는 `date_preset`(`yesterday`, `last_7d`,
  `last_30d`, `this_month` 등) 중 하나만 쓴다. 둘 다 주면 에러.
- **필드명이 Graph API와 다르다**(2.4절 매핑표). 틀린 필드명을 넣으면 에러 메시지가 **지원 필드
  전체를 알려주므로** 거기서 골라 쓰면 된다.
- **값이 포맷 문자열로 온다**: `"₩3,097,957 KRW"`, `"1.53%"` 식. `purchase_roas`만 순수 숫자다.
  숫자로 쓰려면 `₩`, `KRW`, 콤마, 공백을 전부 벗겨내야 한다(`REPLACE(REPLACE(col,',',''),' ','')`
  같은 패턴).
- **⚠ 계정마다 응답 형식이 다르다.** 어떤 계정은 `impressions`가 `"713,350"`(콤마 있음)에
  `amount_spent_cents`(정수) 필드가 딸려오고, 다른 계정은 `impressions`가 `"912744"`(콤마 없음)에
  cents 필드가 아예 없는 식이다. `_cents` 같은 정수 필드가 있고 없고를 가정하지 말고, **문자열
  파싱을 기본 처리 방식으로** 삼는다.
- **빈 배열 `[]` = 집행/데이터 없음이지 에러가 아니다.** 코드에서 0으로 처리하면 된다.
- 조회 전 `ads_get_ad_accounts`의 `is_queryable`을 확인해두면, 닫힌 계정을 조회해 에러를
  받는 걸 미리 피할 수 있다.

**속도 참고**: 단일 계정 7일 기준 Graph API가 캠페인 10개에 약 1.18초, MCP가 캠페인 94개에
약 1.52초였다(실측 사례). 데이터 양 대비로 보면 MCP가 유리하지만, 절대 속도 자체는 비슷한
수준이라 **속도만으로 전환을 판단할 근거는 못 된다.**

---

## 3. 공통 함정

- **actions 계열 배열은 항상 `action_type`으로 골라 써야 한다.** 배열 순서를 신뢰하지 말 것 —
  같은 캠페인이라도 응답에 포함되는 action_type의 개수·순서가 날짜/캠페인마다 다르다.
- **CTR·CVR 같은 비율 지표는 분모가 0일 때를 반드시 처리한다.** 클릭 0인데 나눗셈을 그대로
  돌리면 에러이거나 잘못된 극단값이 나온다.
- **회사마다 "표시값"과 "API 원값"이 다를 수 있다는 전제를 깔고 시작한다.** 자체 매출 데이터로
  덮어쓰거나, 당일 데이터를 실시간으로 얹거나, 이름이 바뀐 캠페인을 옛 이름과 합산하는 로직이
  대시보드 쪽에 있으면 API 원값과 표시값이 달라진다(1.5절). 다른 회사와 숫자를 맞춰볼 때는
  어느 쪽이 "순수 API 값"이고 어느 쪽이 "후처리된 표시값"인지부터 구분해야 한다.
- **다계정을 순회할 때 계정 구분 라벨은 API가 주는 값이 아니라는 점을 명확히 한다.** 이 라벨을
  API 응답 필드처럼 취급하면 나중에 "이 필드가 왜 문서에 없지"라는 혼란이 생긴다.
- **토큰·시크릿·계정 ID는 코드/문서에 값 자체를 남기지 않는다.** 환경변수나 gitignore된 별도
  설정 파일에서 읽어오게 하고, 문서에는 "어떻게 발급받는지" 절차만 남긴다.
