# ============================================================
#  meta-ad-live 설치 (Windows)
#
#  실행 방법 — 아래 둘 중 하나
#   1) 이 파일 우클릭 → "PowerShell에서 실행"
#   2) 터미널에서:  powershell -ExecutionPolicy Bypass -File setup.ps1
#
#  하는 일: Python 확인 → 토큰 검증 → 스킬 폴더로 설치 → 연결 확인
#  걸리는 시간: 1분 (토큰 붙여넣기 1회)
# ============================================================
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

$src  = $PSScriptRoot
$dest = Join-Path $env:USERPROFILE ".claude\skills\meta-ad-live"

function Say($m, $c = 'Gray') { Write-Host $m -ForegroundColor $c }
function Die($m) { Say "`n[X] $m" 'Red'; Say "설치를 중단했습니다.`n" 'Red'; exit 1 }

Say ""
Say "============================================" 'Cyan'
Say "  meta-ad-live 설치" 'Cyan'
Say "============================================" 'Cyan'

# ---------- 1. Python ----------
Say "`n[1/5] Python 확인"
$py = $null
foreach ($c in 'python', 'python3') {
    if (Get-Command $c -ErrorAction SilentlyContinue) {
        $v = & $c --version 2>&1
        if ($LASTEXITCODE -eq 0 -and "$v" -match 'Python 3') { $py = $c; Say "  [O] $v ($c)" 'Green'; break }
    }
}
if (-not $py) {
    Die @"
Python 3 이 없습니다.
  https://www.python.org/downloads/ 에서 설치하세요.
  설치 화면에서 'Add python.exe to PATH' 를 반드시 체크하고,
  설치 후 터미널을 새로 열어 이 스크립트를 다시 실행하세요.
"@
}

# ---------- 2. 토큰 입력 ----------
Say "`n[2/5] 메타 액세스 토큰"
$bundled = Join-Path $src ".token"
$isBundled = $false
if (Test-Path $bundled) {
    $token = (Get-Content -Raw $bundled).Trim()
    $isBundled = $true
    Say "  이 폴더에 포함된 토큰 사용 (.token) — 붙여넣기 불필요"
} elseif ($env:META_MCP_TOKEN) {
    $token = $env:META_MCP_TOKEN.Trim()
    Say "  환경변수 META_MCP_TOKEN 사용"
} else {
    Say "  메타 액세스 토큰(EAA... 로 시작하는 긴 문자열)이 있으면 붙여넣고 Enter." 'Yellow'
    Say "  ※ 없으면 그냥 Enter - 설치를 마친 뒤 Claude가 발급을 도와줍니다." 'Cyan'
    Say "  (붙여넣기: 마우스 우클릭 또는 Ctrl+V)" 'DarkGray'
    Write-Host "  토큰> " -NoNewline -ForegroundColor Yellow
    $token = (Read-Host).Trim()
}

# 토큰 없이도 설치는 계속한다 (Claude가 나중에 SETUP.md 보고 발급을 안내한다)
$hasToken = -not [string]::IsNullOrWhiteSpace($token)
if ($hasToken) {
    $token = $token.Trim('"').Trim("'").Trim()
    if ($token.Length -lt 50) {
        Say "  [!] 토큰이 너무 짧습니다($($token.Length)자). 중간이 잘렸을 수 있습니다." 'Yellow'
        Say "      일단 설치를 계속하고, 나중에 Claude에게 다시 받으세요." 'DarkGray'
        $hasToken = $false; $token = ''
    } elseif (-not $token.StartsWith('EAA')) {
        Say "  [!] 보통 EAA 로 시작합니다. 잘못 복사했는지 확인하세요." 'Yellow'
    }
} else {
    Say "  [-] 토큰 없이 진행합니다. 설치 후 Claude에게 'SETUP.md 보고 세팅해줘' 라고 하세요." 'Cyan'
}

# ---------- 3. 토큰 검증 ----------
Say "`n[3/5] 토큰 검증 (메타에 조회)"
if ($hasToken) {
    $env:META_MCP_TOKEN = $token
    & $py (Join-Path $src "scripts\setup_wizard.py") check
    if ($LASTEXITCODE -ne 0) {
        Say "  [!] 토큰에 문제가 있지만 설치는 계속합니다." 'Yellow'
        Say "      설치 후 Claude에게 'SETUP.md 보고 세팅해줘' 라고 하세요." 'Cyan'
    }
} else {
    Say "  건너뜀 (토큰 없음)" 'DarkGray'
}

# ---------- 4. 설치 ----------
Say "`n[4/5] 스킬 폴더로 설치"
Say "  $dest" 'DarkGray'
if (Test-Path $dest) {
    Remove-Item -Recurse -Force $dest
    Say "  기존 설치를 덮어씁니다."
}
New-Item -ItemType Directory -Force -Path $dest | Out-Null
foreach ($item in 'SKILL.md', 'README.md', 'reference', 'scripts') {
    $p = Join-Path $src $item
    if (Test-Path $p) { Copy-Item $p $dest -Recurse -Force }
}
Get-ChildItem $dest -Recurse -Force -Directory -Filter '__pycache__' |
    ForEach-Object { Remove-Item -Recurse -Force $_.FullName }

# SETUP.md 도 함께 복사 (Claude가 이걸 보고 세팅한다)
foreach ($item in 'SETUP.md', 'setup.ps1', 'setup.sh') {
    $p = Join-Path $src $item
    if (Test-Path $p) { Copy-Item $p $dest -Force }
}

# .token 은 설치된 폴더에만 쓴다 (BOM 없이 — BOM이 붙으면 인증이 깨진다).
# 배포 폴더에는 남기지 않는다 → 이 폴더를 그대로 다시 전달해도 토큰이 새지 않는다.
if ($hasToken) {
    $tokenPath = Join-Path $dest ".token"
    [System.IO.File]::WriteAllText($tokenPath, $token, (New-Object System.Text.UTF8Encoding($false)))
    Say "  [O] 파일 복사 + 토큰 저장 완료" 'Green'
} else {
    Say "  [O] 파일 복사 완료 (토큰은 나중에 Claude가 저장합니다)" 'Green'
}

# ---------- 5. 연결 확인 ----------
Say "`n[5/5] 실제 연결 확인"
Remove-Item Env:\META_MCP_TOKEN -ErrorAction SilentlyContinue   # .token 경로로 읽히는지 함께 확인
if ($hasToken) {
    $tools = & $py (Join-Path $dest "scripts\mcp.py") tools
    if ($LASTEXITCODE -ne 0) {
        Say "  [!] MCP 서버에 연결되지 않았습니다." 'Yellow'
        Say "      광고 제작은 Graph API 경로로 그대로 가능합니다 (미리보기 기능만 제외)." 'DarkGray'
    } else {
        $n = ($tools | Measure-Object -Line).Lines
        Say "  [O] 도구 $n 개 응답 — 연결 정상" 'Green'
    }
} else {
    Say "  건너뜀 (토큰 없음)" 'DarkGray'
}

# ---------- 끝 ----------
if ($isBundled) {
    $tokenNote = @"
  - ⛔ 이 폴더(압축 푼 폴더)에 토큰이 들어 있습니다.
    다른 사람에게 그대로 넘기지 마세요. 필요하면 관리자에게 받게 하세요.
"@
} else {
    $tokenNote = @"
  - 이 폴더(설치 원본)에는 토큰이 저장되지 않았습니다. 그대로 다시 전달해도 안전합니다.
  - 토큰은 사내 공유 위치에서만 받으세요. 외부로 보내면 광고비가 오집행될 수 있습니다.
"@
}
Say ""
Say "============================================" 'Green'
Say "  설치 완료" 'Green'
Say "============================================" 'Green'
Say @"

다음 할 일
  1. Claude Code 를 완전히 닫고 다시 엽니다.  ← 안 하면 스킬이 안 잡힙니다
  2. Claude Code 에 이렇게 말합니다:

       SETUP.md 보고 세팅해줘

     → 광고계정·페이지·픽셀을 Claude 가 찾아서 설정해 줍니다 (한 번만 하면 됩니다)

  3. 세팅이 끝나면, 소재(영상·이미지)가 든 폴더를 주면서 이렇게 말하면 됩니다:

       이 폴더 소재로 광고 만들어줘  (폴더 경로 첨부)

  광고는 전부 PAUSED(꺼진 상태)로 만들어지고,
  라이브(과금 시작) 직전에 요약을 보여주고 확인을 받습니다.

주의
  - 일예산 기본값 100,000원. 다르면 말할 때 같이 알려주세요.
$tokenNote
"@ 'White'
