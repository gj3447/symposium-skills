#!/bin/bash
# dgx_push_when_up.sh — cron: dgx 생존 확인되면 보류 중인 git push 자동 실행 (2026-07-26)
# .0/24 정전으로 dgx bare 푸시가 막힐 때 복구 감지용. up-to-date push는 무해한 no-op.
# 설치: */15 * * * * /bin/bash /Users/lagyeongjun/CD/SYMPOSIUM/bin/dgx_push_when_up.sh
set -u
LOG=/tmp/dgx_push_when_up.log
SYM=/Users/lagyeongjun/CD/SYMPOSIUM

ssh -o BatchMode=yes -o ConnectTimeout=5 dgx true 2>/dev/null || exit 0

cd "$SYM" || exit 1
if [ -n "$(git log origin/main..HEAD --oneline 2>/dev/null)" ]; then
    git push origin main >> "$LOG" 2>&1 \
        && echo "$(date '+%F %T') main pushed to dgx" >> "$LOG"
fi
cd "$SYM/SKILLS" || exit 1
BR=$(git branch --show-current)
if [ -n "$(git log "origin/$BR..HEAD" --oneline 2>/dev/null)" ]; then
    git push origin "$BR" >> "$LOG" 2>&1 \
        && echo "$(date '+%F %T') SKILLS $BR pushed to dgx" >> "$LOG"
fi
exit 0
