# 크리에이티브 개선사항 (어드밴티지+ Creative) 전체 목록

- 출처: 실제 운영 중이던 성과 좋은 영상 광고의
  `degrees_of_freedom_spec.creative_features_spec` **전수 조회 — 2026-07-30, 총 58개**
- 적용 방법: 크리에이티브 생성 시 아래처럼 넣는다. **요청받은 것만 `OPT_IN`, 나머지는 안 넣으면 자동 `OPT_OUT`**
  ```json
  "degrees_of_freedom_spec": {
    "creative_features_spec": {
      "text_optimizations": {"enroll_status": "OPT_IN"},
      "enhance_cta":        {"enroll_status": "OPT_IN"},
      "inline_comment":     {"enroll_status": "OPT_IN"}
    }
  }
  ```
  ⛔ `standard_enhancements`는 **넣지 말 것** (지원 중단 — 넣으면 생성 실패. 아래 함정 1번)
- 확인 방법(만든 뒤 실제로 켜졌는지):
  ```bash
  curl -s -G "https://graph.facebook.com/v25.0/<creative_id>" \
    --data-urlencode "fields=degrees_of_freedom_spec" --data-urlencode "access_token=$TOKEN"
  ```

⚠ 한글 이름은 Meta 광고관리자 UI 기준의 **대응 추정**이다. **기준은 API 키**다.
설명은 그 기능이 하는 일을 적었고, 확실하지 않은 항목은 `(?)`로 표시했다.

---

## A. 영상 판매 광고 — 기본 권장 (2026-07-30 실제 생성해 검증)

| API 키 | 하는 일 | 신규 생성 시 |
|---|---|---|
| `text_optimizations` | **사람마다 문구 최적화** — 본문·제목·설명을 사용자별로 조합해 노출 | ✅ 지정 → 반영됨 |
| `enhance_cta` | 행동 유도 문구 개선 | ✅ 지정 → 반영됨 |
| `inline_comment` | 광고에 댓글 노출 (사회적 증거) | ✅ 지정 → 반영됨 |
| `standard_enhancements` | 표준 개선 (밝기·대비 등 자동 보정) | ⛔ **명시 지정 불가 — 지원 중단.** 단 **Meta가 자동으로 켠다** |
| `reveal_details_over_time` | 정보를 시간차로 순차 노출 | ⚠ 생성 직후엔 붙지만 **몇 분 뒤 빠졌다** (아래 참고) |

### ⛔ 실측 함정 3개 (여기서 시간 많이 버림)

**1. `standard_enhancements`를 지정하면 크리에이티브 생성이 실패한다**
```
error_subcode 3858504
"크리에이티브에 기본 개선 사항 필드를 포함하는 기능이 지원 중단되었습니다.
 대신 개별 기능을 설정하도록 선택하세요."
```
운영 중인 옛 광고는 이 필드를 **갖고 있다**(중단 전에 만들어져서). 그걸 보고 그대로 따라 하면 에러가 난다.
**지정하지 말 것.** 안 넣어도 Meta가 알아서 `OPT_IN`으로 켜준다(실측: 9개 전부).

**2. 요청한 기능이 나중에 조용히 빠질 수 있다**
`text_optimizations` + `enhance_cta` + `inline_comment` + `reveal_details_over_time` 4개를 지정했을 때:
- 생성 직후 조회 → 4개 전부 `OPT_IN` ✅
- 몇 분 뒤 조회 → `reveal_details_over_time`이 사라지고 `standard_enhancements`가 대신 켜짐
- 원인 추적: 단독 지정 ✅ / 4개 조합 ✅ / `link_urls` 유무 무관 / 90초 후에도 유지 / 광고에 붙여도 무관
  → **90초보다 긴 시간대에 Meta가 사후 재조정**한다. 재현 조건은 특정 못 함.

**⇒ 규칙: 생성 직후 검증만 믿지 말고, 몇 분 뒤 한 번 더 읽어 확인한다.**
```bash
curl -s -G "https://graph.facebook.com/v25.0/<creative_id>" \
  --data-urlencode "fields=degrees_of_freedom_spec" --data-urlencode "access_token=$TOKEN"
```

**3. 조회 시점에 따라 기능 목록 개수가 변한다** — 옛 크리에이티브는 58개, 새로 만든 것은 82개가 나왔다.
목록 길이로 판단하지 말고 **필요한 키의 `enroll_status`만** 확인한다.

## A-2. 문구 관련 — Meta가 문구를 만들거나 바꾸는 기능 (2026-07-30 실측)

`text_optimizations`(이미 켬)는 **우리가 준 문구를 사람마다 다르게 조합**하는 것이다.
**Meta가 문구를 새로 만들어주는 것**은 아래 항목들이고, **5개 전부 `OPT_IN`으로 저장됨을 실측 확인**했다.

| API 키 | 하는 일 (추정) | 주의 |
|---|---|---|
| `description_automation` | **설명(description) 자동 생성** | ⛔ 우리가 쓴 설명을 Meta가 바꿀 수 있다. 설명을 고정하려면 끈다 |
| `feed_caption_optimization` | **피드 캡션(본문) 최적화·생성** | 본문이 지면별로 달라질 수 있다 |
| `generate_cta` | **CTA 문구 자동 생성** | ⛔ 담당자가 고정한 `ORDER_NOW`(지금 주문하기)와 충돌할 수 있다 |
| `advantage_plus_creative` | 어드밴티지+ 크리에이티브 묶음 활성 | 범위가 넓어 무엇이 바뀔지 예측이 어렵다 |
| `biz_ai` | Meta AI 기반 전반 개선 | 위와 같음 |

⚠ **한글 UI 라벨과 API 키의 1:1 대응은 Meta가 공개하지 않는다.** 위 설명은 키 이름과 동작 범주에서 추정한 것이다.
**실제로 어떤 문구가 생성됐는지는 게재 후 광고관리자에서 확인해야 한다** — 미리보기에는 원본 문구만 보이는 경우가 많다.

### ✅ 현재 기본 조합 (담당자 확정, 2026-07-30)

```json
"creative_features_spec": {
  "text_optimizations":        {"enroll_status": "OPT_IN"},
  "enhance_cta":               {"enroll_status": "OPT_IN"},
  "inline_comment":            {"enroll_status": "OPT_IN"},
  "description_automation":    {"enroll_status": "OPT_IN"},
  "feed_caption_optimization": {"enroll_status": "OPT_IN"}
}
```
`generate_cta`는 **넣지 않는다** — CTA는 `ORDER_NOW`(지금 주문하기)로 고정하기로 했다.
`advantage_plus_creative`·`biz_ai`도 범위가 넓어 제외했다.

### 📌 API ↔ 광고관리자 UI 대응 (2026-07-30 화면 대조 확인)

광고 편집 화면(`단일 미디어` + 직접 입력 문구)에서 **UI에 보이는 문구 관련 항목은 딱 하나**다.

| UI 표시 | 대응 API |
|---|---|
| 기본 문구 / 제목 / 설명 | `asset_feed_spec.bodies` / `titles` / `descriptions` — **입력값 그대로 표시됨** |
| **사람마다 문구 최적화 → 활성화됨** | `text_optimizations` |
| 행동 유도 → 지금 주문하기 | `call_to_action.type = ORDER_NOW` |
| **(표시 없음)** | `description_automation` · `feed_caption_optimization` · `enhance_cta` · `inline_comment` |

⛔ **`description_automation`·`feed_caption_optimization`은 UI에 토글로 나오지 않는다 = API 전용.**
켜져 있는지 담당자가 화면으로 확인할 수 없다. 이 형태에서는 UI에서 볼 수 있는 문구 기능이
`사람마다 문구 최적화` 뿐이다.

**⇒ 실무 권장**: 보이지 않는 AI 생성에 기대는 대신 **본문을 2~3개 직접 넣는다**(최대 5개).
UI에도 그대로 보이고, `text_optimizations`가 그 조합을 사람별로 노출하며, 문구 내용을 우리가 통제한다
(할인율·가격은 `check_landing.py`로 검증된 값만).

⚠ **`standard_enhancements` 자동 추가는 일관되지 않다.** 9개를 같은 요청으로 만들었는데
**8개는 Meta가 자동으로 켰고 1개는 켜지지 않았다**(실측). 지정할 수도 없으니(지원 중단) 이 항목은
**있으면 좋고 없어도 되는 것으로 보고 신경 쓰지 않는다.** 소재별 성능 비교 시 변수로만 기억한다.

### ⛔ 기존 크리에이티브에는 나중에 추가할 수 없다 (실측)

`degrees_of_freedom_spec`은 **생성 시점에만 설정된다.** 만든 뒤 덮어쓰려 하면:
```
크리에이티브 업데이트 실패 —
"크리에이티브를 업데이트하려면 이름, status 또는 연결된 광고 레이블을 지정하세요."
```
즉 `name` · `status` · `adlabels`만 수정 가능하다.
**개선사항을 바꾸려면 크리에이티브를 다시 만들고 광고를 새 크리에이티브로 다시 붙여야 한다.**
(캠페인·광고세트·업로드한 영상은 그대로 재사용 → 소요 1~2분)

## B. 영상 소재에 추가로 켤 수 있는 것 (선택)

| API 키 | 하는 일 | 비고 |
|---|---|---|
| `creative_stickers` | **스티커 CTA** — 영상 위에 CTA 스티커 올림 | 담당자 요청 항목 |
| `add_text_overlay` | 영상 위 텍스트 오버레이 자동 추가 | 소재 위에 글자가 얹힌다 |
| `adapt_to_placement` | 지면(피드·릴스·스토리)에 맞게 비율·구성 자동 조정 | 노출 지면 확대 효과 |
| `video_auto_crop` | 영상 자동 자르기 (지면 비율 맞춤) | |
| `video_uncrop` | 영상 여백 확장 (세로 지면 대응) | |
| `video_highlight` / `video_highlights` | 영상에서 핵심 구간을 뽑아 강조 | 두 키가 별도 존재 |
| `video_filtering` | 영상 필터 적용 | |
| `video_to_image` | 영상에서 정지 이미지 파생 생성 | |
| `audio` | 배경 음원 자동 추가 | 원본 오디오와 충돌 주의 |
| `music` 계열 없음 → `audio` 사용 | | |
| `ig_video_native_subtitle` | 인스타그램 자동 자막 | |
| `ads_with_benefits` | 혜택(배송·할인 등) 배지 노출 | |
| `show_destination_blurbs` | 랜딩 페이지 요약 문구 노출 | |
| `show_summary` | 광고 요약 정보 노출 | |
| `site_extensions` | 사이트 내 하위 링크 확장 노출 | |
| `profile_card` | 프로필 카드 노출 | |
| `generate_cta` | CTA 문구 자동 생성 | `enhance_cta`와 별개 |
| `description_automation` | 설명(description) 자동 생성 | 우리가 직접 쓴 설명과 충돌 가능 |
| `feed_caption_optimization` | 피드 캡션 최적화 | |
| `media_order` | 여러 소재의 노출 순서 자동 결정 | 소재 2개 이상일 때 |
| `media_type_automation` | 미디어 타입 자동 전환(영상↔이미지) | |
| `media_liquidity_animated_image` | 이미지를 움직이는 형태로 변환 | |
| `multi_photo_to_video` | 여러 사진을 영상으로 합성 | 이미지 소재용 |
| `carousel_to_video` | 캐러셀을 영상으로 변환 | 캐러셀용 |
| `replace_media_text` | 소재 안의 글자를 교체 | |
| `hide_price` | 가격 숨김 | |
| `biz_ai` | Meta AI 기반 자동 개선 (범위 광범위) `(?)` | 무엇이 바뀔지 예측 어려움 |
| `advantage_plus_creative` | 어드밴티지+ 크리에이티브 묶음 활성 `(?)` | 개별 기능과 중복 가능 |
| `cv_transformation` | 컴퓨터비전 기반 소재 변환 `(?)` | |
| `pac_recomposition` / `pac_relaxation` | 소재 재구성·제약 완화 `(?)` | |
| `reveal_details_over_time` | (A군 참고) | |
| `enable_ncs_testimonials` | 후기·추천 문구 노출 `(?)` | |
| `text_translation` / `translate_voiceover` | 문구 번역 / 음성 더빙 번역 | 국내 단독 집행이면 불필요 |
| `image_text_translation` | 이미지 내 문구 번역 | 이미지용 |
| `ig_glados_feed` | 인스타그램 특정 지면 대응 `(?)` | |
| `wa_mm_image_filtering` | 왓츠앱 관련 `(?)` | 국내 무관 |

## C. 이미지 소재 전용 (이번 영상 건에는 무관)

`image_animation` · `image_auto_crop` · `image_uncrop` · `image_background_gen` ·
`image_brightness_and_contrast` · `image_enhancement` · `image_templates` · `image_touchups`

## D. 카탈로그 · 앱 · 매장 전용 (판매 영상 광고엔 무관)

`catalog_feed_tag` · `dha_optimization` · `dynamic_partner_content` · `product_extensions` ·
`product_metadata_automation` · `standard_enhancements_catalog` · `app_highlights` ·
`local_store_extension`

---

## 조합 시 주의

- **`description_automation`을 켜면** 우리가 직접 넣은 `descriptions`를 Meta가 바꿀 수 있다. 문구를 고정하고 싶으면 끈다.
- **`add_text_overlay`·`replace_media_text`·`creative_stickers`는 소재 화면을 바꾼다.** 디자이너가 만든 자막·CTA와 겹칠 수 있으니 미리보기로 반드시 확인한다.
- **`audio`는 원본 오디오가 있는 영상에 켜면 어색해질 수 있다.**
- `advantage_plus_creative`·`biz_ai`처럼 범위가 넓은 항목은 개별 기능과 중복될 수 있어, 처음엔 개별 지정을 권한다.
- 켠 뒤에는 **반드시 미리보기(§5-6)로 실제 노출 모습을 확인**한다. 자동 개선은 소재를 실제로 변형한다.
