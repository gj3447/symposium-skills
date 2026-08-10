---
name: compute-offload
kg_ref: reference_compute_fleet_offload_2026_07_13
version: "1.1.0"
channel: stable
description: >-
  Offload GPU-heavy or disk-intensive work from Mac to the approved Precision and GB10 fleet through `PI/dt.sh`, preserving production and sandbox guards. Invoke when: the user names the Dell towers, DGX, GB10, Jetson, remote GPU execution, vLLM, embeddings, or a workload that exceeds the Mac. Do not use when: the job is lightweight, fits the Mac, or only needs reachability inspection; use direct local execution or `$server-status` instead.
---

# compute-offload — 회사 GPU 플릿 오프로드 (thin pointer)

> **정본은 복제하지 않는다(drift 방지).** 플릿표·스펙·gotcha·안전샌드박스 상세 = **`SYMPOSIUM/PI/DELLTOWER_OFFLOAD.md`**.
> 빠른 recall = 메모리 `reference_compute_fleet_offload_2026_07_13`. 조종 = `SYMPOSIUM/PI/dt.sh`.

## 언제
Mac에서 무거운 작업(32b LLM A/B, embedding populate, pytest 대량, code→KG, Rust 빌드, GPU 컴퓨트)을
돌려야 하는데 Mac이 부족할 때 → 회사 GPU 박스로.

## 조종 치트시트 (dt.sh)
```bash
dt=SYMPOSIUM/PI/dt.sh
$dt status | $dt headroom              # 상태 / 여유+우리잡 자가감시
$dt run "<cmd>"                        # 동기
$dt job <name> "<cmd>" ; $dt wait <name> ; $dt logn <name> ; $dt rc <name>   # detached 잡
$dt serve <model> [port] ; $dt tunnel 8100    # vLLM (기본 util 0.30)
DT_GPU_UTIL=0.85 DT_MEM_MAX=80G $dt serve Qwen/Qwen2.5-32B-Instruct 8100 --max-model-len 16384
```
dgx-worker vLLM은 세팅 불필요 — `curl http://192.168.0.23:8000/v1/...` (모델 `qwen3.6-27b`).

## 계율 (상세는 정본)
1. **회사 프로덕션 무중단** — 델타워 `prismv2_*` 가동. **docker 데몬 재시작 금지**, GPU 서빙은 네이티브 venv.
2. **안전 샌드박스 자동** — 잡·서버가 cgroup 하드캡(MemoryMax/CPUQuota/swap=0)+oom_score_adj=800(우리가 먼저 죽음)+디스크가드+nice/ionice에 격리. env `DT_MEM_MAX/DT_CPU_QUOTA/DT_MIN_DISK_GB/DT_GPU_UTIL`.
3. **SSH 안전** — pubkey+ControlMaster 재사용, 난사 금지([[feedback_no_ssh_retry_storm_use_controlmaster]]).
4. **보안 감사/로그 조작·사용 은폐는 안 함** — 정당한 admin 사용. 문제를 숨기는 게 아니라 애초에 안 나게(계율 2).
