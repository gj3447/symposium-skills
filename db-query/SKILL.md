---
name: db-query
kg_ref: ATOM_Skill_db_query
version: "1.0.0"
channel: stable
description: >
  비행기맨 서버의 DB에 쿼리를 실행합니다. Neo4j Cypher, PostgreSQL SQL, MongoDB 쿼리, Redis 명령어를 실행할 때 사용합니다.
---

# DB 쿼리 실행

사용자의 요청에 따라 적절한 DB에 쿼리를 실행합니다.

## 사용 가능한 DB

### Neo4j (Cypher)
```bash
docker exec neo4j cypher-shell -u neo4j -p neo4jpassword "<CYPHER_QUERY>"
```
- MCP 도구 사용 가능: `mcp__neo4j__read_neo4j_cypher`, `mcp__neo4j__write_neo4j_cypher`
- bolt://localhost:7687

### PostgreSQL (SQL)
```bash
docker exec postgresql psql -U postgres -d maindb -c "<SQL_QUERY>"
```
- 데이터베이스: maindb (메인), n8n (n8n용)

### MongoDB
```bash
docker exec mongodb mongosh -u mongo -p mongopassword --eval "<QUERY>"
```

### Redis
```bash
docker exec redis redis-cli -a redispassword <COMMAND>
```

## 안전 규칙
- SELECT/READ 쿼리는 바로 실행
- INSERT/UPDATE/DELETE/DROP 등 쓰기 쿼리는 사용자 확인 후 실행
- 항상 쿼리 결과를 보기 좋게 포맷하여 출력

# KG: ATOM_Skill_db_query
