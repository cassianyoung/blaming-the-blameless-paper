#!/usr/bin/env bash
# question_word_pod_batch.sh : the question-word test on six pretrained base arms, one card.
#
#   nohup bash scripts/question_word_pod_batch.sh > /root/batch_239.log 2>&1 & echo $! > /root/batch_239.pid
#
# Discovery mode (question_word): nothing registered, nothing in the manuscript. Per arm, ONE
# load reads the banked worksheet three times: blame (records/POD_FRAMES_216.json,
# unchanged), at_fault and responsible (records/frames__*.json), all frozen in
# records/frames_manifest.json before this script could run.
#
# ORDER, AND WHY: the cheap failures first. CUDA and bf16 are asserted, the bank and every
# frame file are re-derived and checked byte-for-byte (build_question_word_frames.py --check),
# THEN each arm prefetches IN ITS OWN PROCESS (a licence 403 or a short tree surfaces as
# a two-minute fix, not inside a paid read; geesefs gave Bus errors when download and
# mmap shared a process), THEN reads. gemma9_base goes first because its blame re-read
# reproducing local_frames's banked ev is the check that licenses comparing this card's
# numbers with the banked ones.
#
# WEIGHTS GO ON THE CONTAINER OVERLAY, NOT /workspace (which may be geesefs: mmap SIGBUS
# and 25-60 MB/s). Sized from Hub repo bytes under prefetch_216's ALLOW patterns:
# llama 16.1 + mistral 29.0 + qwen3 16.4 + olmo2 29.2 + falcon3 14.9 + gemma 37.0 =
# 142.6 GB. Container disk 200 GB.
#
# Liveness: this script writes its own pid file; nothing watches it by process name.
set -uo pipefail

REPO="${REPO:-/root/working_repository}"
PY="${PY:-/root/venv/bin/python}"
export HF_HOME="${HF_HOME:-/root/hf}"
export HF_HUB_ENABLE_HF_TRANSFER=1
# gated repos (llama, mistral, gemma): the deploy places the token at /root/.hf_token
[ -f /root/.hf_token ] && export HF_TOKEN="$(cat /root/.hf_token)"
RUN=question_word
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
)

say "== question_word  question word  HF_HOME=$HF_HOME  commit $(cat GIT_HEAD 2>/dev/null || echo UNKNOWN)"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | sed 's/^/   /' | tee -a "$LOGS/batch.log"
df -h "$HF_HOME" "$(dirname "$HF_HOME")" 2>/dev/null | sed 's/^/   /' | tee -a "$LOGS/batch.log"

$PY -c "
import sys, torch
ok = torch.cuda.is_available(); bf = ok and torch.cuda.is_bf16_supported()
print(f'   torch {torch.__version__} cuda {torch.version.cuda} available {ok} bf16 {bf}')
print(f'   device {torch.cuda.get_device_name(0) if ok else \"NONE\"}')
sys.exit(0 if (ok and bf) else 1)
" | tee -a "$LOGS/batch.log"
[ "${PIPESTATUS[0]}" -eq 0 ] || die "torch cannot see the GPU or cannot do bf16 (build the venv with --system-site-packages, requirements WITHOUT torch)"

$PY scripts/build_question_word_frames.py --check 2>&1 | tee -a "$LOGS/batch.log"
[ "${PIPESTATUS[0]}" -eq 0 ] || die "frames or manifest differ from a fresh derivation; re-deploy from the committed tree"

for line in "${ARMS[@]}"; do
  read -r arm model <<<"$line"
  say "-- $arm  $model  prefetch"
  $PY scripts/prefetch_216.py "$model" 2>&1 | tail -2 | sed 's/^/   /' | tee -a "$LOGS/batch.log"
  [ "${PIPESTATUS[0]}" -eq 0 ] || { say "   PREFETCH FAILED for $arm; skipping, nothing loaded"; continue; }
  say "-- $arm  read: blame, at_fault, responsible (ONE load)"
  t0=$(date +%s)
  $PY scripts/question_word_wording.py --arm "$arm" --model "$model" 2>&1 | tee -a "$LOGS/${arm}.log"
  rc=${PIPESTATUS[0]}
  say "   $arm rc $rc  $(( $(date +%s) - t0 )) s"
  [ "$rc" -eq 2 ] && die "$arm: CONSUMPTION CHECK FAILED; stopping before any further arm"
done
say "== question_word DONE"
touch "$REPO/runs/$RUN/DONE"
