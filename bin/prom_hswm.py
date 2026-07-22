#!/usr/bin/env python3
"""
prom_hswm.py v1.0 — PROM SKILL.md v6.4 HSWM primitive helper (W1-T4).

단일 파일 CLI, JSON-in(stdin 또는 --input) / JSON-out(stdout).
PROM Step 2.5/3.3/3.5/4 에서 스킬이 Bash로 호출하는 헬퍼 (선례: SKILLS/bin/resolve_slot.py,
taliban_mathematical_sampler.py).

서브커맨드 5종:
  prefetch-rank : cypher 후보 JSON + --query <problem> → 임베딩 cosine + 場융합 재랭킹 top-30
  dedup         : 신규 findings + 기존 RF pool → 각 finding {duplicate|alternative|new, score, matched_rf}
  consensus     : cycle RF JSON → n-ary 엔티티 하이퍼그래프 + semantic SEED + hyper_fuse
                  → overlapping 합의그룹/충돌후보/singleton *제안* (확정은 KARMA LLM — P2b:
                  naive semantic-on-recommendation 은 MC-null z=0.19 로 REFUTED, 헬퍼=제안기)
  fuse          : 場별 랭킹 JSON → gated_agreement 가중 RRF (stdlib 순수계산 — 모델 불필요)
  bind          : RF 텍스트 + KG 후보 노드 JSON → cosine≥τ 쌍 목록 + float 플래그 목록

── vendor-copy provenance ────────────────────────────────────────────────────
SKILLS 는 별도 서브모듈 repo → HSWM/prom_search_hswm 에서 import 하지 않고 함수 본문을
복사했다. 원본 파일은 LakatoTree 앵커라 이동 금지. 원본 경로(전부
/Users/lagyeongjun/CD/SYMPOSIUM/HSWM/prom_search_hswm/) + sha256 (2026-07-22 시점):

  [F1] hswm_fusion.py
       sha256=1f36d148e92de0a34c283d60143da5feac660b49ca51b151267dec5619b293cb
       복사: _ranks_from_scores(:22) field_confidence(:31) field_agreement(:41)
             _norm_weights(:50) compute_weights(:57) fuse(:94)
  [F2] test_hswm_true_hypergraph.py  (ML16 n-ary 구성)
       sha256=4e13cea86c0debd2888a3d07c07edfddc72f79ed33222fe00cba07313772bc0d
       복사: STOP(:28-29) ents(:30, regex NER)
       참조: build_hyper(:45-69, Zhou 2006 Θ=Dv^-1/2·H·W·De^-1·H^T·Dv^-1/2)
             appnp(:71-74) — 본문은 [F3] build_graphs/appnp 로 동형 복사 (아래)
  [F3] test_hswm_integrated_payoff.py  (ML19 hyper_fuse)
       sha256=b9f07df4f5c7a61727bf133944590b74e4e1872a7c3b229501ad335642813de7
       복사: build_graphs(:44-60, Zhou Θ — [F2] build_hyper 와 동일 정규화)
             appnp(:62-65) rrf(:99-101) hyper_fuse=rrf(sim, ppr_hyper[:,qi])(:112)
  [F4] hswm_hypergraph.py  (프로덕션형 빌더)
       sha256=af902f614d9c3bb665c14ac7baa7c2a1570e58cc9aaf1353811d485c544d2c6a
       복사: Vertex(:45) Hyperedge(:60) Hypergraph(:78) default_extractor(:106)
             build_hypergraph(:116)
  [F5] hswm_hypergraph_readout.py  (V실채널 = findings-as-hyperedge 1급 채점)
       sha256=139bc94b54bb09fd6024c8e14b2c72c92a6229c2f57fa39d2f1139bed357b5f5
       복사: _cos(:25) candidate_pool(:34) readout(:50) expand(:58)

── 명시적 비채택 (반증 준수 — 부활 금지) ─────────────────────────────────────
  * GCN-II 깊이 전파      : ML19 soliddeep = 전 지표 최악 — 채택 안 함, 코드 부재.
  * 의미 엣지가중 Θ-sem    : ML17 −0.031 해침으로 반증 — 하이퍼그래프 엣지 가중은
                            구조(idf·De^-1)만, 의미 유사도를 엣지 가중에 넣지 않는다.
  * blind RRF 단독        : ML5 — 場 게이트 없는 융합 금지. fuse 기본 strategy=gated_agreement.
  * 순수 hypergraph 랭킹 단독 : ML19 CI 0 가로지름 — PPR 단독 랭킹 경로 없음.
  * entity 정점 후보추가   : V∪E 라인 종결 — entity 는 하이퍼엣지(그룹 구조)로만 쓰고
                            랭킹 후보풀에 정점으로 넣지 않는다 (readout 은 edge_only).
  랭킹 경로 = hyper_fuse (flat cosine + hyper PPR 의 RRF) 만.

── 하위호환 계약 (SKILL.md v6.4 fallback) ────────────────────────────────────
  임베딩 의존 서브커맨드(prefetch-rank / dedup / consensus / bind)는 import 실패·모델
  부재 시 {"status": "UNAVAILABLE", "reason": ...} 를 stdout 에 출력하고 exit 0.
  스킬은 UNAVAILABLE 을 받으면 v6.3 lexical 경로로 그대로 진행한다.
  fuse 는 stdlib 순수계산이라 모델 없이도 항상 동작 (UNAVAILABLE 대상 아님).
  모델 부재 시뮬: SENTENCE_TRANSFORMERS_HOME/HF_HOME 을 빈 dir 로 + HF_HUB_OFFLINE=1.

── 모델/캐시 ─────────────────────────────────────────────────────────────────
  기본 all-MiniLM-L6-v2 (GM st_cache 에 캐시됨), fallback
  paraphrase-multilingual-MiniLM-L12-v2 (한/중/영 cross-lingual).
  모델캐시 env 는 /Volumes/GM/hswm_lab/ 지정 시도 (run_on_gm.sh 관례),
  GM 미마운트면 로컬 캐시 폴백. 이미 설정된 env 는 존중.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass, field

try:
    import numpy as np
except Exception:  # numpy 부재 → 임베딩 서브커맨드는 UNAVAILABLE, fuse 는 무관
    np = None

# ── 사전고정 상수 (임계는 파일 상수로 고정 — 호출부에서 튜닝 금지) ──────────
VERSION = "1.0"
RRF_K = 60                    # [F1] hswm_fusion.py:19
TOP_DEFAULT = 30              # prefetch-rank 주입 상한 (SKILL.md Step 2.5: top-30)
DEDUP_DUP_TAU = 0.85          # cosine ≥ → duplicate
DEDUP_ALT_TAU = 0.60          # cosine ≥ → alternative (미만 = new)
DEDUP_ENT_JACCARD = 0.50      # 공유엔티티 Jaccard ≥ 이면 alternative→duplicate 승격 보조신호
BIND_TAU_DEFAULT = 0.55       # 휴리스틱 기본값 — 운영은 P1 캘리브레이션 τ 를 --tau 로 주입 권장
CONSENSUS_GROUP_MIN = 2       # 엔티티 하이퍼엣지 멤버 ≥ 이면 합의그룹 후보
CONSENSUS_DF_MAX = 40         # [F2]:27 DF_MAX — 과다빈출 엔티티 그룹 제외
CONSENSUS_CONFLICT_TAU = 0.35 # 같은 그룹 내 쌍 cosine < 이면 충돌후보
GM_LAB = "/Volumes/GM/hswm_lab"
MODEL_PRIMARY = "all-MiniLM-L6-v2"
MODEL_FALLBACK = "paraphrase-multilingual-MiniLM-L12-v2"


# ══════════════════════════════════════════════════════════════════════════
# [F1] hswm_fusion.py — 場융합 엔진 (verbatim vendor-copy)
# ══════════════════════════════════════════════════════════════════════════

def _ranks_from_scores(scores):
    """score 높은 순 → rank(1=best) per index.  [F1 hswm_fusion.py:_ranks_from_scores:22]"""
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    rk = [0] * len(scores)
    for r, idx in enumerate(order):
        rk[idx] = r + 1
    return rk


def field_confidence(scores):
    """post-retrieval QPP (NQC/clarity 류): top이 mean서 얼마나 떨어져 확신하나.
    flat 분포(신호 無) → ~0. 단 'confident-but-wrong'은 못 거른다(한계 명시).
    [F1 hswm_fusion.py:field_confidence:31]"""
    if not scores:
        return 0.0
    mx = max(scores); mean = statistics.mean(scores)
    sd = statistics.pstdev(scores) or 1e-9
    return max(0.0, (mx - mean) / sd)


def field_agreement(scores, anchor_scores, top_n=10):
    """anchor場(raw) top-N과 이 場 top-N의 겹침 비율. off-domain場(anchor와 딴판) → 낮음.
    confident-but-wrong을 잡는 핵심 신호: 확신해도 anchor와 어긋나면 down-weight.
    [F1 hswm_fusion.py:field_agreement:41]"""
    def top_set(s):
        return set(sorted(range(len(s)), key=lambda i: -s[i])[:top_n])
    a = top_set(scores); b = top_set(anchor_scores)
    return len(a & b) / max(1, len(b))


def _norm_weights(w):
    """[F1 hswm_fusion.py:_norm_weights:50]"""
    tot = sum(w.values())
    if tot <= 0:
        return {k: 1.0 / len(w) for k in w}
    return {k: v / tot for k, v in w.items()}


def compute_weights(rankings, strategy, anchor="raw", gate_threshold=0.2, external_weights=None):
    """場별 가중치 + (게이트 시) 배제 목록 반환.  returns (weights: dict, dropped: list).
    [F1 hswm_fusion.py:compute_weights:57]"""
    names = list(rankings)
    dropped = []
    if strategy == "blind":
        # 주의: blind 는 비교/디버그용으로만 잔존 — 운영 기본은 gated_agreement (ML5).
        return {n: 1.0 for n in names}, dropped
    if strategy == "external":
        # LLM-judge 등 외부 측정 가중치 주입 (DAT식). 0 가중은 배제로 기록.
        w = dict(external_weights or {})
        dropped = [n for n in names if w.get(n, 0.0) <= 0.0 and n != anchor]
        kept = {n: w.get(n, 0.0) for n in names if n not in dropped}
        return _norm_weights(kept), dropped

    anchor_scores = rankings.get(anchor)
    raw_w = {}
    for n in names:
        if strategy == "confidence":
            raw_w[n] = field_confidence(rankings[n])
        elif strategy in ("agreement", "gated_agreement"):
            if n == anchor or anchor_scores is None:
                raw_w[n] = 1.0
            else:
                raw_w[n] = field_agreement(rankings[n], anchor_scores)
        else:
            raise ValueError(f"unknown strategy {strategy}")

    if strategy == "gated_agreement":
        for n in names:
            if n != anchor and raw_w[n] < gate_threshold:
                dropped.append(n)
        raw_w = {n: v for n, v in raw_w.items() if n not in dropped}
        # 게이트 통과 場은 균일(신호 있는 場만 동등 RRF) — Cormack: 비슷한 수준 場엔 무가중이 견고
        return {n: 1.0 for n in raw_w}, dropped

    return _norm_weights(raw_w), dropped


def fuse(rankings, strategy="gated_agreement", anchor="raw", gate_threshold=0.2, k=RRF_K,
         external_weights=None):
    """가중 RRF. return (fused_scores: list[float], weights, dropped).
    [F1 hswm_fusion.py:fuse:94]"""
    weights, dropped = compute_weights(rankings, strategy, anchor, gate_threshold, external_weights)
    n_cand = len(next(iter(rankings.values())))
    field_ranks = {name: _ranks_from_scores(sc) for name, sc in rankings.items() if name in weights}
    fused = [0.0] * n_cand
    for name, w in weights.items():
        rk = field_ranks[name]
        for i in range(n_cand):
            fused[i] += w * (1.0 / (k + rk[i]))
    return fused, weights, dropped


# ══════════════════════════════════════════════════════════════════════════
# [F2]/[F3] ML16 n-ary 하이퍼그래프 구성 + ML19 hyper_fuse (verbatim vendor-copy)
# ══════════════════════════════════════════════════════════════════════════

# [F2 test_hswm_true_hypergraph.py:STOP:28-29]
STOP = {"The", "A", "An", "In", "On", "At", "He", "She", "It", "They", "This", "That", "His",
        "Her", "When", "After", "Before", "There", "Their", "These", "Those", "As", "Of", "For",
        "And", "But", "Also", "However", "Its"}
DF_MIN = 2   # [F2]:27
DF_MAX = 40  # [F2]:27


def ents(t):
    """regex NER — 대문자 시작 고유명 시퀀스.  [F2 test_hswm_true_hypergraph.py:ents:30]"""
    return {mm.lower() for mm in re.findall(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b", t)
            if mm not in STOP and len(mm) > 2}


def build_graphs(pool):
    """Zhou 2006 정규화 n-ary 하이퍼그래프 Θ + binary clique.
    Θ = Dv^-1/2·H·W·De^-1·H^T·Dv^-1/2 — De^-1 = 하이퍼엣지 크기 정규화 = n-ary 핵심항.
    [F3 test_hswm_integrated_payoff.py:build_graphs:44-60] (동일 정규화 = [F2] build_hyper:45-69)"""
    n = len(pool); el = [ents(p) for p in pool]; inv = defaultdict(list)
    for i, es in enumerate(el):
        for e in es: inv[e].append(i)
    ent = [e for e, ps in inv.items() if DF_MIN <= len(ps) <= DF_MAX]
    eidx = {e: j for j, e in enumerate(ent)}; me = len(ent)
    H = np.zeros((n, me), np.float32)
    for e in ent:
        for p in inv[e]: H[p, eidx[e]] = 1.0
    idf = np.array([math.log(n / len(inv[e])) for e in ent], np.float32)
    De = np.array([len(inv[e]) for e in ent], np.float32)
    HW = H * idf[None, :]
    # Zhou n-ary hypergraph (De^-1 = n-ary)
    Theta = (HW * (1 / De)[None, :]) @ H.T if me else np.zeros((n, n), np.float32)
    np.fill_diagonal(Theta, 0)
    Dv = Theta.sum(1); dvi = 1 / np.sqrt(np.maximum(Dv, 1e-9))
    Theta = ((Theta * dvi[:, None]) * dvi[None, :]).astype(np.float32)
    # binary clique (De 정규화 없음 = HippoRAG식 이진) — 비교/구조용으로만 반환, 랭킹 미사용
    Ab = HW @ H.T if me else np.zeros((n, n), np.float32)
    np.fill_diagonal(Ab, 0); db = Ab.sum(1); dbi = 1 / np.sqrt(np.maximum(db, 1e-9))
    Ab = ((Ab * dbi[:, None]) * dbi[None, :]).astype(np.float32)
    return Theta, Ab, el, inv, n, me


def appnp(A, S, al=0.3, K=10):
    """PPR 전파 (APPNP). S shape=(n, nq).  [F3 test_hswm_integrated_payoff.py:appnp:62-65]
    (동형 = [F2]:71-74. 주의: GCN-II 류 깊은 residual 전파는 ML19 반증으로 비채택 — 코드 없음.)"""
    s = np.maximum(S, 0).astype(np.float32); pi = s.copy()
    for _ in range(K): pi = (1 - al) * (A @ pi) + al * s
    return pi


def rrf(a, b, k=60):
    """2채널 RRF — hyper_fuse = rrf(flat cosine, hyper PPR) 가 유일 랭킹 경로 (ML19).
    [F3 test_hswm_integrated_payoff.py:rrf:99-101; hyper_fuse 사용처 :112]"""
    ra = {i: r for r, i in enumerate(np.argsort(-a))}; rb = {i: r for r, i in enumerate(np.argsort(-b))}
    return list(np.argsort(-np.array([1 / (k + ra[i]) + 1 / (k + rb[i]) for i in range(len(a))])))


# ══════════════════════════════════════════════════════════════════════════
# [F4] 하이퍼그래프 빌더 (프로덕션형, verbatim vendor-copy)
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class Vertex:
    """정점 = entity 또는 topic 라벨.  [F4 hswm_hypergraph.py:Vertex:45]"""
    vid: str                    # 정규화 키 (kind:name)
    name: str                   # 원 라벨
    kind: str                   # "entity" | "topic"
    incident_edges: list = field(default_factory=list)
    embedding: object = None

    @property
    def embed_text(self) -> str:
        return self.name if self.kind == "entity" else f"topic: {self.name}"


@dataclass
class Hyperedge:
    """하이퍼엣지 = finding. k-항 관계 + 값 payload.  [F4 hswm_hypergraph.py:Hyperedge:60]"""
    eid: str
    value: str
    members: list = field(default_factory=list)
    clusters: list = field(default_factory=list)
    embedding: object = None

    @property
    def arity(self) -> int:
        return len(self.members)

    @property
    def embed_text(self) -> str:
        return self.value


@dataclass
class Hypergraph:
    """[F4 hswm_hypergraph.py:Hypergraph:78]"""
    vertices: dict
    edges: dict

    def units(self):
        return ([("V", v) for v in sorted(self.vertices)]
                + [("E", e) for e in sorted(self.edges)])

    def dangling_edges(self):
        return sorted(eid for eid, e in self.edges.items() if e.arity == 0)

    def check_incidence(self) -> None:
        for eid, e in self.edges.items():
            for vid in e.members:
                assert vid in self.vertices, f"edge {eid} → 미존재 정점 {vid}"
                assert eid in self.vertices[vid].incident_edges, \
                    f"incidence 비대칭: {eid}∋{vid} 인데 {vid}.incident에 {eid} 없음"
        for vid, v in self.vertices.items():
            for eid in v.incident_edges:
                assert eid in self.edges, f"정점 {vid} → 미존재 엣지 {eid}"
                assert vid in self.edges[eid].members, \
                    f"incidence 비대칭: {vid}∈{eid}.incident 인데 {eid}.members에 {vid} 없음"


def default_extractor(text: str, lexicon=None) -> set:
    """entity 추출 기본값 — 이 헬퍼에선 regex NER(ents)로 대체 주입.
    [F4 hswm_hypergraph.py:default_extractor:106] (원본은 badiou lexicon 매치 — 코퍼스 특화라
    운영 헬퍼 기본은 ents. lexicon 인자를 주면 원본과 동일 word-boundary 매치.)"""
    if lexicon is None:
        return ents(text)
    t = text.lower()
    found = set()
    for e in lexicon:
        if re.search(rf"\b{re.escape(e)}\b", t):
            found.add(e)
    return found


def build_hypergraph(findings, *, extractor=default_extractor, embed=None,
                     topic_vertices=True) -> Hypergraph:
    """findings: [{"rf": str, "text": str, "clusters": [str], ...}] → Hypergraph. 결정론.
    [F4 hswm_hypergraph.py:build_hypergraph:116]"""
    vertices = {}
    edges = {}

    def ensure_vertex(name: str, kind: str) -> str:
        vid = f"{kind}:{name}"
        if vid not in vertices:
            vertices[vid] = Vertex(vid=vid, name=name, kind=kind)
        return vid

    for f in findings:
        eid = f["rf"]
        if eid in edges:
            raise ValueError(f"중복 finding id {eid} — id는 유일해야 함")
        member_vids = set()
        for ent in extractor(f["text"]):
            member_vids.add(ensure_vertex(ent, "entity"))
        if topic_vertices:
            for cl in f.get("clusters", []):
                if cl not in ("primary", "secondary", "critique"):
                    member_vids.add(ensure_vertex(cl, "topic"))
        edge = Hyperedge(
            eid=eid,
            value=f["text"],
            members=sorted(member_vids),
            clusters=list(f.get("clusters", [])),
        )
        edges[eid] = edge
        for vid in edge.members:
            vertices[vid].incident_edges.append(eid)

    for v in vertices.values():
        v.incident_edges.sort()

    hg = Hypergraph(vertices=vertices, edges=edges)

    if embed is not None:
        v_order = sorted(hg.vertices)
        e_order = sorted(hg.edges)
        texts = [hg.vertices[v].embed_text for v in v_order] + \
                [hg.edges[e].embed_text for e in e_order]
        vecs = embed(texts)
        for i, v in enumerate(v_order):
            hg.vertices[v].embedding = vecs[i]
        for j, e in enumerate(e_order):
            hg.edges[e].embedding = vecs[len(v_order) + j]

    hg.check_incidence()
    return hg


# ══════════════════════════════════════════════════════════════════════════
# [F5] V∪E readout (verbatim vendor-copy) — 운영 사용은 edge_only 만
#   (entity 정점을 랭킹 후보로 추가하는 라인은 V∪E 실험 종결로 비채택 —
#    findings-as-hyperedge 가 실현된 V실채널)
# ══════════════════════════════════════════════════════════════════════════

def _cos(a, b) -> float:
    """[F5 hswm_hypergraph_readout.py:_cos:25]"""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1e-9
    nb = math.sqrt(sum(y * y for y in b)) or 1e-9
    return dot / (na * nb)


def candidate_pool(hg: Hypergraph, mode: str):
    """(kind, id, embedding) 리스트. mode: node_only | edge_only | v_union_e.
    [F5 hswm_hypergraph_readout.py:candidate_pool:34]"""
    pool = []
    if mode in ("node_only", "v_union_e"):
        for vid in sorted(hg.vertices):
            v = hg.vertices[vid]
            if v.embedding is not None:
                pool.append(("V", vid, v.embedding))
    if mode in ("edge_only", "v_union_e"):
        for eid in sorted(hg.edges):
            e = hg.edges[eid]
            if e.embedding is not None:
                pool.append(("E", eid, e.embedding))
    return pool


def readout(hg: Hypergraph, query_vec, mode: str = "edge_only", top_k: int = 10):
    """질의 임베딩 → (kind, id, score) 상위 top_k. 결정론(동점은 id 사전순).
    [F5 hswm_hypergraph_readout.py:readout:50] (기본 mode 만 edge_only 로 변경 — 비채택 정책)"""
    pool = candidate_pool(hg, mode)
    scored = [(kind, uid, _cos(query_vec, emb)) for kind, uid, emb in pool]
    scored.sort(key=lambda r: (-r[2], r[0], r[1]))
    return scored[:top_k]


def expand(hg: Hypergraph, unit_kind: str, unit_id: str) -> dict:
    """읽어낸 unit → 1-hop 이웃 + 값 payload.  [F5 hswm_hypergraph_readout.py:expand:58]"""
    if unit_kind == "E":
        e = hg.edges[unit_id]
        return {"value": e.value, "members": e.members, "clusters": e.clusters}
    v = hg.vertices[unit_id]
    return {"name": v.name, "kind": v.kind,
            "incident_edges": v.incident_edges,
            "values": [hg.edges[eid].value for eid in v.incident_edges]}


# ══════════════════════════════════════════════════════════════════════════
# 모델 로딩 / 공통 IO
# ══════════════════════════════════════════════════════════════════════════

def _setup_cache_env():
    """모델캐시를 GM 으로 재지정 (run_on_gm.sh 관례). 이미 설정된 env 는 존중.
    GM 미마운트면 로컬 캐시 폴백 (첫 다운로드 ~90MB — GM 권장)."""
    if os.environ.get("SENTENCE_TRANSFORMERS_HOME"):
        return
    if os.path.isdir(GM_LAB):
        os.environ.setdefault("HF_HOME", f"{GM_LAB}/hf_cache")
        os.environ.setdefault("HUGGINGFACE_HUB_CACHE", f"{GM_LAB}/hf_cache")
        os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", f"{GM_LAB}/st_cache")
        os.environ.setdefault("TORCH_HOME", f"{GM_LAB}/hf_cache/torch")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def load_model():
    """returns (model|None, reason|None). None 이면 호출부가 UNAVAILABLE 처리."""
    if np is None:
        return None, "numpy unavailable"
    _setup_cache_env()
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        return None, f"import failure: {type(e).__name__}"
    last = "no model"
    for name in (MODEL_PRIMARY, MODEL_FALLBACK):
        try:
            return SentenceTransformer(name), None
        except Exception as e:
            last = f"model load failure ({name}): {type(e).__name__}"
    return None, last


def _embed(model, texts):
    return model.encode(texts, normalize_embeddings=True, convert_to_numpy=True,
                        batch_size=64, show_progress_bar=False).astype(np.float32)


def _unavailable(reason):
    print(json.dumps({"status": "UNAVAILABLE", "reason": reason}, ensure_ascii=False))
    return 0


def _error(reason):
    print(json.dumps({"status": "ERROR", "reason": reason}, ensure_ascii=False))
    return 2


def _read_input(args):
    if getattr(args, "input", None):
        with open(args.input) as f:
            return json.load(f)
    data = sys.stdin.read()
    if not data.strip():
        return None
    return json.loads(data)


def _item_id(c, i):
    for k in ("id", "rf", "findingId", "name"):
        if c.get(k) is not None:
            return str(c[k])
    return f"idx{i}"


def _item_text(c):
    for k in ("text", "desc", "description", "oneLineSummary", "summary", "problem", "name"):
        v = c.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def _norm_items(raw, key):
    """{"<key>": [...]} 또는 bare list 허용 → [(id, text, orig)]"""
    items = raw.get(key) if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise ValueError(f"input must be a list or {{'{key}': [...]}}")
    out = []
    for i, c in enumerate(items):
        if isinstance(c, str):
            out.append((f"idx{i}", c, {"text": c}))
        elif isinstance(c, dict):
            out.append((_item_id(c, i), _item_text(c), c))
        else:
            raise ValueError(f"item {i}: unsupported type {type(c).__name__}")
    return out


# ══════════════════════════════════════════════════════════════════════════
# 서브커맨드
# ══════════════════════════════════════════════════════════════════════════

def cmd_prefetch_rank(args):
    """Step 2.5: cypher 후보(LIMIT 확장 pool) → 임베딩 cosine + 場융합 재랭킹 top-N.
    場 = raw(입력 검색순서 or 후보의 score 필드) + semantic(cosine). 융합=gated_agreement."""
    try:
        raw = _read_input(args)
        cands = _norm_items(raw, "candidates")
    except Exception as e:
        return _error(f"bad input: {e}")
    if not cands:
        print(json.dumps({"status": "OK", "top": [], "weights": {}, "dropped": []},
                         ensure_ascii=False))
        return 0
    if not args.query:
        return _error("--query required for prefetch-rank")
    model, why = load_model()
    if model is None:
        return _unavailable(why)
    texts = [t for _, t, _ in cands]
    vecs = _embed(model, [args.query] + texts)
    q, E = vecs[0], vecs[1:]
    sem = (E @ q).tolist()
    # raw場: 후보에 수치 score 있으면 그걸, 없으면 입력(검색) 순서 기반 점수
    if any(isinstance(o.get("score"), (int, float)) for _, _, o in cands):
        raw_scores = [float(o.get("score") or 0.0) for _, _, o in cands]
    else:
        raw_scores = [1.0 / (1 + i) for i in range(len(cands))]
    rankings = {"raw": raw_scores, "semantic": sem}
    fused, weights, dropped = fuse(rankings, strategy=args.strategy, anchor=args.anchor)
    order = sorted(range(len(cands)), key=lambda i: (-fused[i], cands[i][0]))
    top = [{"id": cands[i][0], "text": cands[i][1][:300],
            "fused": round(fused[i], 6), "semantic_cos": round(sem[i], 4),
            "raw_rank": i + 1} for i in order[:args.top]]
    print(json.dumps({"status": "OK", "query": args.query, "n_candidates": len(cands),
                      "strategy": args.strategy, "weights": weights, "dropped": dropped,
                      "top": top}, ensure_ascii=False))
    return 0


def cmd_dedup(args):
    """Step 3.3-2: 신규 findings vs 기존 RF pool → {duplicate|alternative|new} 제안.
    신호 = 임베딩 cosine(max vs pool) + 공유엔티티 하이퍼엣지 겹침(Jaccard).
    임계 = 파일 상수 (DEDUP_DUP_TAU/DEDUP_ALT_TAU/DEDUP_ENT_JACCARD) — 사전고정.
    결정표 적용/확정은 SKILL.md 측 (헬퍼는 판정 입력만 제공)."""
    try:
        raw = _read_input(args)
        new = _norm_items(raw, "new_findings") if isinstance(raw, dict) and "new_findings" in raw \
            else _norm_items(raw, "new")
        pool = _norm_items(raw.get("pool", []), "pool") if isinstance(raw, dict) else []
    except Exception as e:
        return _error(f"bad input: {e}")
    if not new:
        print(json.dumps({"status": "OK", "results": []}, ensure_ascii=False))
        return 0
    if not pool:
        print(json.dumps({"status": "OK", "results": [
            {"id": nid, "verdict": "new", "score": 0.0, "matched_rf": None,
             "semantic_cos": 0.0, "entity_jaccard": 0.0, "shared_entities": []}
            for nid, _, _ in new]}, ensure_ascii=False))
        return 0
    model, why = load_model()
    if model is None:
        return _unavailable(why)
    new_texts = [t for _, t, _ in new]; pool_texts = [t for _, t, _ in pool]
    vecs = _embed(model, new_texts + pool_texts)
    En, Ep = vecs[:len(new)], vecs[len(new):]
    sims = En @ Ep.T  # (n_new, n_pool)
    pool_ents = [ents(t) for t in pool_texts]
    results = []
    for i, (nid, ntext, _) in enumerate(new):
        j = int(np.argmax(sims[i]))
        sem = float(sims[i][j])
        ne = ents(ntext); pe = pool_ents[j]
        union = ne | pe
        ent_j = (len(ne & pe) / len(union)) if union else 0.0
        if sem >= DEDUP_DUP_TAU or (sem >= DEDUP_ALT_TAU and ent_j >= DEDUP_ENT_JACCARD):
            verdict = "duplicate"
        elif sem >= DEDUP_ALT_TAU:
            verdict = "alternative"
        else:
            verdict = "new"
        results.append({"id": nid, "verdict": verdict, "score": round(sem, 4),
                        "matched_rf": pool[j][0], "semantic_cos": round(sem, 4),
                        "entity_jaccard": round(ent_j, 4),
                        "shared_entities": sorted(ne & pe)})
    print(json.dumps({"status": "OK",
                      "thresholds": {"dup_tau": DEDUP_DUP_TAU, "alt_tau": DEDUP_ALT_TAU,
                                     "ent_jaccard": DEDUP_ENT_JACCARD},
                      "results": results}, ensure_ascii=False))
    return 0


def cmd_consensus(args):
    """Step 4-1/4-2 제안기: cycle RF → n-ary 엔티티 하이퍼그래프(Zhou Θ) + semantic SEED
    + hyper_fuse → overlapping 합의그룹/충돌후보/singleton *제안*.
    확정은 4-4 KARMA LLM (P2b: naive semantic-on-recommendation REFUTED — 헬퍼는 제안만).
    overlapping 표현: 한 finding 이 여러 그룹(엔티티 하이퍼엣지)에 속할 수 있음 (P2b 발견).
    SEED = query 임베딩 semantic only (ML17 확증 config — 의미 엣지가중은 반증이라 없음)."""
    try:
        raw = _read_input(args)
        findings = _norm_items(raw, "findings")
        query = args.query or (raw.get("query") if isinstance(raw, dict) else None)
    except Exception as e:
        return _error(f"bad input: {e}")
    if not findings:
        print(json.dumps({"status": "OK", "groups": [], "conflict_candidates": [],
                          "singletons": [], "finding_ranking": None}, ensure_ascii=False))
        return 0
    model, why = load_model()
    if model is None:
        return _unavailable(why)
    ids = [fid for fid, _, _ in findings]
    texts = [t for _, t, _ in findings]
    if len(set(ids)) != len(ids):
        return _error("duplicate finding ids in input")

    def emb_fn(ts):
        return _embed(model, ts).tolist()

    # [F4] 빌더: topic_vertices=False (운영 findings 에 gold cluster 없음 / leakage 회피)
    hg = build_hypergraph([{"rf": fid, "text": t} for fid, t, _ in findings],
                          extractor=default_extractor, embed=emb_fn, topic_vertices=False)
    E = np.array([hg.edges[fid].embedding for fid in ids], np.float32)
    pair = E @ E.T  # finding 간 cosine (cohesion/충돌 신호)

    # overlapping 합의그룹 = 엔티티 하이퍼엣지 (멤버수 [CONSENSUS_GROUP_MIN, CONSENSUS_DF_MAX])
    idx = {fid: i for i, fid in enumerate(ids)}
    groups, conflicts = [], []
    singleton_mask = {fid: True for fid in ids}
    for vid in sorted(hg.vertices):
        v = hg.vertices[vid]
        members = v.incident_edges
        if not (CONSENSUS_GROUP_MIN <= len(members) <= CONSENSUS_DF_MAX):
            continue
        mi = [idx[m] for m in members]
        cos_pairs = [(members[a], members[b], float(pair[mi[a], mi[b]]))
                     for a in range(len(mi)) for b in range(a + 1, len(mi))]
        cohesion = statistics.mean(c for _, _, c in cos_pairs) if cos_pairs else 0.0
        groups.append({"entity": v.name, "members": list(members),
                       "size": len(members), "cohesion": round(cohesion, 4)})
        for m in members:
            singleton_mask[m] = False
        for a, b, c in cos_pairs:
            if c < CONSENSUS_CONFLICT_TAU:
                conflicts.append({"entity": v.name, "pair": [a, b],
                                  "cosine": round(c, 4),
                                  "reason": "shared-entity group but low semantic agreement"})
    groups.sort(key=lambda g: (-g["size"], -g["cohesion"], g["entity"]))
    singletons = [fid for fid in ids if singleton_mask[fid]]

    # finding 랭킹 (query 있을 때만): 유일 경로 = hyper_fuse (ML19)
    #   sim 채널 = [F5] readout(edge_only — findings-as-hyperedge 1급 채점, V실채널)
    #   구조 채널 = [F2/F3] Zhou Θ + appnp PPR.  PPR 단독 랭킹 반환 금지 (ML19 CI 0).
    finding_ranking = None
    if query:
        qv = _embed(model, [query])[0]
        ro = readout(hg, qv.tolist(), mode="edge_only", top_k=len(ids))
        score_by_id = {uid: sc for _, uid, sc in ro}
        sim = np.array([score_by_id.get(fid, 0.0) for fid in ids], np.float32)
        Theta, _Ab, _el, _inv, _n, _me = build_graphs(texts)
        ppr = appnp(Theta, sim[:, None], al=0.3, K=10)[:, 0]
        order = rrf(sim, ppr)  # hyper_fuse
        finding_ranking = [{"id": ids[i], "sim": round(float(sim[i]), 4),
                            "ppr": round(float(ppr[i]), 6)} for i in order]

    print(json.dumps({"status": "OK", "n_findings": len(ids),
                      "groups": groups, "conflict_candidates": conflicts,
                      "singletons": singletons, "finding_ranking": finding_ranking,
                      "note": "proposals only — final grouping/conflict verdict = KARMA LLM "
                              "(Step 4-4). P2b: naive semantic-on-recommendation REFUTED."},
                     ensure_ascii=False))
    return 0


def cmd_fuse(args):
    """Step 4-0: 場별 랭킹 → gated_agreement 가중 RRF. stdlib 순수계산 (모델 불필요).
    blind 단독 융합은 ML5 반증 — 기본 strategy=gated_agreement, anchor=raw."""
    try:
        raw = _read_input(args)
        rankings = raw["rankings"] if isinstance(raw, dict) and "rankings" in raw else raw
        if not isinstance(rankings, dict) or not rankings:
            raise ValueError("need {'rankings': {field: [scores...]}}")
        lens = {k: len(v) for k, v in rankings.items()}
        if len(set(lens.values())) != 1:
            raise ValueError(f"ranking length mismatch: {lens}")
        ids = raw.get("ids") if isinstance(raw, dict) else None
        n = next(iter(lens.values()))
        if ids is not None and len(ids) != n:
            raise ValueError("ids length mismatch")
        ext = raw.get("external_weights") if isinstance(raw, dict) else None
    except Exception as e:
        return _error(f"bad input: {e}")
    try:
        fused, weights, dropped = fuse({k: [float(x) for x in v] for k, v in rankings.items()},
                                       strategy=args.strategy, anchor=args.anchor,
                                       gate_threshold=args.gate_threshold,
                                       external_weights=ext)
    except ValueError as e:
        return _error(str(e))
    order = sorted(range(n), key=lambda i: -fused[i])
    print(json.dumps({"status": "OK", "strategy": args.strategy, "anchor": args.anchor,
                      "weights": weights, "dropped": dropped,
                      "fused": [round(x, 6) for x in fused],
                      "order": [(ids[i] if ids else i) for i in order]},
                     ensure_ascii=False))
    return 0


def cmd_bind(args):
    """Step 3.5: RF 텍스트 ↔ 기존 KG 후보 노드 → cosine≥τ 쌍(weight-semantic 엣지 재료)
    + τ 미달 RF 는 float 플래그 목록. τ 기본 = BIND_TAU_DEFAULT (휴리스틱) —
    운영은 P1 캘리브레이션 τ(null_mean+3·null_std) 를 --tau 로 주입 권장.
    LakatoTree hard core 구현 재료: '외부노드는 롱기누스 weight-semantic 엣지로
    내부場 바인딩 or float 플래그'."""
    try:
        raw = _read_input(args)
        findings = _norm_items(raw, "findings")
        cands = _norm_items(raw.get("candidates", []), "candidates") if isinstance(raw, dict) else []
    except Exception as e:
        return _error(f"bad input: {e}")
    tau = args.tau if args.tau is not None else BIND_TAU_DEFAULT
    if not findings:
        print(json.dumps({"status": "OK", "tau": tau, "bindings": [], "floats": []},
                         ensure_ascii=False))
        return 0
    if not cands:
        print(json.dumps({"status": "OK", "tau": tau, "bindings": [],
                          "floats": [{"rf": fid, "best_node": None, "best_cos": None}
                                     for fid, _, _ in findings]}, ensure_ascii=False))
        return 0
    model, why = load_model()
    if model is None:
        return _unavailable(why)
    f_texts = [t for _, t, _ in findings]; c_texts = [t for _, t, _ in cands]
    vecs = _embed(model, f_texts + c_texts)
    Ef, Ec = vecs[:len(findings)], vecs[len(findings):]
    sims = Ef @ Ec.T
    bindings, floats = [], []
    for i, (fid, _, _) in enumerate(findings):
        row = sims[i]
        hits = [(cands[j][0], float(row[j])) for j in range(len(cands)) if row[j] >= tau]
        hits.sort(key=lambda h: (-h[1], h[0]))
        if hits:
            for nid, w in hits:
                bindings.append({"rf": fid, "node": nid, "weight": round(w, 4)})
        else:
            j = int(np.argmax(row))
            floats.append({"rf": fid, "best_node": cands[j][0],
                           "best_cos": round(float(row[j]), 4)})
    print(json.dumps({"status": "OK", "tau": tau, "tau_source":
                      ("cli" if args.tau is not None else "default_constant"),
                      "bindings": bindings, "floats": floats}, ensure_ascii=False))
    return 0


# ══════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════

def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="prom_hswm.py",
        description="PROM v6.4 HSWM primitive helper (JSON-in/JSON-out). "
                    "UNAVAILABLE 시 스킬은 v6.3 lexical 경로로 진행.")
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, needs_query=False):
        p.add_argument("--input", help="입력 JSON 파일 (생략 시 stdin)")
        if needs_query:
            p.add_argument("--query", help="problem/질의 텍스트")

    p = sub.add_parser("prefetch-rank", help="Step 2.5 후보 재랭킹")
    common(p, needs_query=True)
    p.add_argument("--top", type=int, default=TOP_DEFAULT)
    p.add_argument("--strategy", default="gated_agreement",
                   choices=["gated_agreement", "agreement", "confidence", "blind", "external"])
    p.add_argument("--anchor", default="raw")
    p.set_defaults(fn=cmd_prefetch_rank)

    p = sub.add_parser("dedup", help="Step 3.3-2 semantic dedup 제안")
    common(p)
    p.set_defaults(fn=cmd_dedup)

    p = sub.add_parser("consensus", help="Step 4-1/4-2 합의그룹/충돌 제안")
    common(p, needs_query=True)
    p.set_defaults(fn=cmd_consensus)

    p = sub.add_parser("fuse", help="Step 4-0 場융합 (stdlib, 모델 불필요)")
    common(p)
    p.add_argument("--strategy", default="gated_agreement",
                   choices=["gated_agreement", "agreement", "confidence", "blind", "external"])
    p.add_argument("--anchor", default="raw")
    p.add_argument("--gate-threshold", dest="gate_threshold", type=float, default=0.2)
    p.set_defaults(fn=cmd_fuse)

    p = sub.add_parser("bind", help="Step 3.5 RF→KG weight-semantic 바인딩 쌍")
    common(p)
    p.add_argument("--tau", type=float, default=None,
                   help=f"cosine 바인딩 임계 (기본 {BIND_TAU_DEFAULT}; P1 캘리브레이션 τ 권장)")
    p.set_defaults(fn=cmd_bind)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
