---
name: db-query
kg_ref: ATOM_Skill_db_query
version: "2.0.0"
channel: stable
defer_loading: true
optional_mcp_tools:
  mongodb:
    mcp__mongodb__find:                 "MongoDB document query / 컬렉션 조회"
    mcp__mongodb__aggregate:            "MongoDB aggregation pipeline 실행"
    mcp__mongodb__count:                "MongoDB document count"
    mcp__mongodb__collection-schema:    "MongoDB collection schema inspection"
    mcp__mongodb__collection-indexes:   "MongoDB index 조사"
    mcp__mongodb__list-collections:     "MongoDB collection listing"
    mcp__mongodb__list-databases:       "MongoDB DB listing"
    mcp__mongodb__insert-many:          "MongoDB bulk insert (WRITE — user confirm)"
    mcp__mongodb__update-many:          "MongoDB bulk update (WRITE — user confirm)"
    mcp__mongodb__delete-many:          "MongoDB bulk delete (WRITE — user confirm)"
    mcp__mongodb__explain:              "MongoDB query plan inspection"
  postgres:
    mcp__postgres__execute_sql:         "PostgreSQL query 실행"
    mcp__postgres__explain_query:       "Postgres EXPLAIN ANALYZE"
    mcp__postgres__list_schemas:        "Postgres schema listing"
    mcp__postgres__list_objects:        "Postgres table/view/index listing"
    mcp__postgres__get_object_details:  "Postgres object 상세 (column / constraint)"
    mcp__postgres__get_top_queries:     "Postgres pg_stat_statements top N"
    mcp__postgres__analyze_db_health:   "Postgres health check (bloat / vacuum / etc.)"
    mcp__postgres__analyze_query_indexes:    "Postgres single-query index advisor"
    mcp__postgres__analyze_workload_indexes: "Postgres workload-level index advisor"
  redis:
    mcp__redis__get:                    "Redis string GET"
    mcp__redis__set:                    "Redis string SET (WRITE)"
    mcp__redis__hgetall:                "Redis hash 전체 조회"
    mcp__redis__hget:                   "Redis hash field 조회"
    mcp__redis__hset:                   "Redis hash field SET (WRITE)"
    mcp__redis__lrange:                 "Redis list 범위 조회"
    mcp__redis__zrange:                 "Redis sorted set 범위 조회"
    mcp__redis__scan_keys:              "Redis key 패턴 탐색"
    mcp__redis__info:                   "Redis 서버 INFO"
    mcp__redis__dbsize:                 "Redis DB key 개수"
    mcp__redis__vector_search_hash:     "Redis vector similarity search"
    mcp__redis__hybrid_search:          "Redis hybrid (vector + text) search"
  neo4j:
    mcp__neo4j__read_neo4j_cypher:      "Neo4j read-only Cypher (KG 조회 default)"
    mcp__neo4j__write_neo4j_cypher:     "Neo4j write Cypher (CREATE/MERGE/SET — user confirm)"
    mcp__neo4j__get_neo4j_schema:       "Neo4j schema (label / rel / property)"
description: >-
  Query Bihaenggiman databases on VM200 data-01 (192.168.0.25) through approved endpoints from any gateway node (dev-01 canonical / Mac), never a local Docker host. Use when: reading or safely updating Neo4j, PostgreSQL, MongoDB, Redis, or related server data. Do not use when: the goal is health inspection, backup, or Kafka administration rather than a database query; use `$server-status`, `$backup`, or `$kafka-manage` instead.
---

# DB 쿼리 실행 (v3 — VM200 정본, 2026-08-10 dev-01 이관 반영)

## 아키텍처 (절대 잊지 말 것)

```
DB 실체   = Proxmox VM200 data-01 @ 192.168.0.25 (2026-07-19 4TB 컷오버로 DGX k8s에서 이사)
게이트웨이 = dev-01 (canonical) / Mac (지휘·읽기) — 둘 다 thin client, DB 서버 기동 금지
클라이언트 → localhost:PORT (각 노드 socat → 192.168.0.25) 또는 192.168.0.25:PORT 직결
정본: ~/CD/SERVER/05_DOCS/BHGMAN_SERVER_ARCHITECTURE.md (SERVER는 gj3447/SERVER repo)
```

**금지**
- `docker exec …` (게이트웨이 노드에 docker 없음)
- 게이트웨이 노드에 Neo4j/Postgres/Mongo/Redis 서버 기동
- Multipass `192.168.2.2` / 옛 k8s-cp / **DGX NodePort(30687 등) 가정 — 2026-07-19 이후 폐기, 실측 CLOSED**

**허용 경로 (우선순위)**
1. MCP tools (`mcp__neo4j__*`, `mcp__postgres__*`, …)
2. CLI → `localhost` (socat 경유) 또는 `192.168.0.25` 직결 — cypher-shell 없으면 HTTP API(`:7474/db/neo4j/tx/commit`)
3. `ssh dgx` + `kubectl exec -n data …` (레거시 디버그 전용 — DB 본체는 더 이상 DGX에 없음)

---

## ToolSearch 패턴

| 요청 | ToolSearch |
|---|---|
| Neo4j Cypher | `select:mcp__neo4j__read_neo4j_cypher` |
| Postgres SQL | `select:mcp__postgres__execute_sql` |
| Mongo find | `+mongodb find` |
| Redis keys | `select:mcp__redis__scan_keys` |

WRITE 도구는 사용자 확인 후에만.

---

## 사용 가능한 DB

### Neo4j (APT KG 정본)
```bash
# Mac (socat → DGX 30687)
cypher-shell -a bolt://127.0.0.1:7687 -u neo4j -p neo4jpassword 'RETURN 1'
# 또는 HTTP
curl -s -u neo4j:neo4jpassword -H 'Content-Type: application/json' \
  -d '{"statements":[{"statement":"MATCH (n) RETURN count(n) AS c"}]}' \
  http://127.0.0.1:7474/db/neo4j/tx/commit
# DGX 직접
ssh dgx 'sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl exec -n data neo4j-0 -- cypher-shell -u neo4j -p neo4jpassword "RETURN 1"'
```
- bolt://localhost:7687 · http://localhost:7474

### PostgreSQL
```bash
# Mac에 psql 있으면
psql "host=127.0.0.1 port=5432 user=postgres dbname=maindb" -c 'SELECT 1'
# 없으면 DGX
ssh dgx 'sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl exec -n data postgresql-0 -- psql -U postgres -d maindb -c "SELECT 1"'
```
- DBs: `postgres`, `maindb`, `n8n`, `memos_note`, `metahumotonic_memo`
- NodePort 30432 → localhost:5432

### MongoDB
```bash
mongosh 'mongodb://127.0.0.1:27017' --eval 'db.runCommand({ping:1})'
# 또는
ssh dgx 'sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl exec -n data mongodb-0 -- mongosh --quiet --eval "db.runCommand({ping:1})"'
```

### Redis
```bash
redis-cli -h 127.0.0.1 -p 6379 PING
ssh dgx 'sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl exec -n data redis-0 -- redis-cli PING'
```

### MinIO
```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9000/minio/health/live
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9001/
```

---

## socat / kubectl 복구

```bash
# 포트 포워드 재기동
bash ~/CD/SERVER/03_SCRIPTS/launchd/start-user-socat.sh &
# 또는 launchctl kickstart -k gui/$(id -u)/com.metahumotonic.port-forwarding

# k8s
kubectl get nodes                    # via 127.0.0.1:6443 socat
~/CD/SERVER/03_SCRIPTS/bin/kubectl-dgx get pods -n data
```

## 안전 규칙
- SELECT/READ 즉시 실행
- INSERT/UPDATE/DELETE/DROP/WRITE는 사용자 확인
- 결과를 읽기 쉽게 포맷

# KG: ATOM_Skill_db_query
# KG: bhgman-server-architecture-2026-07-15 (v2 docker-free / DGX-only)
