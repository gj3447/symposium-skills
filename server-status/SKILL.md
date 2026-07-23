---
name: server-status
kg_ref: ATOM_Skill_server_status
version: "2.0.0"
channel: stable
description: >
  비행기맨 서버 상태 점검. Mac=gateway, DGX=server. Docker Desktop 없음.
  kubectl + localhost(socat) + ssh dgx 로 점검.
---

# 비행기맨 서버 상태 점검 (v2)

정본: `~/CD/SERVER/05_DOCS/BHGMAN_SERVER_ARCHITECTURE.md`  
**Mac에 Docker 설치/기동하지 말 것.** 무거운 서비스는 전부 DGX.

## 1. k8s (DGX)
```bash
kubectl get nodes -o wide
kubectl get pods -A | grep -vE 'Completed|0/'
# fallback
~/CD/SERVER/03_SCRIPTS/bin/kubectl-dgx get pods -n data
```

## 2. DB 접속 (Mac localhost = socat → DGX)
- Neo4j: `cypher-shell -a bolt://127.0.0.1:7687 -u neo4j -p neo4jpassword 'RETURN "OK"'`
- Redis: `redis-cli -h 127.0.0.1 -a redispassword PING`
- Mongo: `mongosh 'mongodb://127.0.0.1:27017' --quiet --eval 'db.runCommand({ping:1}).ok'`
- MinIO: `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:9000/minio/health/live`
- Postgres: `ssh dgx 'sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl exec -n data postgresql-0 -- psql -U postgres -d maindb -tAc "SELECT 1"'`
- Prometheus: `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:9090/-/healthy`
- Grafana: `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3000/login`

## 3. socat 게이트웨이 + 워치독
```bash
lsof -nP -iTCP:7687,7474,5432,6379,27017,9000,9001,6443,9090,3000 -sTCP:LISTEN
# 수동 재기동
nohup bash ~/CD/SERVER/03_SCRIPTS/launchd/start-user-socat.sh &
# 워치독 (60s, auto-heal)
launchctl print gui/$(id -u)/com.metahumotonic.watchdog | head
tail -20 ~/Library/Logs/metahumotonic-watchdog.log
```

## 4. 외부 / 도메인
- `curl -s -o /dev/null -w '%{http_code}\n' https://metahumotonic.com/infra/`
- `bhgman.iptime.org` 는 DDNS fallback only

## 5. 스토리지 (DGX)
```bash
ssh dgx 'df -h / /mnt/ext4'
```

## 6. Mac 로컬 (가벼움만)
```bash
# 무거운 DB launchd 가 disabled 인지
ls ~/Library/LaunchAgents/*disabled* | grep -iE 'neo4j|mongo|postgres|redis|traefik'
# Docker 없어야 정상
command -v docker || echo 'docker: not installed (expected)'
```

결과를 테이블로 정리.

# KG: ATOM_Skill_server_status
# KG: bhgman-server-architecture-2026-07-15
