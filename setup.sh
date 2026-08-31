#!/usr/bin/env bash
# 메타 광고 도구 설치 (macOS / Linux)
#   사용: bash setup.sh
# 하는 일: 파이썬 확인 → 토큰 저장 → 토큰 검증 → 스킬 폴더에 설치
# 광고계정·페이지 설정(config.json)은 Claude가 SETUP.md 보고 진행한다.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

echo ""
echo "  메타 광고 도구 설치"
echo "  ────────────────────────────────"
echo ""

# 1) 파이썬
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then
    if "$c" -c 'import sys; sys.exit(0 if sys.version_info>=(3,8) else 1)' 2>/dev/null; then
      PY="$c"; break
    fi
  fi
done
if [ -z "$PY" ]; then
  echo "  [X] Python 3.8 이상이 필요합니다."
  echo "      https://www.python.org/downloads/ 에서 설치한 뒤"
  echo "      터미널을 새로 열고 다시 실행하세요."
  exit 1
fi
echo "  [O] Python 확인  ($($PY --version 2>&1))"

# 2) 토큰
if [ -s ".token" ]; then
  echo "  [O] 토큰 파일이 이미 있습니다."
  printf "      새 토큰으로 바꾸시겠습니까? (y/N) "
  read -r ANS
  [ "${ANS:-N}" != "y" ] && [ "${ANS:-N}" != "Y" ] && SKIP_TOKEN=1
fi

HAS_TOKEN=0
if [ "${SKIP_TOKEN:-0}" != "1" ]; then
  echo ""
  echo "  메타 액세스 토큰이 있으면 붙여넣고 Enter (Cmd+V)"
  echo "  ※ 없으면 그냥 Enter — 설치를 마친 뒤 Claude가 발급을 도와줍니다"
  printf "  토큰> "
  read -r TOKEN
  TOKEN="$(printf '%s' "$TOKEN" | tr -d '[:space:]')"
  if [ -n "$TOKEN" ]; then
    printf '%s' "$TOKEN" > .token
    chmod 600 .token
    echo "  [O] 토큰 저장 완료"
    HAS_TOKEN=1
  else
    echo "  [-] 토큰 없이 진행합니다 (나중에 Claude가 안내합니다)"
  fi
else
  HAS_TOKEN=1
fi

# 3) 검증 (토큰이 있을 때만)
if [ "$HAS_TOKEN" = "1" ]; then
  echo ""
  "$PY" scripts/setup_wizard.py check || {
    echo ""
    echo "  토큰에 문제가 있지만 설치는 계속합니다."
    echo "  나중에 Claude에게 'SETUP.md 보고 세팅해줘' 라고 하세요."
  }
fi

# 4) 스킬 설치
SKILL_DIR="$HOME/.claude/skills/meta-ad-live"
echo ""
printf "  Claude 스킬로 설치할까요? (Y/n) "
read -r INS
if [ "${INS:-Y}" != "n" ] && [ "${INS:-Y}" != "N" ]; then
  mkdir -p "$HOME/.claude/skills"
  rm -rf "$SKILL_DIR"
  mkdir -p "$SKILL_DIR"
  tar cf - --exclude='__pycache__' --exclude='.git' . | (cd "$SKILL_DIR" && tar xf -)
  echo "  [O] 설치 완료 → $SKILL_DIR"
fi

echo ""
echo "  ────────────────────────────────"
echo "  설치 완료"
echo ""
echo "  다음 단계 — Claude Code를 완전히 껐다 켠 뒤 이렇게 말하세요:"
echo ""
echo "      SETUP.md 보고 세팅해줘"
echo ""
echo "  광고계정·페이지 설정을 Claude가 알아서 진행합니다."
echo ""
