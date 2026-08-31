#!/usr/bin/env python3
"""메타 광고 소재 업로드 (이미지/영상) — 로컬에서 바로 실행.

MCP에는 로컬 파일 업로드 도구가 없다(공개 URL만 받는다). 그래서 업로드만 Graph API로 한다.
이미지는 한 번에, 영상은 나눠서 올린다(resumable). 전송 중 끊기면 자동 재시도.

사용:
  python3 upload_media.py 소재.mp4
  python3 upload_media.py 소재1.jpg 소재2.mp4 ...
  python3 upload_media.py 소재폴더/                # ★ 폴더를 주면 안의 소재를 전부 찾는다(하위 폴더까지)
  python3 upload_media.py --scan 소재폴더/         # ★ 업로드 없이 "무엇이 있는지 + 제품 감지"만
  python3 upload_media.py --account <광고계정ID> 소재.mp4
  python3 upload_media.py --json 소재.mp4          # 결과를 JSON으로만 출력(파이프용)

출력: 파일별 media_type / media_id(image_hash 또는 video_id) / 영상은 썸네일 URL까지.

⚠ 폴더를 받으면 **--scan 으로 먼저 확인**하고 담당자에게 보여준 뒤 업로드한다.
   제품이 감지되지 않은 파일(product=null)은 랜딩 URL을 정할 수 없으므로 반드시 물어본다.

⛔ 업로드한 계정 = 광고 만들 계정이어야 한다. 다르면 Meta가 미디어를 못 찾는다.
"""
import argparse
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from config import cfg, cfg_optional, get_token, BASE_URL, API_VERSION  # noqa: E402

_SKILL_DIR = os.path.dirname(_HERE)
CHUNK_SIZE = 4 * 1024 * 1024  # 4MB
VIDEO_EXT = ("mp4", "mov", "avi", "m4v", "webm", "mkv")
IMAGE_EXT = ("jpg", "jpeg", "png", "gif", "webp", "bmp")
MEDIA_EXT = VIDEO_EXT + IMAGE_EXT


def expand_inputs(paths):
    """파일·폴더가 섞인 입력을 '업로드할 소재 파일 목록'으로 펼친다.

    폴더면 하위까지 훑고, 소재가 아닌 파일(psd·txt·엑셀 등)과 macOS 잔재는 건너뛴다.
    반환: (files, skipped) — skipped는 [(경로, 이유)]
    """
    files, skipped = [], []
    for p in paths:
        if not os.path.exists(p):
            skipped.append((p, "경로 없음"))
            continue
        if os.path.isfile(p):
            ext = p.lower().rsplit(".", 1)[-1] if "." in p else ""
            if ext in MEDIA_EXT:
                files.append(p)
            else:
                skipped.append((p, f"소재 아님(.{ext})"))
            continue
        # 폴더
        for root, dirs, names in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d != "__MACOSX" and not d.startswith("."))
            for n in sorted(names):
                if n.startswith("._") or n.startswith("."):
                    continue                       # macOS 리소스 포크·숨김
                full = os.path.join(root, n)
                ext = n.lower().rsplit(".", 1)[-1] if "." in n else ""
                if ext in MEDIA_EXT:
                    files.append(full)
                else:
                    skipped.append((full, f"소재 아님(.{ext})"))
    # 중복 제거(순서 유지)
    seen, uniq = set(), []
    for f in files:
        k = os.path.abspath(f).lower()
        if k not in seen:
            seen.add(k)
            uniq.append(f)
    return uniq, skipped


def _norm(s):
    """비교용 정규화 — 공백·구분자·기호를 없애고 소문자화."""
    return "".join(c for c in s.lower() if c.isalnum())


_PRODUCTS = None


def load_products():
    global _PRODUCTS
    if _PRODUCTS is None:
        path = os.path.join(_SKILL_DIR, "reference", "products.json")
        try:
            with open(path, encoding="utf-8") as f:
                items = json.load(f)
        except Exception:
            items = []
        # 긴 이름 먼저 — 예) '제품A_옵션'이 '제품A'보다 우선 매칭되게
        # ⛔ ad_url(광고 전용 프로모션 페이지)을 반드시 함께 실어야 한다.
        #    빠뜨리면 url(일반 상품페이지)로 폴백해 랜딩이 엉뚱한 제품으로 간다(실측 버그).
        _PRODUCTS = sorted(
            ({"name": i["name"], "url": i["url"], "ad_url": i.get("ad_url"),
              "key": _norm(i["name"])} for i in items),
            key=lambda x: -len(x["key"]))
    return _PRODUCTS


def _lcs_len(a, b):
    """가장 긴 공통 부분문자열 길이 — 제품명 표기가 사람마다 달라도 잡아내기 위해."""
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    best = 0
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                best = max(best, cur[j])
        prev = cur
    return best


def match_product(filename):
    """파일명 앞부분의 제품 표기를 products.json에 등록된 제품 목록에 매핑한다.

    담당자마다 적는 방식이 다르므로(띄어쓰기·줄임말 등 표기 차이)
    정확 일치 → 부분 일치 → 유사도 순으로 넓게 잡고, **애매하면 후보를 돌려준다.**

    반환: {"name","url","ad_url","how","candidates"}  또는  {"name":None,...}
      how = "포함" | "부분일치" | "유사" | None
      candidates 가 2개 이상이면 ⛔ 담당자에게 확인해야 한다.
    """
    stem = os.path.basename(filename)
    stem = stem.rsplit(".", 1)[0] if "." in stem else stem
    key = _norm(stem)
    prods = load_products()

    def pack(p, how, cands=None):
        return {"name": p["name"], "url": p["url"],
                "ad_url": p.get("ad_url") or p["url"],
                "how": how, "candidates": cands or [p["name"]]}

    # 1) 제품명이 파일명에 그대로 들어있다 (긴 이름 우선)
    for p in prods:
        if p["key"] and p["key"] in key:
            return pack(p, "포함")

    # 2) 앞 토큰 기준 부분 일치
    tokens = [t for t in re.split(r"[_\-\s.,()\[\]]+", stem) if t.strip()]
    head = _norm(tokens[0]) if tokens else ""
    if head:
        hits = [p for p in prods if p["key"] and (head in p["key"] or p["key"] in head)]
        if len(hits) == 1:
            return pack(hits[0], "부분일치")
        if len(hits) > 1:
            hits.sort(key=lambda p: -_lcs_len(head, p["key"]))
            return {**pack(hits[0], "부분일치", [p["name"] for p in hits[:4]])}

    # 3) 유사도 (공통 부분문자열 3자 이상)
    scored = sorted(((_lcs_len(head or key, p["key"]), p) for p in prods),
                    key=lambda x: -x[0])
    if scored and scored[0][0] >= 3:
        top = [p["name"] for s, p in scored if s == scored[0][0]][:4]
        return {**pack(scored[0][1], "유사", top)}

    return {"name": None, "url": None, "ad_url": None, "how": None, "candidates": []}


def detect_product(filename):
    """하위 호환 — match_product의 축약형."""
    m = match_product(filename)
    return m if m["name"] else None


# 소구점으로 쓸 수 없는 토큰 — 이게 남으면 파일명이 잘못 적힌 것이다
_MEANINGLESS = {
    "신규소재", "기존소재", "신규", "기존", "소재", "영상", "이미지", "동영상", "썸네일",
    "최종", "최종본", "파이널", "수정", "수정본", "편집", "사본", "복사", "완료",
    "copy", "final", "fin", "ver", "version", "test", "테스트", "샘플", "sample",
    "무제", "untitled", "new", "old", "raw", "원본", "출력", "export", "render",
}
_JUNK_RE = re.compile(r"^(v?\d+%?|\d{4,8}|\d+화|\d+차)$", re.I)


def detect_point(filename, product_name=None):
    """파일명에서 소구점을 뽑는다. 못 뽑으면 None (→ 파일명을 고쳐달라고 해야 한다).

    광고명·utm_content에 그대로 들어가므로 짧고 의미 있는 한 단어여야 한다.
    """
    stem = os.path.basename(filename)
    stem = stem.rsplit(".", 1)[0] if "." in stem else stem
    prod_key = _norm(product_name) if product_name else ""
    out = []
    for tok in re.split(r"[_\-\s.,()\[\]]+", stem):
        tok = tok.strip()
        if not tok:
            continue
        n = _norm(tok)
        if not n:
            continue
        if prod_key and (n in prod_key or prod_key in n):
            continue                        # 제품명 조각
        if tok.lower() in _MEANINGLESS or n in _MEANINGLESS:
            continue
        if _JUNK_RE.match(tok):
            continue                        # 01, v2, 260730, 14차, 54% 등
        out.append(tok)
    return out[0] if out else None


def name_issues(match, point):
    """파일명이 규칙(§4-1)을 지켰는지. 반환: 문제 목록(빈 리스트면 정상).

    번호·특수문자·공백은 문제로 보지 않는다 — 번호는 도구가 붙이고,
    나머지는 도구가 정리해서 광고명을 다시 쓴다. **필수는 제품 표기 + 소구점 2개뿐.**
    """
    issues = []
    if not match or not match.get("name"):
        issues.append("제품 표기 없음")
    elif len(match.get("candidates") or []) > 1:
        issues.append("제품 후보 %d개 → 확인 필요" % len(match["candidates"]))
    if not point:
        issues.append("소구점 없음")
    return issues


NAME_RULE = """  ── 소재 파일명 규칙 ──────────────────────────────
  제품명_소구점.mp4            예)  제품A_발바닥.mp4
                                    제품A_품절대란.mp4
                                    제품B_속근육지압.mp4
    · 제품   : 앞에 제품명만 넣으면 된다. 표기가 조금 달라도 자동 매핑한다
               (products.json에 등록된 제품명 기준, 띄어쓰기·줄임말 허용)
               ⛔ 단, 매핑 결과는 담당자에게 확인받고 진행한다
    · 소구점 : 이 소재가 무엇으로 설득하는지 한 단어 (2~6자)
               광고명·utm_content에 그대로 들어가 매출 귀인 키가 된다
               예) 발바닥 · 붓기 · 품절대란 · 마감임박 · 후기
    · 번호   : 넣지 않아도 된다. 도구가 1부터 자동으로 붙인다
    · 공백·특수문자·날짜는 있어도 된다 — 도구가 정리해서 광고명을 다시 쓴다
    · 피할 것: '신규소재_1', '최종', '사본', '수정본' 처럼 소구점을 알 수 없는 이름
  ────────────────────────────────────────────────"""


def scan(paths):
    """업로드 없이 목록·미디어타입·감지된 제품을 만든다."""
    files, skipped = expand_inputs(paths)
    rows = []
    for f in files:
        ext = f.lower().rsplit(".", 1)[-1]
        m = match_product(f)
        point = detect_point(f, m["name"])
        rows.append({
            "file": os.path.basename(f),
            "path": os.path.abspath(f),
            "media_type": "영상" if ext in VIDEO_EXT else "이미지",
            "size_mb": round(os.path.getsize(f) / 1024 / 1024, 2),
            "product": m["name"],
            "product_match": m["how"],
            "product_candidates": m["candidates"],
            "landing_url": m["ad_url"],
            "소구점": point,
            "ad_name": None,
            "name_issues": name_issues(m, point),
        })
    # 광고명 번호는 도구가 붙인다 — 판정 통과한 소재만 1부터 연속으로
    n = 0
    for r in rows:
        if r["product"] and r["소구점"]:
            n += 1
            r["ad_name"] = "%s_%s_%s_일반_%d" % (
                r["product"], r["media_type"], r["소구점"], n)
    return rows, skipped


def print_scan(rows, skipped):
    if not rows:
        print("소재를 찾지 못했습니다.", file=sys.stderr)
    else:
        print("\n찾은 소재 %d개" % len(rows), file=sys.stderr)
        print("-" * 92, file=sys.stderr)
        print("  %-28s %-5s %6s  %-14s %-9s %s" % (
            "파일", "종류", "MB", "제품(매핑)", "소구점", "판정"), file=sys.stderr)
        for r in rows:
            name = r["file"] if len(r["file"]) <= 28 else r["file"][:25] + "..."
            prod = (r["product"] or "???")
            if r["product"] and r["product_match"] != "포함":
                prod += "*"
            print("  %-28s %-5s %6.2f  %-14s %-9s %s" % (
                name, r["media_type"], r["size_mb"], prod, r["소구점"] or "???",
                "OK" if not r["name_issues"] else "⚠ " + ", ".join(r["name_issues"])),
                file=sys.stderr)

        # ⛔ 제품 매핑 확인 절차 — 파일명 표기를 그대로 쓰지 않고 다시 쓴 경우
        rewritten = [r for r in rows if r["product"] and r["product_match"] != "포함"]
        if rewritten:
            print("\n⛔ 제품명을 이렇게 매핑했습니다 — **담당자에게 맞는지 확인받고 진행할 것**",
                  file=sys.stderr)
            for r in rewritten:
                cands = r["product_candidates"]
                extra = ("   (다른 후보: %s)" % " / ".join(c for c in cands if c != r["product"])
                         if len(cands) > 1 else "")
                print("    %-30s → %s   [%s]%s" % (
                    r["file"], r["product"], r["product_match"], extra), file=sys.stderr)

        named = [r for r in rows if r["ad_name"]]
        if named:
            print("\n생성될 광고명 (번호는 자동 부여):", file=sys.stderr)
            for r in named:
                print("    %s" % r["ad_name"], file=sys.stderr)

        bad = [r for r in rows if r["name_issues"]]
        if bad:
            print("\n⛔ 파일명이 규칙에 맞지 않는 소재 %d개 — **담당자에게 파일명을 고쳐 달라고 요청할 것**"
                  % len(bad), file=sys.stderr)
            for r in bad:
                print("    - %-34s %s" % (r["file"], ", ".join(r["name_issues"])), file=sys.stderr)
            print(file=sys.stderr)
            print(NAME_RULE, file=sys.stderr)
            print("\n  담당자가 '그냥 진행해라' 하면: 제품·소구점을 직접 물어보거나"
                  "\n  썸네일을 열어 내용을 확인한 뒤 진행한다(SKILL.md §7-0-2).", file=sys.stderr)
    if skipped:
        print("\n건너뜀 %d개 (소재 아님):" % len(skipped), file=sys.stderr)
        for p, why in skipped[:20]:
            print("    - %s  [%s]" % (os.path.basename(p), why), file=sys.stderr)
        if len(skipped) > 20:
            print("    ... 외 %d개" % (len(skipped) - 20), file=sys.stderr)
    print("", file=sys.stderr)


def _multipart(fields: dict, file_field=None, file_bytes=None, filename=None):
    boundary = "----MetaUploadBoundary7MA4YWxkTrZu0gW"
    parts = []
    for k, v in fields.items():
        parts.append(f"--{boundary}\r\n"
                     f'Content-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n')
    body = "".join(parts).encode()
    if file_field and file_bytes is not None:
        head = (f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'
                f"Content-Type: application/octet-stream\r\n\r\n").encode()
        body += head + file_bytes + f"\r\n--{boundary}--\r\n".encode()
    else:
        body += f"--{boundary}--\r\n".encode()
    return body, boundary


def _post_multipart(url, body, boundary, timeout=180, retries=4):
    """POST. 네트워크가 끊기면(Meta가 대용량 업로드 중 연결을 리셋한다) 재시도한다.

    ⛔ 실측: 12MB 영상 48% 지점에서 WinError 10054(연결 강제 종료) 발생.
       재시도 없이는 스크립트가 죽고 나머지 소재도 못 올린다.
    """
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:          # API가 응답한 에러 — 재시도 무의미
            try:
                return json.loads(e.read())
            except Exception:
                return {"error": {"message": str(e)}}
        except (urllib.error.URLError, OSError, ConnectionError) as e:
            last = e
            if attempt < retries - 1:
                wait = 2 ** attempt                   # 1, 2, 4, 8초
                sys.stderr.write(f"\n  ⚠ 네트워크 끊김({e}) — {wait}초 후 재시도 "
                                 f"{attempt + 1}/{retries - 1}\n")
                sys.stderr.flush()
                time.sleep(wait)
    return {"error": {"message": f"네트워크 재시도 {retries}회 실패: {last}"}}


def upload_image(path, account, token):
    with open(path, "rb") as f:
        data = f.read()
    body, b = _multipart({"access_token": token}, "filename", data, os.path.basename(path))
    res = _post_multipart(f"{BASE_URL}/{account}/adimages", body, b)
    images = res.get("images", {})
    if images:
        first = list(images.values())[0]
        return {"ok": True, "media_type": "이미지", "media_id": first["hash"]}
    return {"ok": False, "error": res}


def upload_video(path, account, token):
    size = os.path.getsize(path)
    name = os.path.basename(path)
    url = f"{BASE_URL}/{account}/advideos"

    body, b = _multipart({"upload_phase": "start", "file_size": str(size),
                          "name": name, "access_token": token})
    start = _post_multipart(url, body, b)
    vid, sess = start.get("video_id"), start.get("upload_session_id")
    if not vid or not sess:
        return {"ok": False, "error": start}

    start_off = int(start.get("start_offset", 0))
    end_off = int(start.get("end_offset", min(CHUNK_SIZE, size)))
    with open(path, "rb") as f:
        raw = f.read()

    while start_off < size:
        chunk = raw[start_off:end_off]
        body, b = _multipart(
            {"upload_phase": "transfer", "upload_session_id": sess,
             "start_offset": str(start_off), "end_offset": str(end_off),
             "access_token": token},
            "video_file_chunk", chunk, name)
        res = _post_multipart(url, body, b)
        if "error" in res:
            return {"ok": False, "error": res}
        nxt = int(res.get("start_offset", end_off))
        sys.stderr.write(f"\r  업로드 {min(nxt,size)*100//size}% ({min(nxt,size):,}/{size:,} bytes)")
        sys.stderr.flush()
        if nxt >= size:
            break
        start_off = nxt
        end_off = int(res.get("end_offset", min(nxt + CHUNK_SIZE, size)))
    sys.stderr.write("\n")

    body, b = _multipart({"upload_phase": "finish", "upload_session_id": sess,
                          "access_token": token})
    fin = _post_multipart(url, body, b)
    if not fin.get("success"):
        return {"ok": False, "error": fin}
    return {"ok": True, "media_type": "영상", "media_id": vid}


def get_video_thumbnail(video_id, token, retries=15, wait=4):
    """영상 커버 이미지 URL. ads_create_creative의 image_url(비디오 썸네일)에 필요.

    ⛔ 업로드 직후에는 썸네일이 **없다** — Meta가 인코딩을 끝내야 생긴다.
       실측: 업로드 직후 0개 → `status.video_status: ready` 이후 11~14개.
       그래서 준비될 때까지 기다린다(최대 retries×wait초).
    """
    waited = False
    for attempt in range(retries):
        try:
            u = f"{BASE_URL}/{video_id}?fields=thumbnails,status&access_token={token}"
            with urllib.request.urlopen(u, timeout=60) as r:
                d = json.loads(r.read())
        except Exception:
            d = {}
        lst = (d.get("thumbnails") or {}).get("data", [])
        if lst:
            if waited:
                sys.stderr.write("\n")
            pref = next((t for t in lst if t.get("is_preferred")), lst[0])
            return pref.get("uri") or pref.get("url")
        if attempt < retries - 1:
            waited = True
            sys.stderr.write("\r  썸네일 생성 대기... %d초 (video_status=%s)" % (
                (attempt + 1) * wait, (d.get("status") or {}).get("video_status", "?")))
            sys.stderr.flush()
            time.sleep(wait)
    sys.stderr.write("\n  ⚠ 썸네일을 아직 못 받았습니다. 몇 분 뒤 아래로 다시 받으세요:\n"
                     "     python upload_media.py --thumbs %s\n" % video_id)
    return None


def main():
    ap = argparse.ArgumentParser(description="메타 광고 소재 업로드")
    ap.add_argument("files", nargs="*", help="이미지/영상 파일 또는 폴더 (폴더는 하위까지 훑는다)")
    ap.add_argument("--account", default=None,
                    help="광고계정 숫자ID (미지정 시 config.json의 default_account_id 사용)")
    ap.add_argument("--json", action="store_true", help="JSON만 출력")
    ap.add_argument("--scan", action="store_true",
                    help="업로드하지 않고 목록·미디어타입·감지된 제품만 보여준다")
    ap.add_argument("--thumbs", nargs="+", metavar="VIDEO_ID",
                    help="이미 올린 영상의 썸네일 URL만 다시 받는다(인코딩 대기 후 복구용)")
    a = ap.parse_args()

    # ---- 썸네일만 다시 받기 ----
    if a.thumbs:
        token = get_token()
        out = []
        for vid in a.thumbs:
            url = get_video_thumbnail(vid, token)
            out.append({"video_id": vid, "thumbnail_url": url})
            print("  %s : %s" % (vid, "OK" if url else "없음"), file=sys.stderr)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        sys.exit(0 if all(o["thumbnail_url"] for o in out) else 1)

    if not a.files:
        ap.error("소재 파일 또는 폴더를 지정하세요 (또는 --thumbs <video_id ...>)")

    # ---- 파일·폴더 펼치기 (폴더 지원) ----
    rows, skipped = scan(a.files)
    if not a.json:
        print_scan(rows, skipped)

    if a.scan:
        print(json.dumps({"media": rows,
                          "skipped": [{"path": p, "reason": w} for p, w in skipped]},
                         ensure_ascii=False, indent=2))
        sys.exit(0 if rows else 1)

    if not rows:
        print(json.dumps([], ensure_ascii=False))
        sys.exit(1)

    token = get_token()
    account_id = a.account or cfg("default_account_id")
    acct = account_id if account_id.startswith("act_") else "act_" + account_id
    results = []

    for i, row in enumerate(rows, 1):
        path = row["path"]
        is_video = row["media_type"] == "영상"
        print(f"[{i}/{len(rows)}] {row['file']} ({row['size_mb']}MB) 업로드 중...",
              file=sys.stderr)
        # 한 파일이 죽어도 나머지는 계속 올린다
        try:
            r = upload_video(path, acct, token) if is_video else upload_image(path, acct, token)
        except Exception as e:
            r = {"ok": False, "error": {"message": f"예외: {type(e).__name__}: {e}"}}
        r["file"] = row["file"]
        r["path"] = path
        r["product"] = row["product"]
        r["landing_url"] = row["landing_url"]
        r["소구점"] = row["소구점"]
        r["ad_name"] = row["ad_name"]
        r["account_id"] = acct.replace("act_", "")
        if r.get("ok") and is_video:
            r["thumbnail_url"] = get_video_thumbnail(r["media_id"], token)
        results.append(r)
        if r.get("ok"):
            print(f"  ✅ {r['media_type']} media_id={r['media_id']}", file=sys.stderr)
        else:
            print(f"  ❌ 실패: {json.dumps(r.get('error'), ensure_ascii=False)[:300]}",
                  file=sys.stderr)

    print(json.dumps(results, ensure_ascii=False, indent=2))
    sys.exit(0 if all(r.get("ok") for r in results) else 1)


if __name__ == "__main__":
    main()
