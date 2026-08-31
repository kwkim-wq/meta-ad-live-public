#!/usr/bin/env python3
"""랜딩 페이지 실제 가격·할인율 확인 — 문구에 숫자 쓰기 전에 반드시 돌린다.

⛔ 왜 필요한가 (2026-07-30 실측):
   소재 화면은 "54% 할인", 기존 광고 문구는 "57% 특가", 랜딩 실제는 정가 69,000 → 26,900 = 61%.
   세 숫자가 다 달랐다. 프로모션이 바뀌면 문구가 조용히 허위 표기가 된다.

사용:
  python check_landing.py <랜딩URL>
  python check_landing.py <랜딩URL> --claim 54     # "54% 할인" 이라고 써도 되는지 판정
  python check_landing.py --product <제품명>        # products.json 의 ad_url/url 사용

판정 기준:
  실제 할인율 >= 주장 할인율  →  안전 (실제보다 보수적으로 말하는 것)
  실제 할인율 <  주장 할인율  →  ⛔ 과장. 문구를 고쳐야 한다.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
_SKILL_DIR = os.path.dirname(_HERE)


def fetch(url):
    u = urllib.parse.quote(url, safe=":/?&=%#")
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    try:
        return urllib.request.urlopen(req, timeout=90).read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            sys.exit(f"\n[X] 페이지를 찾을 수 없습니다 (404)\n    {url}\n"
                     "    주소가 맞는지, reference/products.json 의 URL이 맞는지 확인하세요.")
        sys.exit(f"\n[X] 페이지를 열지 못했습니다 (HTTP {e.code})\n    {url}")
    except urllib.error.URLError as e:
        sys.exit(f"\n[X] 페이지에 접속하지 못했습니다.\n    {url}\n"
                 f"    사유: {e.reason}\n    인터넷 연결과 주소를 확인하세요.")
    except Exception as e:
        sys.exit(f"\n[X] 페이지를 읽는 중 오류가 났습니다.\n    {url}\n    {e}")


def num(s):
    try:
        return int(re.sub(r"[^\d]", "", str(s)))
    except Exception:
        return None


def extract(html_text):
    """여러 출처에서 가격을 뽑아 교차 검증한다."""
    out = {"sale": [], "list": [], "percent_on_page": [], "rating": None, "name": None}

    m = re.search(r'<title>(.*?)</title>', html_text, flags=re.S)
    if m:
        out["name"] = re.sub(r"\s+", " ", m.group(1)).strip()

    # 1) meta 태그
    for prop, key in [("product:price:amount", "sale"),
                      ("product:sale_price:amount", "sale")]:
        for v in re.findall(r'<meta[^>]*property="%s"[^>]*content="([^"]+)"' % prop, html_text):
            n = num(v)
            if n:
                out["sale"].append(("meta " + prop, n))

    # 2) ld+json
    for blob in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>',
                           html_text, flags=re.S):
        try:
            d = json.loads(blob.strip())
        except Exception:
            continue
        if isinstance(d, dict) and d.get("@type") == "Product":
            off = d.get("offers") or {}
            if isinstance(off, dict) and off.get("price"):
                n = num(off["price"])
                if n:
                    out["sale"].append(("ld+json offers.price", n))
            ar = d.get("aggregateRating") or {}
            if ar.get("ratingValue"):
                out["rating"] = "%s (리뷰 %s)" % (ar.get("ratingValue"), ar.get("reviewCount"))

    # 3) 본문 표기 (cafe24 기본 마크업)
    flat = re.sub(r"<[^>]+>", " ", html_text)
    flat = re.sub(r"\s+", " ", flat)
    for label, key in [("판매가", "sale"), ("소비자가", "list"), ("정가", "list")]:
        for m in re.finditer(label + r"\s*([\d,]{4,})\s*원", flat):
            n = num(m.group(1))
            if n:
                out[key].append((label + " 표기", n))

    out["percent_on_page"] = sorted(set(re.findall(r"\b(\d{1,2})\s*%", flat)), key=int)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?")
    ap.add_argument("--product", help="products.json 의 제품명으로 URL을 찾는다")
    ap.add_argument("--claim", type=float, help="문구에 쓰려는 할인율(%%)")
    a = ap.parse_args()

    url = a.url
    if a.product:
        products_path = os.path.join(_SKILL_DIR, "reference", "products.json")
        if not os.path.exists(products_path):
            sys.exit("products.json이 없습니다. URL을 직접 넣으세요: python check_landing.py <URL> --claim 54")
        try:
            with open(products_path, encoding="utf-8") as f:
                items = json.load(f)
        except json.JSONDecodeError:
            sys.exit("products.json이 없습니다. URL을 직접 넣으세요: python check_landing.py <URL> --claim 54")
        if not items:
            sys.exit("products.json이 없습니다. URL을 직접 넣으세요: python check_landing.py <URL> --claim 54")
        hit = next((i for i in items if i["name"] == a.product), None)
        if not hit:
            sys.exit("products.json 에 없는 제품: " + a.product)
        url = hit.get("ad_url") or hit["url"]
        print("제품: %s\nURL : %s\n" % (a.product, url))
    if not url:
        sys.exit("URL 또는 --product 를 지정하세요")

    d = extract(fetch(url))
    print("페이지 :", d["name"])
    if d["rating"]:
        print("평점   :", d["rating"])

    def show(key, label):
        if not d[key]:
            print("%s : (찾지 못함)" % label)
            return None
        vals = {}
        for src, n in d[key]:
            vals.setdefault(n, []).append(src)
        print("%s :" % label)
        for n, srcs in sorted(vals.items()):
            print("   %10s원   ← %s" % (format(n, ","), ", ".join(srcs)))
        if len(vals) > 1:
            print("   [!] 값이 여러 개다. 화면을 직접 확인할 것.")
        return max(vals)          # 가장 큰 값을 대표로

    sale = show("sale", "판매가")
    lst = show("list", "정가·소비자가")
    print("페이지 내 % 표기 :",
          ", ".join(x + "%" for x in d["percent_on_page"]) if d["percent_on_page"] else "없음")

    if not sale:
        sys.exit("\n[X] 판매가를 못 찾았습니다. 브라우저로 직접 확인하세요.")

    if lst and lst > sale:
        actual = round((lst - sale) / lst * 100, 1)
        print("\n실제 할인율 = (%s - %s) / %s = **%s%%**" % (
            format(lst, ","), format(sale, ","), format(lst, ","), actual))
    else:
        actual = None
        print("\n정가를 못 찾아 할인율을 계산할 수 없습니다 (판매가 %s원만 확인됨)." %
              format(sale, ","))

    print("\n--- 문구에 쓸 수 있는 검증된 값 ---")
    print("  가격  : %s원" % format(sale, ","))
    if actual is not None:
        print("  할인율: %s%% 이하로만 표기" % actual)

    if a.claim is not None:
        print()
        if actual is None:
            print("[!] 할인율을 계산할 수 없어 '%s%%' 주장을 검증하지 못했습니다." % a.claim)
            sys.exit(1)
        if a.claim <= actual:
            print("[O] '%s%% 할인' 표기 가능 — 실제 %s%% 보다 보수적입니다." % (a.claim, actual))
            sys.exit(0)
        print("[X] '%s%% 할인'은 과장입니다. 실제는 %s%%. 문구를 고치세요." % (a.claim, actual))
        sys.exit(1)


if __name__ == "__main__":
    main()
