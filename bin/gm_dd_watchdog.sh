#!/bin/bash
# gm_dd_watchdog.sh — cron 감시: GM dd 청크 이미지 run 자동 재개 (2026-07-26)
# ① 완료(seal) 감지 시 마커 찍고 종료  ② 실행 중이면 종료  ③ 죽었고 미완료면 keychain sudo로 재기동
# 설치: */20 * * * * /bin/bash /Users/lagyeongjun/CD/SYMPOSIUM/bin/gm_dd_watchdog.sh
set -u

SCRIPT=/Users/lagyeongjun/CD/SYMPOSIUM/bin/gm_dd_chunked.py
RUN_LOG=/tmp/gm_dd_run.log
WLOG=/tmp/gm_dd_watchdog.log
SEAL_MARKER="$HOME/.gm_dd_run/SEALED"
REMOTE_MANIFEST=/srv/dgx4tb/nas/GM_RESCUE_2026/dd/MANIFEST.json
SSH="ssh -i $HOME/.ssh/id_ed25519 -o BatchMode=yes -o ConnectTimeout=8 metahumotonic27@192.168.0.25"

# ① 완료 확인 (로컬 마커 → 원격 seal 순)
[ -f "$SEAL_MARKER" ] && exit 0
if $SSH "test -f $REMOTE_MANIFEST" 2>/dev/null; then
    mkdir -p "$HOME/.gm_dd_run"
    touch "$SEAL_MARKER"
    echo "$(date '+%F %T') SEAL 감지 — 이미지 완료, watchdog 해제" >> "$WLOG"
    exit 0
fi

# ② 실행 중
pgrep -f "gm_dd_chunked.py" >/dev/null && exit 0

# ③ 재기동 — keychain 에서 sudo 비밀번호 조회 (잠겨 있으면 다음 주기로 보류)
PW=$(security find-generic-password -s org.metahumotonic.mac-sudo -w 2>/dev/null)
if [ -z "$PW" ]; then
    echo "$(date '+%F %T') keychain locked — 재기동 보류" >> "$WLOG"
    exit 0
fi
echo "$(date '+%F %T') 프로세스 없음 + 미완료 — 재기동" >> "$WLOG"
printf '%s\n' "$PW" | sudo -S -k nohup python3 "$SCRIPT" >> "$RUN_LOG" 2>&1 &
exit 0
