---
name: meta-ad-live
description: 소재 파일(영상·이미지)을 받아 메타 광고를 캠페인·광고세트·소재·광고까지 만들고 라이브(게재 시작)까지 하는 실전 절차. MCP(mcp.facebook.com/ads)와 Graph API를 섞어 쓴다. 문구·제목은 AI가 베리에이션. "소재 라이브해줘", "이 영상들로 광고 만들어줘", "광고 켜줘", "메타에 올려줘" 류 요청에 이 스킬을 부른다.
---

# 메타 광고 라이브 (실전 절차)

> **2026-07-29 전 구간 실호출 검증 완료.** 아래 인자·값은 실제로 캠페인→광고세트→크리에이티브→광고까지
> 만들어보고(그리고 삭제하고) 확인한 것이다. 추측으로 쓴 값 없음.
> 이 폴더 안에 필요한 게 다 있다 — 다른 정보 찾으러 갈 필요 없음.

## 0. ⛔ 먼저 알 것 — 돈이 나가는 지점

```
업로드 · 캠페인 · 광고세트 · 크리에이티브 · 광고 생성  →  전부 PAUSED  →  돈 안 나감
ads_activate_entity (3층 전부)                        →  ACTIVE      →  💸 과금 시작
```

**담당자 재량**이므로 예산·계정·라이브에 별도 승인은 필요 없다. 다만 **켜기 직전 한 줄 요약**
(계정 / 캠페인명 / 광고 수 / 일예산)은 반드시 보여주고 켠다.

## 0-0. 🔴 라이브(켜기)·삭제는 **3중 확인** 후에만 실행 (권장)

담당자가 "켜줘" / "라이브해줘" / "삭제해줘" 라고 말해도 **바로 실행하지 않는다.**
아래 3단계를 **순서대로, 매번 새로 물어본다.** 같은 질문을 3번 반복하는 게 아니라 **확인 내용이 다르다.**

| 단계 | 무엇을 확인하나 | 물어볼 말 |
|---|---|---|
| **1차 — 대상 확인** | 계정·캠페인명·광고 수·일예산·성과목표를 **표로 다 펼쳐서** 보여준다. 엉뚱한 캠페인을 켜는 사고를 막는 단계 | "이 대상이 맞습니까?" |
| **2차 — 되돌릴 수 없는 결과 확인** | 켜기: **지금부터 과금 시작, 켜져 있던 동안 쓴 돈은 환불 안 됨**(§10)<br>삭제: **복구 불가. 캠페인 삭제 시 하위 광고세트·광고 전부 함께 삭제**(§10) | "이 결과를 알고 진행합니까?" |
| **3차 — 실행 직전 최종** | 실행할 API 호출과 대상 ID를 그대로 보여준다(3층 전부 켜는지, 어느 ID를 지우는지) | "지금 실행합니다. 마지막으로 맞습니까?" |

- **3단계를 한 메시지에 몰아 쓰지 않는다.** 각 단계마다 담당자 답을 받고 다음으로 간다
- 어느 단계에서든 답이 모호하면(**"어…" "일단" "아마"**) **멈춘다.** 명확한 승인만 승인으로 본다
- 담당자가 "3번 묻지 말고 그냥 해"라고 하면 **1차 표만 보여주고 1회 확인 후 진행**한다 (그 지시는 기록해 둔다)
- ⛔ **끄기(PAUSED)와 예산 낮추기는 3중 확인 대상이 아니다** — 돈이 새는 걸 막는 방향이라 즉시 실행한다

## 0-1. ⛔ 이 스킬의 존재 이유 = 속도 (제일 중요)

> **목적**: 기존 세팅 방식을 **더 간소화**하기
> — 기준선은 수동이 아니다. 대시보드 페이지에서 **항목을 하나씩 클릭해 넣던 방식**을 이미 쓰고 있었고,
> 그 클릭 단계를 없애는 것이 목적이다
> **목표**: 소재만 던지면 → 전부 세팅 → **사람이 최종 확인 1회** → 업로드

**중간 질문을 늘리면 이 스킬은 의미가 없다.** 기존 방식과 손이 비슷하게 들면 만든 이유가 사라진다.

| ❌ 하지 말 것 | ✅ 이렇게 |
|---|---|
| 랜딩·문구·캠페인키워드·제품을 **차례로 하나씩** 물어보기 | 판단 가능한 건 **근거를 대며 자동 확정**하고, 확인은 **라이브 직전 1회**로 몰아 한 화면에 정리 |
| "이렇게 할까요?"를 단계마다 반복 | 생성(PAUSED·과금 0원)까지 **끊지 않고 진행** → 미리보기·UTM·요약을 함께 보여주고 딱 한 번 확인 |

### ⚠ 단계를 구분할 것 — 지금은 테스트 기간

| 단계 | 질문 정책 |
|---|---|
| **테스트 기간 (지금)** | **사람 확인이 필요한 지점은 계속 물어본다.** 무엇을 묻게 되는지 드러나야 자동화 후보를 찾을 수 있다. 물어본 항목은 아래 "자동화 후보"에 **판정 근거와 함께 기록**한다 |
| 운영 전환 후 | 자동 확정으로 옮기고, 확인은 라이브 직전 1회로 몰아 한 화면에 정리 |

**자동화 후보 기록** (테스트에서 물어본 것 → 자동 판정 근거):

| 물어본 항목 | 자동 판정 근거 | 상태 |
|---|---|---|
| 제품 | 파일명 → `products.json` 대조. 실패 시 상위 폴더의 `.prproj`·`.prin` 파일명 대조 (실측: `제품A_소구점.prproj` ↔ `기존소재_소구점_54%.mp4`) | 반자동 (감지 실패 시 질문) |
| 랜딩 URL | `products.json.ad_url` > 운영 중 고ROAS 광고의 실제 링크 > `url` | **자동 가능** (ad_url 추가 완료) |
| 문구·제목 | 최근 고ROAS 광고의 현행 문구 그대로 (§7-0) | **자동 가능** |
| 캠페인키워드 | 같은 제품 최근 캠페인명에서 이어받기 (예: `<캠페인키워드>제품A`) | **자동 가능** |
| 소구점 | 파일명에서 추출 | **자동 가능** |
| 일예산·타겟 | 기본값 100,000원 / 18~65 남녀 | 확인만 |
| 할인율 숫자 | §7-0으로 랜딩 페이지 실제 할인율 확인 | 미구현 |

**자동 확정 기준** (근거를 함께 보여주면 물어보지 않는다):
- **제품** — 파일명에서 감지(§4). 실패하면 상위 폴더명·같은 폴더의 프로젝트 파일명까지 본다. 그래도 모르면 **그것만** 묻는다
- **랜딩 URL** — `products.json`의 `ad_url` > `url`. 더 확실한 근거는 **운영 중 고ROAS 광고의 실제 링크**(§7-0)
- **문구·제목** — 최근 고ROAS 광고의 현행 문구를 **기본값으로 그대로 쓴다**(§7). 새로 쓰고 싶을 때만 제안
- **캠페인키워드** — 같은 제품의 최근 캠페인명에서 이어받는다 (예: `<캠페인키워드>제품A`)
- **소구점** — 파일명에서 뽑는다 (`기존소재_소구점_54%.mp4` → `소구점`)
- **일예산·타겟** — 기본값(100,000원 / 18~65 남녀)으로 세팅하고 최종 확인 화면에 표시

## 1. 준비 — 토큰 (제일 먼저 확인)

**⚠ 이 폴더는 어디에 둬도 된다.** 아래 명령의 `<이폴더>`는 SKILL.md가 있는 폴더 경로로 바꿔 쓴다
(스킬로 설치했다면 `~/.claude/skills/meta-ad-live`, 바탕화면에 뒀다면 `~/Desktop/meta-ad-live` 등).
스크립트는 자기 위치를 스스로 찾으므로 **경로만 맞으면 어디서 실행하든 동작한다.**

```bash
# macOS / Linux
cd <이폴더>/scripts && python3 mcp.py tools | head -3
```
```powershell
# Windows — python3 대신 python
cd <이폴더>\scripts ; python mcp.py tools | Select-Object -First 3
```
도구 이름이 나오면 준비 끝. 토큰 상태만 보려면 `python check_token.py`(유효성·권한·만료일 한 번에).

⚠ **Windows 주의 — 이 문서의 명령은 bash 기준이다.** `TOKEN=$(...)`, `curl -d '{...}'`, 홑따옴표 JSON 인자는
PowerShell에서 그대로 동작하지 않는다(§5-6·§8·§10이 해당). Windows에서는 **Bash 도구(Git Bash)로 실행**하거나
PowerShell 문법으로 바꿔 쓴다. `mcp.py`·`upload_media.py` 호출은 양쪽 다 문제없다.

토큰은 아래 순서로 **자동** 확보된다(대부분 그냥 된다):
1. 환경변수 `META_MCP_TOKEN`
2. **이 폴더 안의 `.token` 파일** ← 폴더를 옮겨도 따라다닌다(권장)
3. `~/.claude/skills/meta-ad-live/.token` 또는 `~/.meta-ad-live-token`

**401이 나면** = 토큰 만료. 재발급:
1. https://developers.facebook.com/tools/explorer → 앱 `<앱ID>` 선택 (config.json의 `app_id`)
2. User Token + 권한 **5개만** (최소권한):
   `ads_mcp_management` `ads_read` `ads_management` `pages_show_list` `pages_manage_ads`
3. Generate Access Token → 복사
4. `echo "<토큰>" > <이폴더>/.token`   ← SKILL.md와 같은 폴더에 저장
5. `python check_token.py` 로 검증. 새 토큰을 팀에 배포하기 전이면 `python smoke_test.py`로 전 구간 확인

⛔ **권한을 더 붙이지 말 것.** `leads_retrieval`(고객 개인정보) · `catalog_management`(상품 피드) ·
`business_management`는 라이브 절차에 쓰지 않는다. 붙여두면 토큰 유출 시 피해가 광고비를 넘어 개인정보·상품
데이터로 번진다. 광고 생성·예산·라이브는 `ads_management` 하나로 전부 된다.
(단 `pages_manage_ads`를 빼면 §5-4 크리에이티브 생성이 막힐 수 있다.)

📅 **토큰에는 "데이터 접근 만료일"이 따로 있다.** 토큰 자체가 무기한(`expires_at:0`)이어도
이 날짜가 지나면 조회가 막힌다. `python setup_wizard.py check` 로 남은 일수를 확인할 수 있으니,
만료 전에 미리 재발급한다. 여러 사람이 같은 토큰을 쓰면 그날 전원이 동시에 멈춘다.

⛔ **시스템 사용자 토큰은 MCP에서 401로 거부된다**(실측). 반드시 **USER 토큰**.
Graph API(업로드)는 둘 다 되지만, 스크립트가 같은 토큰을 쓰므로 USER 토큰 하나로 통일한다.

### 토큰을 새로 발급해도 기존 것은 안 죽는다 (실측 확인)

| 행동 | 기존 토큰(대시보드·ads가 쓰는 `metaad.js` 등) |
|---|---|
| 여기서 새 토큰 발급 | ✅ **무사** — 토큰은 여러 개 동시 유효 |
| Explorer에서 토큰 생성 | ✅ 무사 |
| **앱 시크릿 재설정** | ❌ **그 앱의 토큰 전부 즉사** |
| 계정 비밀번호 변경 | ❌ USER 토큰 사망(시스템 사용자 토큰은 무사) |

⛔ **앱 시크릿(App Secret)은 함부로 재설정하지 말 것.** 재설정하면 대시보드 성과 조회·ads 서버 자동화가
쓰는 토큰까지 같이 죽어서 **서비스가 멈춘다.** 꼭 해야 하면 "재설정 → 전 토큰 재발급 → 서버 배포"를
한 번에 처리할 준비를 하고 진행한다.

## 2. 설정값 (config.json)

광고계정·페이지·픽셀·인스타·기본예산은 폴더의 `config.json`에 있다.

```
처음이라면: python setup_wizard.py check → discover → write   (SETUP.md 참고)
확인:      python setup_wizard.py verify
```

```
Graph API  https://graph.facebook.com/v25.0
MCP        https://mcp.facebook.com/ads
```

⚠ 광고계정이 여러 개일 수 있다. `config.json`의 `default_account_id`가 기본값이고,
계정마다 상태(정지 여부 `is_queryable`)가 다를 수 있으니 `ads_get_ad_accounts`로 항상 재확인한다.

## 3. 도구 분담 — MCP만으로는 안 된다

| 단계 | 도구 | 이유 |
|---|---|---|
| 소재 업로드 | **Graph API** (`upload_media.py`) | ⛔ MCP엔 **로컬 파일** 업로드 도구가 없다. `ads_creative_upload_image/video`는 **공개 URL에서만** 받아오므로 PC의 파일은 못 올린다 |
| 문구·제목 **2개 이상** | **Graph API** `asset_feed_spec` (§8) | ⛔ MCP는 `message`/`headline` 각 1개만 |
| 캠페인·광고·미리보기 | **MCP** | |
| 광고세트 — **전환 가치 극대화(`VALUE`)** | **Graph API** | ⛔ MCP `ads_create_ad_set`이 `VALUE`를 거부한다("최적화 목표가 잘못됨"). Graph API로는 정상 생성됨(실측 2026-07-30) |
| 광고세트 — 전환수(`OFFSITE_CONVERSIONS`) | MCP 가능 | |
| 크리에이티브 | **Graph API** | MCP는 제목 1개·설명 없음·개선사항 설정 불가(§5-4-1) |
| 미리보기 | **MCP** `ads_get_ad_preview` | 기존 마법사에 없던 기능 |
| 라이브 | **MCP** `ads_activate_entity` | **3층 전부** 켜야 함(§6) |
| 성과 확인 | **MCP** `ads_get_ad_entities` | |

## 4. 담당자에게 받을 것

⛔ **아래 표에서 "반드시 물어본다"로 표시된 3개는 절대 추측하지 말 것.**

| 항목 | 처리 방식 |
|---|---|
| 소재 파일 | 담당자가 준다 (폴더 경로 또는 파일 목록) |
| 🔴 **광고 계정** | **반드시 물어본다.** 담당자·건마다 다르다. 기본값으로 넘기지 말 것.<br>`python mcp.py call ads_get_ad_accounts '{}'` 로 목록을 보여주고 고르게 한다. `config.json`의 `default_account_id`가 기본값이지만, 계정이 여러 개면 그중 정지 상태(`is_queryable=False`)인 것도 있을 수 있으니 목록에서 상태까지 확인한다<br>⛔ **계정을 바꾸면 소재를 그 계정으로 다시 업로드해야 한다**(미디어는 올린 계정 귀속) → 업로드 전에 정한다 |
| 🔴 **성과 목표** | **기본값 = 전환 가치 극대화 `optimization_goal: "VALUE"`** (권장).<br>**그래도 한 번은 물어본다** — *"성과 목표는 전환 가치 극대화로 갑니다. 전환수 극대화로 하시겠어요?"*<br>담당자가 **"전환수"라고 하면** `OFFSITE_CONVERSIONS`. 답이 없거나 상관없다고 하면 `VALUE`.<br>⛔ 광고세트 생성 시점에 정해진다 → **나중에 바꾸려면 광고세트를 새로 만들고 광고도 다시 붙여야 한다**(크리에이티브는 재사용 가능).<br>참고: 운영 중 캠페인도 `VALUE`를 쓰는 경우가 많다. 두 목표를 비교 테스트 중이면 담당자 지시를 우선한다 |
| 🔴 **크리에이티브 개선사항** | **반드시 물어본다.** 켤 수 있는 항목 전체 목록은 `reference/creative_features.md`. 요청받은 것만 `OPT_IN`, 나머지는 `OPT_OUT` |
| **제품** | **① 파일명에서 자동 감지** — `reference/products.json`의 제품 목록과 대조<br>**② 못 찾으면 반드시 물어본다** (추측해서 진행하지 말 것 — 랜딩 URL·캠페인명·귀인이 전부 틀어진다) |
| **일 예산** | **항상 물어본다.** 기본값은 `config.json`의 기본예산 제시 후 확인. 🔴 **원 그대로 입력** = `100000` (§5-2) |
| 소재 설명 | 물어본다 (캠페인명에 들어감. 예: 여름특가, 쇼호스트, 테스트) |
| 광고 계정 | `config.json`의 `default_account_id` — 다른 계정이면 담당자가 지정 |
| 랜딩 URL | `products.json`의 **`ad_url`이 있으면 그걸 먼저** 쓴다(광고 전용 프로모션 페이지). 없으면 `url`.<br>⛔ **실측 함정**: 어떤 제품은 `url`(일반 상품페이지)과 운영 광고가 쓰는 페이지(별도 프로모션 페이지)가 **서로 다른 상품페이지**였다. 둘 다 200이라 눈치채기 어렵다 → **§7-0으로 운영 중 광고의 실제 링크를 대조**할 것 |
| 타겟 | 18~65 남녀 (기본값 그대로 진행, 지정 시 반영) |
| 문구·제목 | AI가 3~5개 제안 → 담당자 확정 (§7) |

**제품 자동 감지 규칙**: 파일명에서 확장자·날짜·번호·구분자를 떼고 `products.json` 이름과 대조한다.
예) `제품A_쇼호스트_01.mp4` → `제품A` / `productA_ad.mp4` → 한글명 매칭 실패 → **물어본다**.
여러 제품이 섞여 있으면 파일별로 감지하되, 애매한 것만 모아서 한 번에 확인한다.

## 4-1. 🔴 소재 파일명 규칙 — 자동화의 출발점 (권장)

**파일명이 유일한 자동 판별 근거다.** 여기에 제품·소구점이 들어 있으면 물어볼 게 사라진다.
실측: 파일명 규칙 없이 온 소재는 **제품 감지가 전부 실패**했고, `신규소재_1~4.mp4`처럼 소구점을 알 수 없으면
**썸네일을 하나씩 열어 화면을 읽어야** 했다. 파일명만 제대로 왔으면 그 과정이 전부 없어진다.

```
{제품}_{소구점}.{확장자}          ← 필요한 건 이 2개뿐. 번호는 도구가 붙인다

  제품A_발바닥.mp4       제품A_품절대란.mp4       제품B_속근육지압.mp4
```

| 칸 | 규칙 |
|---|---|
| `{제품}` | **앞에 제품명만 넣으면 된다.** 표기가 달라도 도구가 `products.json` 목록에 **자동 매핑**한다<br>실측: 띄어쓰기·줄임말이 섞여도(`제품 A`→제품A 처럼) 자동 매핑됐다 |
| `{소구점}` | 이 소재가 **무엇으로 설득하는지 한 단어(2~6자)**. 🔴 광고명·`utm_content`에 그대로 들어가 **매출 귀인 키**가 된다 |
| 번호 | **넣지 않아도 된다.** 도구가 판정 통과한 소재에 **1부터 연속으로** 붙인다 |
| 공백·특수문자·날짜 | **있어도 된다.** 도구가 정리해서 광고명을 다시 쓴다 (`제품A_1200돌기_54%.mp4` → `제품A_영상_1200돌기_일반_4`) |
| 피할 것 | `신규소재_1` · `최종` · `사본` · `수정본` — **소구점을 알 수 없는 이름** |

### ⛔ 제품 매핑 확인 절차 (필수)

제품 표기를 **그대로 쓰지 않고 다시 쓴 경우**(부분일치·유사 매핑), 광고를 만들기 전에
**매핑 결과를 담당자에게 보여주고 확인받는다.** `--scan`이 이 목록을 뽑아준다.

```
⛔ 제품명을 이렇게 매핑했습니다 — 담당자에게 맞는지 확인받고 진행할 것
    제품A_찜질.mp4      → 제품A정식명칭   [부분일치]
    제품B_극락.mp4      → 제품B+옵션세트  [부분일치]  (다른 후보: 제품B오리지널 / 제품B_변형1 …)
    제품C_복부.mp4      → 제품Cv2        [부분일치]  (다른 후보: 제품Cv3)
```
- **후보가 2개 이상이면 반드시 물어본다.** 실측: 이름 앞부분만으로는 후보가 3~4개까지 걸리는 경우가 있었다
  (버전 표기·세트 구성이 갈리는 제품군) → 임의로 고르면 **랜딩 URL과 매출 귀인이 엉뚱한 제품으로 붙는다**
- 확인 문구 예: *"`제품C_복부.mp4`를 **제품Cv2**로 봤습니다. v3가 맞나요?"*

**검증된 소구점 예시** (실제 운영·이번 배치에서 쓰인 것):
`발바닥` `붓기` `극락` `1200돌기` `집에오면` `타임특가` `마감임박` `품절대란` `입소문` `후기` `곧종료` `속근육지압` `쇼호스트` `여름특가`

**⛔ 파일명이 규칙에 안 맞으면 — 업로드 전에 담당자에게 고쳐 달라고 요청한다.**
`upload_media.py --scan`이 파일별로 판정해 주고, 안 맞으면 규칙표까지 출력한다.
```bash
python upload_media.py --scan <소재폴더>      # 제품 / 소구점 / 파일명 판정
```
요청 문구 예:
> 소재 파일명에 **제품과 소구점**을 넣어주세요 — `제품A_발바닥_01.mp4` 형식입니다.
> 이 소구점이 광고명과 매출 귀인 키로 그대로 들어가서, 지금 이름(`신규소재_1.mp4`)으로는
> 나중에 어떤 소재가 잘 나왔는지 성과 분석이 안 됩니다.

**담당자가 "그냥 진행해라"고 하면** 막지 말고 진행한다. 대신 ① 제품·소구점을 직접 물어보거나
② 썸네일을 열어 화면 내용을 읽어(§7-0-2) 소구점을 정하고, **정한 값을 보여주고 확인받은 뒤** 만든다.

## 5. 실행 순서 (검증된 명령 그대로)

작업 디렉토리: `cd <이폴더>/scripts` (§1 참고 — 폴더 위치는 자유)

### 5-1. 소재 업로드 (Graph API)

**폴더를 받았으면 먼저 `--scan`으로 확인하고 담당자에게 보여준다.** 업로드는 그 다음.
```bash
python3 upload_media.py --scan 소재폴더/       # 업로드 안 함. 목록·미디어타입·제품 감지만
python3 upload_media.py 소재폴더/              # 폴더 안 소재 전부 업로드 (하위 폴더까지)
python3 upload_media.py 소재1.mp4 소재2.jpg     # 파일 지정도 가능(섞어 써도 됨)
python3 upload_media.py --account <광고계정ID> 소재.mp4   # 다른 계정
```
→ `media_id`(이미지=`image_hash`, 영상=`video_id`), 영상 썸네일 URL, **감지된 제품·랜딩 URL**이 JSON으로 나온다.

폴더 처리 규칙(스크립트가 자동으로 한다):
- 소재 확장자만 집는다 — 영상 `mp4 mov avi m4v webm mkv` / 이미지 `jpg jpeg png gif webp bmp`
- `.txt`·`.psd`·엑셀 등은 **건너뛰고 목록에 이유를 표시**한다
- macOS 잔재(`__MACOSX`, `._`로 시작하는 파일)와 숨김 파일은 제외
- 하위 폴더까지 훑고, 파일명 순으로 정렬한다
- 파일명에서 **제품을 자동 감지**한다(§4). `product: null`이면 **랜딩 URL을 정할 수 없으니 반드시 물어본다**

⛔ **업로드 계정 = 광고 만들 계정.** 다르면 Meta가 "미디어 없음" 에러를 낸다.

### 5-2. 캠페인 생성
```bash
python3 mcp.py call ads_create_campaign '{
  "ad_account_id":"<광고계정ID>",
  "campaign_name":"260729_판매_캠페인_여름특가_제품A",
  "objective":"OUTCOME_SALES",
  "buying_type":"AUCTION",
  "campaign_daily_budget":100000,
  "special_ad_categories":"[]"
}'
```
→ `campaign_id` 반환, `status: PAUSED`

⛔ **함정 2개 (실제로 밟고 확인)**
- 🔴 **예산은 원(KRW) 그대로 넣는다. 100,000원 → `100000`.**
  **2026-07-30 정정**: 이 문서에 "cents 단위, 0 두 개 더 붙인다(`10000000`)"라고 적혀 있었는데 **완전히 틀렸다.**
  그대로 따라서 캠페인을 만들었더니 일예산이 **₩10,000,000(천만원)** 으로 잡혔다. 100배 사고다.
  검증 방법(같은 계정의 기존 캠페인과 대조):
  ```
  MCP 표시 ₩100,000  →  raw daily_budget = 100000     ← 배율 1
  MCP 표시 ₩252,000  →  raw daily_budget = 252000
  ```
  KRW는 소수점이 없는 통화라 offset이 1이다. **만들고 나서 반드시 raw 값을 다시 읽어 확인할 것**:
  ```bash
  curl -s -G "https://graph.facebook.com/v25.0/<campaign_id>" \
    --data-urlencode "fields=name,daily_budget" --data-urlencode "access_token=$TOKEN"
  ```
- **`special_ad_categories`는 배열이 아니라 문자열** `"[]"`. 배열로 주면 `Expected string` 에러

목표: 판매/공구 → `OUTCOME_SALES`, 트래픽 → `OUTCOME_TRAFFIC`

### 5-3. 광고세트 생성
```bash
python3 mcp.py call ads_create_ad_set '{
  "ad_account_id":"<광고계정ID>",
  "campaign_id":"<위에서 받은 campaign_id>",
  "ad_set_name":"260729_어드밴티지_1865_남녀",
  "billing_event":"IMPRESSIONS",
  "optimization_goal":"VALUE",
  "targeting":"{\"geo_locations\":{\"countries\":[\"KR\"]},\"age_min\":18,\"age_max\":65,\"targeting_automation\":{\"advantage_audience\":1}}",
  "promoted_object":"{\"pixel_id\":\"<픽셀ID>\",\"custom_event_type\":\"PURCHASE\"}"
}'
```
→ `ad_set_id` 반환, PAUSED

- 🔴 **`optimization_goal` 기본값은 `VALUE`**(전환 가치 극대화, §4). 담당자가 전환수라고 하면 `OFFSITE_CONVERSIONS`
- ⛔ **`VALUE`는 위 MCP 명령으로 안 된다**("최적화 목표가 잘못됨"). **Graph API로 만든다**(실측 2026-07-30):
  ```bash
  TOKEN=$(python -c "import sys;sys.path.insert(0,'.');from mcp import get_token;print(get_token())")
  curl -X POST "https://graph.facebook.com/v25.0/act_<광고계정ID>/adsets" \
    -d "name=260730_어드밴티지_1865_남녀" -d "campaign_id=<campaign_id>" \
    -d "billing_event=IMPRESSIONS" -d "optimization_goal=VALUE" -d "status=PAUSED" \
    -d 'targeting={"geo_locations":{"countries":["KR"]},"age_min":18,"age_max":65,"targeting_automation":{"advantage_audience":1}}' \
    -d 'promoted_object={"pixel_id":"<픽셀ID>","custom_event_type":"PURCHASE"}' \
    -d "access_token=$TOKEN"
  ```
- ⛔ **CBO 캠페인은 광고세트들의 최적화 목표가 모두 같아야 한다.** 다른 목표로 추가하면
  *"광고 게재 최적화 기준이 동일해야 함"* 에러. **목표를 바꾸려면 기존 광고세트를 먼저 삭제**해야 한다
  (하위 광고도 함께 삭제되지만 **크리에이티브는 남으므로 광고만 다시 붙이면 된다** — 실측)
- **`targeting`·`promoted_object`는 JSON 문자열**(이스케이프 필요)
- 성별 지정 시 targeting에 `"genders":[1]`(남) 또는 `[2]`(여). 남녀 전체면 넣지 않음
- CBO(캠페인 예산)를 쓰면 광고세트에 `daily_budget` 넣지 않는다
- attribution(클릭7일·조회1일)은 Meta가 자동으로 붙여준다

### 5-4. 크리에이티브 생성 (소재 1개당)
```bash
python3 mcp.py call ads_create_creative '{
  "ad_account_id":"<광고계정ID>",
  "page_id":"<페이지ID>",
  "image_hash":"<업로드로 받은 hash>",
  "link_url":"https://example.com/product/제품A/<상품번호>/?utm_source=meta&utm_medium=cpc&utm_campaign=<캠페인명>&utm_content=<광고명>",
  "message":"본문 문구",
  "headline":"제목",
  "call_to_action_type":"SHOP_NOW",
  "name":"제품A_이미지_마감임박_일반_1"
}'
```
→ `creative_id` 반환

- **영상이면** `image_hash` 대신 `video_id` + `image_url`(썸네일, upload_media.py가 같이 준다)
- **UTM은 `link_url`에 직접 박아 넣는다** — 실측으로 `link_data.link`와 `call_to_action.value.link` 양쪽에 정상 저장됨 확인
- ⚠ Meta가 크리에이티브 이름 뒤에 날짜+해시를 자동으로 붙인다(`..._1 2026-07-29-fb155...`). **광고(ad) 이름은 우리가 준 그대로 유지되므로 귀인에 영향 없다**

### 5-4-1. ⛔ 크리에이티브 필수 설정 (권장 규칙)

**MCP `ads_create_creative`로는 아래를 넣을 수 없다. 그래서 §8 Graph API 경로가 기본이다.**
운영 중 승자 광고를 전수 조회해 확인한 실제 구조다.

| 항목 | 필드 | 값 |
|---|---|---|
| **여러 광고주의 광고** | `contextual_multi_ads` | **`{"enroll_status":"OPT_OUT"}` 고정** (미체크 상태) |
| **표시 링크** | `object_story_spec.video_data.call_to_action.value.link_caption` | **자사 도메인 고정** (예: `"example.com"`) |
| **인스타그램 계정** | `object_story_spec.instagram_user_id` | `config.json`의 `instagram_user_id` (`<인스타ID>`) — 없으면 IG 지면 노출이 제한된다 |
| **본문** | `asset_feed_spec.bodies` | **1개** |
| **제목** | `asset_feed_spec.titles` | **최소 3개, 권장 4개** |
| **설명** | `asset_feed_spec.descriptions` | **1개 이상 (필수 — 예전엔 빠뜨렸다)** |
| **문구 최적화** | `asset_feed_spec.optimization_type` | `"DEGREES_OF_FREEDOM"` |
| **사람마다 문구 최적화** | `degrees_of_freedom_spec…text_optimizations` | **`OPT_IN` 고정** |
| **행동 유도** | `call_to_action.type` / `asset_feed_spec.call_to_action_types` | **기본 `ORDER_NOW`(지금 주문하기).** 담당자가 다른 걸 원하면 그 값으로 바꾼다(고정 아님) |
| **개선사항** | `degrees_of_freedom_spec.creative_features_spec` | **기본 5개**(권장): `text_optimizations` `enhance_cta` `inline_comment` `description_automation` `feed_caption_optimization`<br>⛔ `standard_enhancements`는 넣지 말 것(지원 중단, Meta가 자동 처리) / `generate_cta`도 제외(CTA 고정)<br>전체 58개 목록·함정: `reference/creative_features.md` |
| **개선사항 변경** | — | ⛔ **생성 시점에만 설정된다.** 나중에 덮어쓰기 불가(이름·status·라벨만 수정 가능) → 바꾸려면 **크리에이티브 재생성 + 광고 재부착**(캠페인·광고세트·영상은 재사용, 1~2분) |

기본 골격(영상):
```json
"object_story_spec": {
  "page_id": "<페이지ID>",
  "instagram_user_id": "<인스타ID>",
  "video_data": {
    "video_id": "<video_id>", "image_url": "<썸네일>",
    "message": "<본문>", "title": "<제목1>",
    "call_to_action": {"type": "ORDER_NOW",
      "value": {"link": "<UTM URL>", "link_caption": "example.com"}}}}
"asset_feed_spec": {
  "videos": [{"video_id": "<video_id>", "thumbnail_url": "<썸네일>"}],
  "bodies": [{"text": "<본문>"}],
  "titles": [{"text": "<제목1>"}, {"text": "<제목2>"}, {"text": "<제목3>"}, {"text": "<제목4>"}],
  "descriptions": [{"text": "<설명>"}],
  "link_urls": [{"website_url": "<UTM URL>", "display_url": "example.com"}],
  "call_to_action_types": ["ORDER_NOW"],
  "optimization_type": "DEGREES_OF_FREEDOM"}
"contextual_multi_ads": {"enroll_status": "OPT_OUT"}
"degrees_of_freedom_spec": {"creative_features_spec": {
  "text_optimizations": {"enroll_status": "OPT_IN"}, ...담당자가 고른 것}}
```

만든 뒤 **반드시 읽어서 대조**한다(§5-6). 특히 `link_caption`·`descriptions`·`contextual_multi_ads`·
`degrees_of_freedom_spec`은 조용히 빠지기 쉽다.

### 5-5. 광고 생성
```bash
python3 mcp.py call ads_create_ad '{
  "ad_account_id":"<광고계정ID>",
  "ad_set_id":"<ad_set_id>",
  "ad_name":"제품A_이미지_마감임박_일반_1",
  "creative":"{\"creative_id\":\"<creative_id>\"}"
}'
```
→ `ad_id` 반환, PAUSED. **`creative`는 JSON 문자열.**

소재 N개 × 광고세트 M개 → 5-4·5-5를 **N×M번** 반복(광고명 번호는 1부터 증가).

### 5-6. 검증 (라이브 전 필수)
```bash
python3 mcp.py call ads_get_ad_preview '{"ad_id":"<ad_id>"}'
```
→ `preview_url`을 담당자에게 보여준다(브라우저에서 실제 노출 모습 확인 가능).

⚠ 미리보기 응답의 `creative.body`·`link_url`이 **비어 보여도 정상**이다(표시 형식 문제). 실제 저장값은 Graph API로 확인:
```bash
TOKEN=$(python3 -c "import sys;sys.path.insert(0,'.');from mcp import get_token;print(get_token())")
curl -s -G "https://graph.facebook.com/v25.0/<creative_id>" \
  --data-urlencode "fields=name,object_story_spec" --data-urlencode "access_token=$TOKEN" | python3 -m json.tool
```
**UTM이 제대로 박혔는지 여기서 반드시 확인**(틀리면 매출 귀인이 깨진다).

### 5-7. 라이브 — ⛔ 3층 전부 켜야 한다

🔴 **실행 전에 §0-0의 3중 확인을 반드시 거친다.** 담당자가 "켜줘"라고 해도 바로 켜지 않는다.
```bash
# 캠페인
python3 mcp.py call ads_activate_entity '{"ad_account_id":"<광고계정ID>","entity_id":"<campaign_id>","entity_type":"campaign"}'
# 광고세트
python3 mcp.py call ads_activate_entity '{"ad_account_id":"<광고계정ID>","entity_id":"<ad_set_id>","entity_type":"ad_set"}'
# 광고 (여러 개면 각각)
python3 mcp.py call ads_activate_entity '{"ad_account_id":"<광고계정ID>","entity_id":"<ad_id>","entity_type":"ad"}'
```

**Meta 공식 문구(도구 설명 원문):**
> "Activating a parent does NOT automatically activate its children. For ads to deliver, **ALL levels must be ACTIVE**. Activating a child while its parent is paused will **succeed, but will NOT deliver**."

⚠ **광고만 켜면 "성공" 응답이 오는데 실제로는 노출이 안 된다.** 성공했다고 착각하기 쉬운 지점.
(참고: 대시보드 기존 마법사의 "게재 시작"은 광고만 켠다 — 그래서 광고관리자에서 상위를 따로 켜야 했다.)

**끄기**는 `ads_update_entity`로:
```bash
python3 mcp.py call ads_update_entity '{"ad_account_id":"<광고계정ID>","entity_id":"<id>","entity_type":"ad","fields":"{\"status\":\"PAUSED\"}"}'
```

### 5-8. 기존 캠페인에 소재 추가 (2026-07-30 실측 검증)

"이미 돌고 있는 캠페인에 새 소재만 얹어달라"는 요청. **새 캠페인을 만들지 않는다.**

**① 기존 정보를 먼저 자동 파악한다** (추측 금지 — 이름 하나 틀리면 귀인이 깨진다)
```bash
TOKEN=$(python -c "import sys;sys.path.insert(0,'.');from mcp import get_token;print(get_token())")
# 캠페인명 (UTM에 그대로 써야 한다) · 상태 · 예산
curl -s -G "https://graph.facebook.com/v25.0/<campaign_id>" \
  --data-urlencode "fields=name,status,daily_budget" --data-urlencode "access_token=$TOKEN"
# 광고세트 (최적화 목표까지)
curl -s -G "https://graph.facebook.com/v25.0/<campaign_id>/adsets" \
  --data-urlencode "fields=name,status,optimization_goal" --data-urlencode "access_token=$TOKEN"
# 기존 광고명 → 끝 번호 확인
curl -s -G "https://graph.facebook.com/v25.0/<campaign_id>/ads" \
  --data-urlencode "fields=name,status" --data-urlencode "limit=100" --data-urlencode "access_token=$TOKEN"
```

**② 지켜야 할 것**

| 항목 | 규칙 |
|---|---|
| `utm_campaign` | 🔴 **기존 캠페인명을 그대로** 쓴다. 새로 만들면 자사 매출 데이터에서 매출이 갈린다 |
| 광고 번호 | 기존 광고명 끝 번호의 **최댓값 + 1**부터. 실측: 번호가 중복돼 있을 수 있으니 max 기준 |
| 광고세트 | **2개 이상이면 어디에 넣을지 반드시 물어본다.** 1개면 그것에 붙인다 |
| 최적화 목표 | 기존 광고세트 값을 **그대로 따른다**(새로 정하지 않는다). 실측: 운영 캠페인은 `VALUE`(전환 가치)를 쓰고 있었다 |
| 소재 업로드 계정 | 🔴 **그 캠페인이 속한 계정**에 올린다. 다른 계정에 올리면 "미디어 없음" |
| 예산 | **건드리지 않는다.** 기존 값 유지 |
| 상태 | 캠페인·광고세트가 이미 ACTIVE여도 **신규 광고는 PAUSED로 생성된다**(실측) → **광고만** `ads_activate_entity`로 켜면 즉시 게재된다(상위는 이미 ACTIVE) |
| **랜딩 URL** | 🔴 **기존 광고에서 읽어와 그대로 쓴다.** `products.json`을 다시 보지 말 것 — 그 캠페인이 실제로 쓰는 프로모션 페이지가 따로 있을 수 있다(§4)<br>`GET /<기존 ad_id>?fields=creative{object_story_spec}` → `video_data.call_to_action.value.link`에서 쿼리스트링을 떼고 재사용 |
| 문구 | 기존 광고 문구를 이어받는 게 기본(§7-0). 새 소재의 화면 내용이 다르면 그 소재에 맞춰 새로 쓴다 |

**③ 순서**: 소재 업로드(§5-1) → 크리에이티브(§5-4·5-4-1) → 광고 생성 시 `ad_set_id`에 **기존 광고세트 ID** → 미리보기(§5-6) → 광고만 활성화

**④ 되돌리기**: 추가한 광고만 지운다. ⛔ **캠페인을 지우면 기존 광고까지 전부 사라진다**(§10).
```bash
curl -s -X DELETE "https://graph.facebook.com/v25.0/<추가한 ad_id>?access_token=$TOKEN"
```

## 6. 이름 규칙 — ⛔ 절대 바꾸지 말 것

대시보드/자사 매출 데이터의 매출 귀인이 이 문자열 매칭에 의존한다. 바꾸면 **매출이 0으로 뜬다.**

```
캠페인:   {YYMMDD}_{목표}_{예산유형}_{캠페인키워드}_{제품}
광고세트: {YYMMDD}_어드밴티지_{연령4자리}_{성별}    예) 260729_어드밴티지_1865_남녀
광고:     {제품}_{미디어타입}_{소구점}_일반_{번호}   예) 제품A_영상_마감임박_일반_1
UTM:      utm_source=meta&utm_medium=cpc&utm_campaign={캠페인명}&utm_content={광고명}
```

**캠페인명 4개 칸 (권장 규칙)**

| 칸 | 값 |
|---|---|
| `{YYMMDD}` | 만드는 날짜 |
| `{목표}` | **판매** / **트래픽** / **카탈로그** / **공구** 중 하나 (→ objective 매핑: 판매·공구 `OUTCOME_SALES`, 트래픽 `OUTCOME_TRAFFIC`, 카탈로그 `OUTCOME_SALES`+카탈로그 세팅) |
| `{예산유형}` | **캠페인** = CBO(`campaign_daily_budget`) / **광고세트** = ABO(광고세트별 `daily_budget`) |
| `{캠페인키워드}` | 자유 텍스트. 예: `<캠페인키워드>`, `여름특가`. 담당자 표기를 붙일 수 있다 |
| `{제품}` | **복수 가능 — `/`로 이어 붙인다.** 예: `제품A_옵션1/제품B_옵션1` |

예) `260730_판매_캠페인_<캠페인키워드>_제품A` (CBO·판매 목표)
- **담당자 표기(권장)**: 공용 토큰을 여러 명이 쓰면 광고관리자 변경 로그에 전원이 **같은 사용자**로 찍혀
  사고(예: 예산 100배 오입력) 원인 추적이 안 된다. `{소재설명}` 자리에 담당자를 함께 넣으면 추적이 된다 —
  예) `260730_판매_캠페인_여름특가김대리_제품A`. **형식은 그대로라 매출 귀인은 깨지지 않는다**(자유 텍스트 구간)
- 성별: `both`→남녀, `male`→남, `female`→여 / 연령 4자리 = `1865`(18~65)
- 미디어타입: mp4·mov·avi·m4v·webm·mkv → `영상`, 나머지 → `이미지`
- 제품명 목록: `reference/products.json` (파일명 앞부분과 대조해 자동 감지)

## 7. 문구 베리에이션 — AI가 할 일

### 7-0. 먼저 "지금 잘 나가는 광고"를 그대로 베낀다 (기본 경로)

새로 쓰기 전에 **현행 승자 광고의 실제 문구·제목·랜딩·CTA를 뽑아 기본값으로 쓴다.** 이게 가장 빠르고 안전하다.
```bash
# 1) 고ROAS 광고 id 찾기
python mcp.py call ads_get_ad_entities '{"ad_account_id":"<광고계정ID>","level":"ad","fields":["name","amount_spent","purchase_roas"],"date_preset":"last_30d","sort":"purchase_roas_descending","limit":15}'
# 2) 그 광고의 실제 문구·랜딩 뽑기 (Graph API — MCP 미리보기는 body가 비어 보인다)
TOKEN=$(python -c "import sys;sys.path.insert(0,'.');from mcp import get_token;print(get_token())")
curl -s -G "https://graph.facebook.com/v25.0/<ad_id>" \
  --data-urlencode "fields=name,creative{object_story_spec,asset_feed_spec}" \
  --data-urlencode "access_token=$TOKEN" | python -m json.tool
```
실측으로 확인된 것(고ROAS 운영 광고 기준):
- 운영 광고는 **`asset_feed_spec`(§8) 경로**를 쓴다 — 본문 1개 + **제목 2개**
- CTA는 **`ORDER_NOW`** (이 문서 §5-4 예시의 `SHOP_NOW`가 아니다)
- 랜딩은 `products.json`의 `url`이 아니라 **프로모션 페이지**였다 → §4 참고
- `asset_feed_spec.link_urls`는 비어 있고, 링크는 `object_story_spec…call_to_action.value.link`에 들어 있었다

### 7-0-1. ⛔ 가격·할인율은 반드시 랜딩에서 검증한다 (`check_landing.py`)

**문구에 숫자를 쓰기 전에 이걸 먼저 돌린다. 안 하면 소재·문구·랜딩이 서로 다른 숫자를 말한다.**
```bash
python check_landing.py --product 제품A --claim 54
python check_landing.py "<랜딩 URL>" --claim 54
```
`meta product:price` · `ld+json offers.price` · 본문 `판매가/소비자가` 표기를 **교차 검증**하고,
`--claim`으로 준 할인율이 실제보다 과장이면 **exit 1로 막는다**.

📌 **실측 — 세 숫자가 다 달랐다** (수치는 예시)
| 출처 | 값 |
|---|---|
| 랜딩 실제 (정가 → 판매가 기준 계산) | **가장 높은 할인율** |
| 소재 화면·파일명 | **랜딩보다 낮은 값** |
| 당시 운영 광고 문구 | **랜딩보다 낮은 값(소재와도 다름)** |

소재·문구 표기가 실제보다 낮아 허위는 아니었지만, **소재 화면과 문구가 다른 숫자를 말하면 신뢰가 깨진다.**
→ **소재에 적힌 숫자에 문구를 맞추는 것이 기본.** 검증 불가면 숫자를 아예 쓰지 않는다.

⚠ **소재끼리 정가가 다를 수 있다**(실측: 같은 배치에서 소재별로 표기 정가가 서로 달랐다).
랜딩 기준으로 통일할지, 소재별로 맞출지 **담당자에게 확인**한다.

⚠ cafe24 페이지는 JS 렌더링이라 **본문 텍스트만 긁으면 가격이 안 나온다.** `check_landing.py`는 meta 태그·ld+json을 보므로 잡힌다.

⛔ **`check_landing.py`가 판정할 수 없는 경우 — "최대 N%" 표기 (실측)**
이 도구는 **대표 가격 하나**(meta 태그·ld+json)만 읽는다. **옵션(길이·구성)별로 가격이 다른 상품**은
옵션마다 할인율이 달라서, 도구가 계산한 값보다 **실제 최대 할인율이 더 클 수 있다.**
- 실측: 옵션이 여러 개인 세트 상품에서 도구는 대표 옵션 기준으로 계산해 소재의 `최대 N%` 표기를 과장이라고 판정.
  실제로는 **다른 옵션에서 소재 표기와 같은 값이 나와 맞는 표기였다.**
- ⇒ **`최대 N%` 형태의 표기는 도구 판정만으로 반박하지 말고 담당자에게 확인한다.**
  도구가 "과장"이라고 해도, 옵션 상품이면 담당자 확인이 우선이다.
- 도구 판정이 확실히 유효한 경우: **단일 옵션 상품**, 또는 `최대` 없이 특정 할인율을 단정하는 표기.

### 7-0-2. 소재별로 문구를 다르게 쓴다 (권장 규칙)

⛔ **소재 여러 개에 같은 문구를 넣지 말 것.** 소재마다 화면에 다른 소구점이 있으므로 문구도 그에 맞춘다.
- 소구점은 **파일명에서** 뽑는다 (`기존소재_발바닥_54%.mp4` → `발바닥`)
- 파일명이 `신규소재_1.mp4`처럼 무의미하면 **썸네일을 직접 보고** 내용을 파악해 소구점을 정한다
  ```bash
  python upload_media.py --scan <폴더>        # thumbnail_url 확보
  # 썸네일을 내려받아 이미지로 열어 화면의 문구·가격·할인율을 읽는다
  ```
  실측 예) `신규소재_1~4.mp4` → 붓기 / 입소문 / 품절대란 / 후기 로 확정
- **소재 화면에 적힌 내용만 문구로 쓴다.** 없는 혜택을 만들어내지 않는다

### 7-1. 새로 쓸 때

담당자가 문구를 안 줬거나 "알아서 뽑아줘" 하면:

1. **성과 근거 확보** — 최근 고ROAS 광고를 본다
   ```bash
   python3 mcp.py call ads_get_ad_entities '{"ad_account_id":"<광고계정ID>","level":"ad","fields":["name","amount_spent","purchase_roas"],"date_preset":"last_30d","sort":"purchase_roas_descending","limit":20}'
   ```
2. **소재DB 참고** — 자사에 톤·앵글을 정리한 소재 자산(페르소나 카드 등)이 있으면 참고
3. **3~5개 제안** → 담당자 확정
4. 각 안마다 **소구점 한 단어**를 같이 뽑는다(광고명에 들어감: `마감임박`, `신년세일` 등)
5. 2개 이상 쓸 거면 §8 경로로

## 8. 다중 문구(asset_feed_spec) — Graph API 직접

MCP는 문구·제목을 1개씩만 받는다. 여러 개를 Meta AI가 조합하게 하려면 Graph API로:

```bash
TOKEN=$(python3 -c "import sys;sys.path.insert(0,'.');from mcp import get_token;print(get_token())")
curl -X POST "https://graph.facebook.com/v25.0/act_<광고계정ID>/adcreatives" \
  -d "name=제품A_영상_마감임박_일반_1" \
  -d 'object_story_spec={"page_id":"<페이지ID>","link_data":{"image_hash":"<hash>","link":"<UTM붙은URL>","message":"<첫문구>","name":"<첫제목>","call_to_action":{"type":"SHOP_NOW"}}}' \
  -d 'asset_feed_spec={"link_urls":[{"website_url":"<UTM붙은URL>"}],"optimization_type":"DEGREES_OF_FREEDOM","bodies":[{"text":"문구1"},{"text":"문구2"},{"text":"문구3"}],"titles":[{"text":"제목1"},{"text":"제목2"}],"call_to_action_types":["SHOP_NOW"]}' \
  -d "access_token=$TOKEN"
```
→ 받은 `id`를 5-5의 `creative_id`로 쓴다. 문구·제목 각 최대 5개.
(영상이면 `link_data` 대신 `video_data`, `asset_feed_spec`에 `videos:[{"video_id":"..."}]`)

## 9. ⛔ 함정 모음 (전부 실측으로 밟은 것)

| 함정 | 내용 |
|---|---|
| 🔴 **예산은 원 그대로** | 100,000원 = `100000`. **이 문서가 예전에 `10000000`(cents)이라고 잘못 안내해 일예산이 천만원으로 잡힌 사고가 있었다.** KRW offset=1. 만든 뒤 raw 값 재확인 필수(§5-2) |
| **`special_ad_categories`** | 배열 ❌ / 문자열 `"[]"` ✅ |
| **JSON 문자열 인자** | `targeting`·`promoted_object`·`creative`·`fields`는 **문자열**로 이스케이프 |
| **라이브는 3층 전부** | 광고만 켜면 성공 응답 오지만 노출 안 됨 |
| **업로드 계정 불일치** | 미디어는 올린 계정 귀속. 다른 계정에서 쓰면 "미디어 없음" |
| **대용량 영상 업로드 중 연결 끊김** | Meta가 전송 중 연결을 리셋한다(실측: 12MB 영상 48%에서 `WinError 10054`). `upload_media.py`가 1·2·4·8초 백오프로 4회 재시도하고, 한 파일이 죽어도 나머지는 계속 올린다 |
| **업로드 직후 썸네일 없음** | 인코딩 중이라 `thumbnails`가 빈 배열이다(실측: 직후 0개 → `status.video_status: ready` 후 11~14개). **영상 크리에이티브는 `image_url`이 필수**라 이걸 놓치면 §5-4가 막힌다. `upload_media.py`가 자동으로 기다리며, 놓쳤으면 `python upload_media.py --thumbs <video_id>`로 복구 |
| **MCP 로컬 업로드 불가** | MCP 업로드 도구는 공개 URL만 받는다. PC 파일은 무조건 Graph API |
| **MCP 다중 문구 불가** | 1개만. 여러 개는 §8 |
| **MCP가 `VALUE`를 거부** | 전환 가치 극대화 광고세트는 **Graph API로만** 생성된다(§5-3). MCP는 "최적화 목표가 잘못됨" |
| **CBO는 목표 통일 필수** | 캠페인 내 광고세트 최적화 목표가 다르면 에러. 바꾸려면 기존 광고세트 삭제 후 재생성(크리에이티브 재사용 가능) |
| **크리에이티브는 광고세트와 독립** | 광고세트를 지워도 크리에이티브는 남는다. 목표 변경 시 **광고만 다시 붙이면 됨**(9개 재생성 1분) |
| **정지 계정 사용 불가** | 정지 상태(`is_queryable=False`). Graph든 MCP든 안 됨. 여러 계정 중 하나가 정지돼 있을 수 있으니 `ads_get_ad_accounts`로 매번 확인 |
| **시스템 사용자 토큰 401** | MCP는 USER 토큰만 |
| **크리에이티브명 자동 변조** | Meta가 날짜+해시 붙임. 광고명은 그대로라 귀인 무관 |
| **미리보기 body 빈칸** | 표시 형식 문제. 실제 값은 Graph API로 확인 |
| **미리보기 URL이 `&amp;`로 나온다** | `preview_url`이 HTML 이스케이프된 채 온다. 그대로 열면 `amp;t=`가 되어 **미리보기가 깨진다.** `&amp;` → `&` 치환해서 담당자에게 준다 |
| **랜딩이 products.json과 다름** | 광고용 프로모션 페이지가 따로 있다. `ad_url` 우선, 운영 광고 링크와 대조(§4·§7-0) |
| 🔴 **랜딩 URL은 조용히 틀린다** | `ad_url`을 못 읽으면 코드가 `url`(일반 상품페이지)로 **조용히 폴백**한다. 실측(재테스트): `upload_media.py`가 `ad_url`을 누락해 소재 전부가 엉뚱한 일반 상품페이지로 붙었고, **에러 없이 정상처럼 보였다.** 검증 게이트(§5-6)가 광고 생성 전에 막아서 사고를 피했다 → **크리에이티브 생성 후 링크 재확인은 생략 금지** |
| **값이 포맷 문자열** | 성과 조회 시 `"₩3,097,957 KRW"` — 계산하려면 ₩·콤마·KRW 제거 |
| **이름 규칙 변경** | 매출 귀인 즉사(§6) |

## 10. 실수했을 때

🔴 **삭제도 §0-0의 3중 확인을 거친다.** 복구가 안 되기 때문이다.
(반대로 **끄기·예산 낮추기는 즉시 실행** — 손해를 막는 방향이므로 확인 절차 없이 바로 한다)

- **잘못 만들었다** → 캠페인을 지우면 하위(광고세트·광고) 전부 함께 삭제된다
  ```bash
  TOKEN=$(python3 -c "import sys;sys.path.insert(0,'.');from mcp import get_token;print(get_token())")
  curl -s -X DELETE "https://graph.facebook.com/v25.0/<campaign_id>?access_token=$TOKEN"
  ```
- **잘못 켰다** → `ads_update_entity`로 즉시 PAUSED(§5-7). 켜져 있던 동안 쓴 돈은 환불 안 됨
- **광고관리자에서 직접** 보려면 생성 응답의 `ads_manager_url`을 열면 된다

## 11. 완료 후 보고 형식

```
✅ 라이브 완료
계정    : <계정명> (<광고계정ID>)
캠페인  : 260729_판매_캠페인_여름특가_제품A
광고세트: 1개 (18~65 남녀)
광고    : 5개
일 예산 : 100,000원
상태    : 캠페인·광고세트·광고 전부 ACTIVE
광고관리자: <ads_manager_url>
```
성과는 **다음날부터** `ads_get_ad_entities`로 확인(당일은 미집계).
자사 대시보드에도 뜨지만 **매출·구매수는 자사 매출 데이터 값으로 덮어씌워진다** — 이름 규칙이 맞아야 매칭된다.

## 12. 이 폴더 구성

```
SKILL.md                    이 문서 (실행 절차)
README.md                   담당자용 설치 안내 (배포 시 같이 전달)
setup.ps1 / setup.sh        원클릭 설치 (Windows / macOS) — 토큰 검증 + 스킬 설치 + 연결 확인
scripts/config.py            config.json 로더 (회사별 값을 읽어온다. 수정 불필요)
scripts/setup_wizard.py      config.json 생성/검증 (check → discover → write, verify)
scripts/mcp.py              MCP 호출기 (tools / schema / call)
scripts/upload_media.py     소재 업로드 (Graph API)
scripts/check_token.py      토큰 검증 (유효성·종류·권한·만료일)
scripts/check_landing.py    랜딩 실제 가격·할인율 검증 (§7-0-1) — 문구에 숫자 쓰기 전 필수
scripts/smoke_test.py       전 구간 E2E 테스트 — 캠페인 만들고 자동 삭제 (과금 없음)
reference/products.json     제품 목록 + 랜딩 URL (+ 광고 전용 ad_url)
reference/creative_features.md  크리에이티브 개선사항 58개 전체 + 실측 함정 (§5-4-1)
reference/tools.md          MCP 도구 97개 전체 목록
config.json                 회사별 값(광고계정·페이지·픽셀·인스타·기본예산). setup_wizard.py로 생성
.token                      토큰 (설치 시 생성. ⛔ 배포 zip에는 넣지 않는다)
```

## 13. 팀 배포

새 담당자에게 넘길 때: **`.token`과 `__pycache__`를 뺀** 폴더를 zip으로 압축해 전달하고,
토큰(197자 문자열)은 **사내 공유 위치(노션 비공개 페이지 등)로 따로** 알려준다.
담당자는 압축 풀고 `setup.ps1`(Windows) 또는 `bash setup.sh`(mac) 실행 → 토큰 붙여넣기 1회 → **Claude Code 재시작**.
자세한 안내와 문제 해결은 `README.md`.

⛔ zip 안에 `.token`을 넣지 않는다. 카톡·메일로 한 번 돌면 회수가 불가능하고, 무효화하려면
토큰 재발급 = 담당자 전원 재배포가 된다.
