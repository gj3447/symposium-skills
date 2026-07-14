---
name: compute-offload
kg_ref: reference_compute_fleet_offload_2026_07_13
version: "1.1.0"
channel: stable
description: >-
  Mac(디스크압박·GPU없음)의 무거운 작업을 회사 GPU 플릿으로 오프로드. 조종도구 = SYMPOSIUM/PI/dt.sh,
  정본 = SYMPOSIUM/PI/DELLTOWER_OFFLOAD.md (+ airo KG InfraHost = 인프라 정본). 필수세트 4대 전부 Mac SSH OK
  = 워크스테이션 2대(델타워 Precision 7960 Blackwell 98GB `ssh precision7960` / diamondperl Precision
  7875 Ada 48GB `ssh diamondperl`) + GB10 Duo 2대(`ssh spark1`=i2b-llm-no1 vLLM Head Qwen3.6-35B /
  `ssh spark2`=edgexpert-e86b Worker, 델타워 ProxyJump). Invoke when: "델타워", "델 타워", "dell tower",
  "dell precision", "diamondperl", "dgx", "GB10", "airo jetson", "회사 컴퓨터로 돌려", "GPU로 돌려",
  "오프로드", "무거운 작업 넘겨", "vLLM 서버 띄워", "원격 실행", "embedding populate", "32b A/B",
  "dt run/job/serve". 회사 프로덕션(prismv2) 무중단 + 안전 샌드박스(cgroup/oom/디스크가드) 계율 내장.
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
