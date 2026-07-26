#!/usr/bin/env python3
"""gm_dd_chunked.py — GM(disk7s1, ExFAT 2TB) 파티션 블록 이미지를 16GiB 청크로
zstd 압축하며 data-01 NAS로 전송한다.

설계 (2026-07-26, 사용자 승인 "전체 이미지 재실행"):
- root로 실행 (sudo 1회). dd 는 root 가 직접 띄우므로 재인증 없이 iseek 재배치 가능.
- 청크별 sha256(raw/압축) + chunks.jsonl 매니페스트 → 중단 후 같은 명령으로 resume.
- 디스크 hang(300s 무진행) 또는 청크 연속 실패 시 abort — 물리 재연결 후 재실행하면 이어찍기.
- 복원: cat chunk_*.img.zst | zstd -d > gm-disk7s1.img  (zstd 멀티프레임 연결 유효)

사용: sudo python3 bin/gm_dd_chunked.py        (일반 실행/재개)
      python3 bin/gm_dd_chunked.py --plan      (청크 맵만 출력, root 불필요)
"""

import hashlib
import json
import os
import select
import subprocess
import sys
import threading
import time

SRC = "/dev/rdisk7s1"
EXPECTED_TOTAL = 2000397795328  # bytes — disk7s1 파티션 Disk Size (마운트 무관 고정값, 2026-07-26)
VOLUME_HINT = "GM"
CHUNK = 16 * 1024**3  # 16 GiB
DD_BS = 1024 * 1024  # 1m (iseek 단위)
STALL_TIMEOUT = 300  # s 무진행 = hang
CHUNK_RETRY = 5
ABORT_AFTER_CONSECUTIVE_FAILS = 2

DEST_HOST = "metahumotonic27@192.168.0.25"
DEST_DIR = "/srv/dgx4tb/nas/GM_RESCUE_2026/dd"
SSH = [
    "ssh", "-i", "/Users/lagyeongjun/.ssh/id_ed25519",
    "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "UserKnownHostsFile=/Users/lagyeongjun/.ssh/known_hosts",
    DEST_HOST,
]

RUN_DIR = os.path.expanduser("~/.gm_dd_run")
MANIFEST = os.path.join(RUN_DIR, "chunks.jsonl")
N_CHUNKS = (EXPECTED_TOTAL + CHUNK - 1) // CHUNK


def log(msg):
    print(time.strftime("[%Y-%m-%d %H:%M:%S]"), msg, flush=True)


def sha256_self():
    with open(os.path.abspath(__file__), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def verify_device():
    """디스크 번호는 재부팅/재연결로 바뀔 수 있다 — GM ExFAT + 크기 일치 확인."""
    try:
        out = subprocess.run(
            ["diskutil", "info", "disk7s1"], capture_output=True, text=True, timeout=20
        ).stdout
    except Exception as e:  # noqa: BLE001
        log(f"FATAL: diskutil info 실패: {e}")
        return False
    ok = (
        VOLUME_HINT in out
        and "ExFAT" in out
        and str(EXPECTED_TOTAL) in out.replace(",", "")
    )
    if not ok:
        log("FATAL: disk7s1 이 GM ExFAT 2TB 가 아님 — 디스크 번호 변경 가능성. 중단.")
    return ok


def unmount_volume():
    r = subprocess.run(
        ["diskutil", "unmount", "/Volumes/GM"], capture_output=True, text=True
    )
    log(f"unmount /Volumes/GM: rc={r.returncode} {(r.stdout + r.stderr).strip()[:120]}")


def load_done():
    done = set()
    if os.path.exists(MANIFEST):
        with open(MANIFEST) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("status") == "done":
                    done.add(rec["chunk"])
    return done


def run_chunk(i, expected_len):
    """청크 i 전송 (스트리밍). 성공 시 record dict, 실패 시 None."""
    offset_blocks = i * (CHUNK // DD_BS)
    dd = subprocess.Popen(
        ["dd", f"if={SRC}", f"bs={DD_BS}", f"iseek={offset_blocks}"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    zstd = subprocess.Popen(["zstd", "-6", "-T0", "-c"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    tmp = f"{DEST_DIR}/chunk_{i:03d}.img.zst.tmp"
    final = f"{DEST_DIR}/chunk_{i:03d}.img.zst"
    ssh = subprocess.Popen(SSH + [f"cat > {tmp} && mv {tmp} {final}"], stdin=subprocess.PIPE)

    raw_h = hashlib.sha256()
    zst_h = hashlib.sha256()
    zst_size = 0
    hang = False

    def pump_compressed():
        nonlocal zst_size
        while True:
            data = zstd.stdout.read(1 << 20)
            if not data:
                break
            zst_h.update(data)
            zst_size += len(data)
            ssh.stdin.write(data)
        ssh.stdin.close()

    t = threading.Thread(target=pump_compressed, daemon=True)
    t.start()

    remaining = expected_len
    while remaining > 0:
        r, _, _ = select.select([dd.stdout], [], [], STALL_TIMEOUT)
        if not r:
            hang = True
            log(f"chunk {i}: HANG ({STALL_TIMEOUT}s 무진행 — 디스크 의심)")
            break
        block = os.read(dd.stdout.fileno(), min(8 * 1024**2, remaining))
        if not block:
            break  # dd 조기 EOF (마지막 청크 경계)
        raw_h.update(block)
        try:
            zstd.stdin.write(block)
        except BrokenPipeError:
            break
        remaining -= len(block)

    dd.terminate()
    try:
        zstd.stdin.close()
    except Exception:  # noqa: BLE001
        pass
    # 전송측(네트워크) stall 감시: 정상이라도 청크당 ~30분 걸리므로 넉넉히
    t.join(timeout=3600)
    if t.is_alive():
        log(f"chunk {i}: 전송측 stall — ssh/zstd kill")
        ssh.kill()
        zstd.kill()
        t.join(30)
    rc_z, rc_s = zstd.wait(), ssh.wait()
    got = expected_len - remaining
    if hang or rc_z != 0 or rc_s != 0 or got != expected_len:
        log(f"chunk {i}: FAIL (zstd rc={rc_z}, ssh rc={rc_s}, hang={hang}, got={got})")
        return None
    return {
        "chunk": i, "offset": i * CHUNK, "bytes": expected_len,
        "raw_sha256": raw_h.hexdigest(),
        "zst_sha256": zst_h.hexdigest(), "zst_size": zst_size,
        "status": "done", "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }


def append_manifest(rec):
    line = json.dumps(rec, ensure_ascii=False)
    with open(MANIFEST, "a") as f:
        f.write(line + "\n")
    subprocess.run(
        SSH + [f"printf '%s\\n' '{line}' >> {DEST_DIR}/chunks.jsonl"],
        capture_output=True, timeout=30,
    )


def seal_manifest(done_recs):
    seal = hashlib.sha256(
        "".join(done_recs[i]["raw_sha256"] for i in sorted(done_recs)).encode()
    ).hexdigest()
    doc = {
        "image": "gm-disk7s1", "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source_device": SRC, "total_bytes": EXPECTED_TOTAL,
        "chunk_bytes": CHUNK, "n_chunks": N_CHUNKS,
        "chunks": [done_recs[i] for i in sorted(done_recs)],
        "seal_sha256_of_raw_chunk_shas": seal,
        "script_sha256": sha256_self(),
        "restore": "cat chunk_*.img.zst | zstd -d > gm-disk7s1.img",
    }
    payload = json.dumps(doc, ensure_ascii=False, indent=2)
    with open(os.path.join(RUN_DIR, "MANIFEST.json"), "w") as f:
        f.write(payload)
    subprocess.run(
        SSH + [f"cat > {DEST_DIR}/MANIFEST.json"],
        input=payload.encode(), capture_output=True, timeout=60,
    )
    log(f"SEAL 완료: {seal[:16]}… (raw 청크 sha 연결 해시)")


def main():
    if "--plan" in sys.argv:
        for i in range(N_CHUNKS):
            n = min(CHUNK, EXPECTED_TOTAL - i * CHUNK)
            print(f"chunk {i:03d}: offset={i * CHUNK:>13} bytes={n:>13}")
        print(f"total {N_CHUNKS} chunks, {EXPECTED_TOTAL} bytes")
        return 0

    if os.geteuid() != 0:
        log("root 필요: sudo python3 bin/gm_dd_chunked.py")
        return 4
    if not verify_device():
        return 4
    os.makedirs(RUN_DIR, exist_ok=True)
    unmount_volume()

    done = load_done()
    pending = [i for i in range(N_CHUNKS) if i not in done]
    log(f"총 {N_CHUNKS}청크 중 완료 {len(done)}, 잔여 {len(pending)}")
    open(MANIFEST, "a").close()  # 이후 read 경로 단순화 (빈 파일 보장)
    if not pending:
        log("이미 전부 완료 — seal 만 재생성")
        recs = {}
        with open(MANIFEST) as f:
            for line in f:
                rec = json.loads(line)
                if rec.get("status") == "done":
                    recs[rec["chunk"]] = rec
        seal_manifest(recs)
        return 0

    start = time.time()
    consecutive_fails = 0
    done_recs = {}
    with open(MANIFEST) as f:
        for line in f:
            try:
                rec = json.loads(line)
                if rec.get("status") == "done":
                    done_recs[rec["chunk"]] = rec
            except json.JSONDecodeError:
                pass

    for i in pending:
        expected_len = min(CHUNK, EXPECTED_TOTAL - i * CHUNK)
        rec = None
        for attempt in range(1, CHUNK_RETRY + 1):
            rec = run_chunk(i, expected_len)
            if rec:
                break
            log(f"chunk {i}: 재시도 {attempt}/{CHUNK_RETRY}")
            time.sleep(30 * attempt)
        if not rec:
            consecutive_fails += 1
            log(f"chunk {i}: 최종 실패 (연속 {consecutive_fails})")
            if consecutive_fails >= ABORT_AFTER_CONSECUTIVE_FAILS:
                log("연속 실패 — 디스크/네트워크 점검 후 재실행하면 resume 됨. abort.")
                return 3
            continue
        consecutive_fails = 0
        append_manifest(rec)
        done_recs[i] = rec
        elapsed = time.time() - start
        done_now = len([c for c in pending if c in done_recs])
        rate = done_now / max(elapsed, 1)
        eta_h = (len(pending) - done_now) / max(rate, 1e-9) / 3600
        log(f"chunk {i:03d}/{N_CHUNKS - 1} done — zst {rec['zst_size'] / 2**30:.1f}GiB, "
            f"진행 {done_now}/{len(pending)}, ETA ~{eta_h:.1f}h")

    seal_manifest(done_recs)
    log("전체 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
