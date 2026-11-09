#!/usr/bin/env bash
# duty_on_base_pod_batch.sh : the duty test on six base checkpoints and their releases, one card.
#
#   nohup bash scripts/duty_on_base_pod_batch.sh > /root/batch_245.log 2>&1 & echo $! > /root/batch_245.pid
#
# Discovery mode (duty_on_base, records/PREREG_duty_on_base_DUTY_BASE.md). Per arm, ONE load reads the
# banked worksheet bank and then the twelve duty legs (scripts/duty_on_base_duty_worksheet.py).
#
# ORDER, AND WHY (question_word's): CUDA and bf16 asserted, frames re-derived and checked
# byte-for-byte, then each arm prefetches IN ITS OWN PROCESS (a licence 403 surfaces as a
# two-minute fix, not inside a paid read), then reads. gemma9_base goes first: its worksheet
# re-read reproducing local_frames / 239's banked ev is what licenses comparing this card with
# the banked numbers.
#
# DISK: 252.1 GB of Hub bytes over twelve repos (largest 37.0, gemma-2-9b), sized under
# prefetch_216's ALLOW patterns on 2026-11-06. EACH ARM'S WEIGHTS ARE DELETED AFTER ITS
# ARTEFACTS ARE WRITTEN AND ITS CONSUMPTION CHECKS PASS, so the peak is one repo plus
# the venv. Container disk 100 GB, weights on the overlay (not /workspace: geesefs).
#
# Liveness: this script writes its own pid file; nothing watches it by process name.
set -uo pipefail

REPO="${REPO:-/root/working_repository}"
PY="${PY:-/root/venv/bin/python}"
export HF_HOME="${HF_HOME:-/root/hf}"
export HF_HUB_ENABLE_HF_TRANSFER=1
[ -f /root/.hf_token ] && export HF_TOKEN="$(cat /root/.hf_token)"
RUN=duty_on_base
LOGS="$REPO/runs/$RUN/logs"
mkdir -p "$LOGS"
echo $$ > "$REPO/runs/$RUN/batch.pid"
cd "$REPO" || exit 2

say() { echo "[$(date -u '+%H:%M:%SZ')] $*" | tee -a "$LOGS/batch.log"; }
die() { say "REFUSING: $*"; exit 2; }

ARMS=(
  "gemma9_base   google/gemma-2-9b"
  "llama31_base  meta-llama/Llama-3.1-8B"
  "mistral_base  mistralai/Mistral-7B-v0.3"
  "qwen3_base    Qwen/Qwen3-8B-Base"
  "olmo2_base    allenai/OLMo-2-1124-7B"
  "falcon3_base  tiiuae/Falcon3-7B-Base"
  "gemma9_rel    google/gemma-2-9b-it"
  "llama31_rel   meta-llama/Llama-3.1-8B-Instruct"
  "mistral_rel   mistralai/Mistral-7B-Instruct-v0.3"
  "qwen3_rel     Qwen/Qwen3-8B"
  "olmo2_rel     allenai/OLMo-2-1124-7B-Instruct"
  "falcon3_rel   tiiuae/Falcon3-7B-Instruct"
)

say "== duty_on_base  duty test on base and release  HF_HOME=$HF_HOME  commit $(cat GIT_HEAD 2>/dev/null || echo UNKNOWN)"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | sed 's/^/   /' | tee -a "$LOGS/batch.log"
df -h "$(dirname "$HF_HOME")" 2>/dev/null | sed 's/^/   /' | tee -a "$LOGS/batch.log"

$PY -c "
import sys, torch
ok = torch.cuda.is_available(); bf = ok and torch.cuda.is_bf16_supported()
print(f'   torch {torch.__version__} cuda {torch.version.cuda} available {ok} bf16 {bf}')
print(f'   device {torch.cuda.get_device_name(0) if ok else \"NONE\"}')
sys.exit(0 if (ok and bf) else 1)
" | tee -a "$LOGS/batch.log"
[ "${PIPESTATUS[0]}" -eq 0 ] || die "torch cannot see the GPU or cannot do bf16"

$PY scripts/build_duty_on_base_frames.py --check 2>&1 | tee -a "$LOGS/batch.log"
[ "${PIPESTATUS[0]}" -eq 0 ] || die "frames.json differs from a fresh derivation; re-deploy"
$PY scripts/build_question_word_frames.py --check 2>&1 | tee -a "$LOGS/batch.log"
[ "${PIPESTATUS[0]}" -eq 0 ] || die "question_word's manifest (the worksheet consumption check) differs"

for line in "${ARMS[@]}"; do
  read -r arm model <<<"$line"
  if [ -f "$REPO/runs/$RUN/duty/duty_on_base__${arm}.json" ]; then say "-- $arm already read; skipping"; continue; fi
  say "-- $arm  $model  prefetch"
  $PY scripts/prefetch_216.py "$model" 2>&1 | tail -2 | sed 's/^/   /' | tee -a "$LOGS/batch.log"
  [ "${PIPESTATUS[0]}" -eq 0 ] || { say "   PREFETCH FAILED for $arm; skipping, nothing loaded"; continue; }
  say "-- $arm  read: worksheet bank, then duty legs (ONE load)"
  t0=$(date +%s)
  $PY scripts/duty_on_base_duty_worksheet.py --arm "$arm" 2>&1 | tee -a "$LOGS/${arm}.log"
  rc=${PIPESTATUS[0]}
  say "   $arm rc $rc  $(( $(date +%s) - t0 )) s"
  [ "$rc" -eq 2 ] && die "$arm: CONSUMPTION CHECK FAILED; stopping before any further arm"
  if [ "$rc" -eq 0 ] && [ -f "$REPO/runs/$RUN/duty/duty_on_base__${arm}.json" ]; then
    # THE WHOLE HUB CACHE, NOT THE MODEL'S DIRECTORY: prefetch_216 materialises every
    # repo's bytes into ONE shared $HF_HOME/hub/blobs, so deleting models--<repo> freed
    # nothing and the first pass filled 100 GB after four arms (2026-11-06). Only one model
    # is ever on disk here, so the whole cache is that model's.
    rm -rf "$HF_HOME/hub" "$HF_HOME/xet" && say "   hub cache cleared after $arm"
  fi
  df -h "$(dirname "$HF_HOME")" | tail -1 | sed 's/^/   /' | tee -a "$LOGS/batch.log"
done
say "== duty_on_base DONE"
touch "$REPO/runs/$RUN/DONE"
