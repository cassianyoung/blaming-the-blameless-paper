# Pre-registration, duty_on_base: the duty test on base checkpoints

Written 2026-11-06, before any pod is rented. The instruction follows verbatim, then
Amendment 0, which fixes what it leaves open and records four places where it does not match
the banked material or a standing rule. Points marked **FOR RULING** carry a default that
applies unless the author rules otherwise.

**FROZEN 2026-11-06 ON THE AUTHOR'S RULINGS (end of file), NO POD YET.** Frames
`duty_on_base_FRAMES.json`, sha256
**7fb5badfad0b1994efca57c4d4cc45d44109a9743f56584f57e8db2281c2ed04** (byte-identical to the
dry-run draft), pinned in `read_duty_on_base.py`. Drafted at a4469567.

---

# Instruction: the duty test on base checkpoints (duty_on_base)

Discovery mode, in AI_Ethics. Pod work, on the RTX A6000 48 GB (the banked card class), six
small base models only. Pre-register the predictions below before the pod is rented; freeze
the frames by hash; stop with the estimate.

## THE QUESTION

The paper read role blindness on deployed models only. A claim now on the table is that
pretraining carries the structure of the allowance (what people owe someone who acted for them
as a favour) and post-training overlays rules on it. If so, base models should give the
private person more of the allowance than their releases do. If base models withhold it as
the releases do, the allowance was never compressed into the weights, and strict causal blame
is the only disposition in evidence at the base.

## MODELS (pretrained base, bf16, no quantisation; the banked worksheet models)

Llama-3.1-8B, Mistral-7B-v0.3, Qwen3-8B-Base, OLMo-2-1124-7B, Falcon3-7B-Base, gemma-2-9b. Six
is enough to know whether anything is there; the larger checkpoints follow only if it is.

Also read, on the same card and in the same session: the six developer releases of the same
families, on the worksheet, so base and release are compared like for like on one frame.

## WHAT IS READ

The duty bank's six pairs (electrical work, gas safety, childcare, driving, hair dye, prawns),
both legs (the careless professional and the careless private person), each as a separate
case, on the worksheet frame (the four banked worked examples, five orderings, next-token
readout, the banked gate). The side-by-side condition cannot be read on a base model (it
needs a two-score answer), so the stated slack is not available at the base; the comparison
is the gap between the two legs read separately, in digits, as the paper's "slack given".

For the scale, read the duty-test anchors the paper's builders use for the worksheet (the
banked N and C for each pair's scenario), so each leg's position can be formed on its own
anchors as well as its raw digit.

## PRE-REGISTERED PREDICTIONS

Let gap = professional-leg mean digit minus private-leg mean digit, per model and pair, on
the worksheet. The release's gap on the same frame is the comparison.

- **duty_on_base P1 (the residue claim).** Pooled over the five pairs other than driving, base models'
  gap exceeds their releases' gap by at least 0.5 digits on at least 4 of 6 models. (Pass =
  the allowance is larger before post-training.)
- **duty_on_base P2 (the alternative: nothing there).** Base models' gap is within one pooled noise band
  of zero on at least 20 of 30 model–pair cells. (Pass = the base does not distinguish the
  legs.)
- **duty_on_base P3 (driving as control).** On the driving pair, where both legs break the same rule,
  the gap is within one band of zero for base and release alike.
- **Null for the residue claim.** If duty_on_base P1 fails, the base carries no more of the allowance
  than the release.

duty_on_base P1 and duty_on_base P2 cannot both pass; register which outcome supports which reading.

## WHAT IS ALSO RECORDED

Per model and pair, both legs' raw digits and positions, with their bands; the gate per
cell; the professional leg's digit on its own (whether base models blame the professional at
the release's level, or less); and the same readings for the release.

## PRICE AND STOP

About 6 models × 2 versions × 6 pairs × 2 legs × 5 orderings, plus anchors: a few hundred
worksheet completions per model, well under an hour on the card. Card cap $6; shut the pod
down the moment the last model is read. STOP with the estimate and the frozen frames before
renting.

## REPORT

Per model: the six gaps for base and for release, side by side, with bands; the pooled
medians; duty_on_base P1–duty_on_base P3 pass or fail; and a one-paragraph reading written before the results
are seen, saying what each outcome would mean for the claim that pretraining carries the
structure of the allowance.

---

# Amendment 0 (2026-11-06, before any pod)

## A0.0 Four points checked against the banked material and the standing rules

1. **There are no banked duty-test anchors on the worksheet.** The duty test has never been
   read on the worksheet (no script, record or registered figure does so). The duty bank
   holds only the two careless legs per pair, plus a control; it has no careful (N) or
   careless-with-harm (C) row per pair. **The one exception is prawns, whose two legs ARE
   the C rows of the worksheet bank's prawns_restaurant and prawns_home scenarios** (same
   strings, asserted by the builder), so "each leg on its own anchors" would place them at
   1.0 by construction. See A0.4 for the ruler used instead.
2. **The standing ruler rule forbids comparing raw digits across arms, and base against
   release is a comparison across arms.** CLAUDE.md, "NO CROSS-ARM COMPARISON IN RAW
   DIGITS. EVERY ARM CARRIES A RULER PER CHANNEL", and "A THRESHOLD IN DIGITS IS A
   THRESHOLD IN SOMEONE'S UNITS". On question_word's banked worksheet reads the six base arms'
   median C − N runs from **2.14 digits (Mistral) to 4.38 (Falcon3)**, so 0.5 digits is 23%
   of one arm's range and 11% of another's. See A0.6.
3. **A release on the worksheet is not the release as deployed.** The worksheet is a
   completion frame: no chat template, the instruct model continuing a page of ratings. That
   is what makes base and release like for like on one frame, as the instruction asks, and
   it is also why this reading says nothing directly about the deployed models the paper
   read. local_frames read two releases this way (gemma-2-27b-it, Yi-1.5-34B-Chat) and both licensed
   6 of 6 worksheet scenarios (checked on the worksheet reading's banked cells), so the frame is readable on
   instruct models.
4. **duty_on_base P1 and duty_on_base P2 CAN both pass**: base gaps near zero, and releases' gaps negative (the
   release blaming the private person more than the professional), puts base minus release
   above 0.5 while the base sits inside its band. The four outcomes are registered in A0.9.

## A0.1 Material, frozen (PENDING the freeze commit)

`build_duty_on_base_frames.py` → `duty_on_base_FRAMES.json`, sha256 7fb5badf (above). Nothing in
it is authored:
- **Legs**: the twelve strings syllogism_duty and an earlier run read (from `v11_frames.json`, its
  pinned sha asserted), each traced by sha to its bank row: pairs 1, 3, 4, 5 from
  `moral__duty__v1.jsonl` (DUTYn_PRO, DUTYn_PRIV), pair 7 from `moral__duty228__v1.jsonl`,
  prawns from `moral__families__v1.jsonl` (prawns_restaurant__C, prawns_home__C). Each names
  Alaric, so the worksheet asks about him.
- **Frames**: the banked worksheet, `worksheet_FRAMES__blame.json`, its five completion
  orderings (`b2_completion_named`, `_2` to `_5`), unchanged and asserted by id.
- **Prompt hashes**: sha256[:16] of every rendered duty prompt (5 orderings x 12 legs), the
  string `rate_pod216.read_cell` hashes, compared cell by cell after the read.

## A0.2 Arms

| Arm | Hub id | GB | Arm | Hub id | GB |
|---|---|---|---|---|---|
| gemma9_base | google/gemma-2-9b | 37.0 | gemma9_rel | google/gemma-2-9b-it | 18.5 |
| llama31_base | meta-llama/Llama-3.1-8B | 16.1 | llama31_rel | meta-llama/Llama-3.1-8B-Instruct | 16.1 |
| mistral_base | mistralai/Mistral-7B-v0.3 | 29.0 | mistral_rel | mistralai/Mistral-7B-Instruct-v0.3 | 29.0 |
| qwen3_base | Qwen/Qwen3-8B-Base | 16.4 | qwen3_rel | Qwen/Qwen3-8B | 16.4 |
| olmo2_base | allenai/OLMo-2-1124-7B | 29.2 | olmo2_rel | allenai/OLMo-2-1124-7B-Instruct | 14.6 |
| falcon3_base | tiiuae/Falcon3-7B-Base | 14.9 | falcon3_rel | tiiuae/Falcon3-7B-Instruct | 14.9 |

- bf16, `cuda:bfloat16`, no quantisation. Base arm names are question_word's, so its banked cells
  are the reproduction comparand. Sizes are Hub bytes under `prefetch_216`'s patterns, read
  2026-11-06: **252.1 GB in all**. gemma and Llama repos are gated; the token's access was
  used in question_word for the base repos and must also cover gemma-2-9b-it and
  Llama-3.1-8B-Instruct (prefetch fails fast if not; that arm is then unread, not moved).
- **"Developer release" is read as the instruct checkpoint** each developer ships for that
  base. Qwen3-8B is a hybrid reasoning release; on the worksheet (no chat template) no
  reasoning block is opened.

## A0.3 What one arm reads, on one load

1. **The banked worksheet bank** (`moral__families223__v1.jsonl`, six scenarios, every role,
   five orderings, 310 cells) by `rate_pod216.main` with the local_frames / question_word base-arm
   invocation (completion, read through the gate, no harvest). This gives each arm its
   ruler and gate on the frame the legs are read on. Every non-void cell's prompt hash is
   checked against question_word's frozen manifest for the blame wording.
2. **The twelve duty legs**, 5 orderings each (60 cells), by `rate_pod216.read_cell`, the
   function that scored every banked worksheet cell, on the same load.

The CPU dry run (gpt2, `--dry-run`, into a dry-run directory, never the real paths) passed
end to end: one load, 310 worksheet cells carrying question_word's manifest hashes, 60 duty cells
carrying the frozen hashes, and the analysis reading both.

## A0.4 Definitions (results_derive's; nothing new)

- **Leg**: mean ev over its five orderings; **band** 2.33 x population sd over the five.
- **Gap**: PRO mean minus PRIV mean. **Its band**: `pooled_band(b_PRO, b_PRIV)` =
  sqrt((b_PRO² + b_PRIV²) / 2), results_derive's band for a difference. "Within one pooled
  noise band of zero" is |gap| ≤ that.
- **The arm's ruler, in place of the anchors that do not exist (A0.0.1), FOR RULING**: the
  median over the arm's licensed worksheet scenarios of C − N in digits, with the median N
  as its zero. Each leg's position is (leg − median N) / ruler; each gap in ruler units is
  gap / ruler. It is the arm's own N-to-C range on the very frame and load the legs are read
  on, which is what a ruler per arm per frame means here.

## A0.5 Gates, FOR RULING (the threshold of 4)

- **Worksheet scenario**: LICENSED iff (C − N) ≥ 3 bands and answer mass ≥ 0.7 (the banked
  completion gate).
- **The arm is licensed on the frame if at least 4 of its 6 scenarios are.** question_word's six
  base arms licensed 6 of 6 under blame.
- **A duty leg** is gated if all five orderings read with answer mass ≥ 0.7. **A duty cell**
  (arm, pair) is gated if both legs are and the arm is licensed.

## A0.6 duty_on_base P1, operational: FOR RULING (units)

- Per family and version: the median gap over its gated non-driving pairs (prawns, 1, 3, 4,
  7). Per family: base minus release.
- **Default: decided in ruler units, PASS on a family if base minus release ≥ 0.16 of the
  N-to-C range**, which is 0.5 digits on the base arms' pooled median ruler (3.1 digits,
  question_word). **PASS overall on at least 4 of 6 families.** The same test in raw digits at 0.5
  is reported beside and decides nothing. Alternative: raw digits decide, as the instruction
  wrote, with the ruler figure beside.
- A family with no gated non-driving pair on either version counts as not exceeding.

## A0.7 duty_on_base P2, operational

- On the 30 base cells (6 models x 5 non-driving pairs): count |gap| ≤ pooled band. **PASS at
  20 or more.** An ungated cell counts as not within: "nothing there" must be shown, not
  inferred from a missing read.

## A0.8 duty_on_base P3, operational: FOR RULING (all gated arms)

- On driving (pair 5): **PASS iff |gap| ≤ pooled band on every gated arm, base and release**;
  the count and the arms outside are reported. UNTESTABLE if no arm is gated.
  Alternative: on at least 10 of 12.

## A0.9 The four outcomes, registered

| duty_on_base P1 | duty_on_base P2 | Reading |
|---|---|---|
| PASS | FAIL | **Residue**: the base gives the private person more of the allowance than the release does. Supports the claim that pretraining carries its structure and post-training overrides it. |
| FAIL | PASS | **Nothing there**: the base does not distinguish the legs. The allowance is not in evidence at the base; strict causal blame is. |
| FAIL | FAIL | **The base distinguishes the legs, no more than the release**: whatever separates them is in the weights before post-training and is not reduced by it. The null for the residue claim. |
| PASS | PASS | **Both**: base gaps inside the band and releases' gaps negative; the release blames the private person more than the professional. |

duty_on_base P3 qualifies every row: a driving gap outside the band on an arm says that arm separates
the legs on something other than the role, and its other gaps are read with that beside them.

## A0.10 Also recorded

Per arm and pair: both legs' means, positions on the ruler, bands, answer masses and gate;
the professional leg alone (base against release); the worksheet scenarios' N, C, band and
gate; and, for the base arms, **the reproduction check: the largest |ev difference| between
this card's worksheet cells and question_word's banked blame read** (question_word reproduced local_frames to
1.2e-6 on the same card class).

## A0.11 Price, and the card

- **Time**, from question_word on the same card class: gemma-2-9b's 37 GB downloaded in 5 min 39 s
  (about 110 MB/s), and a load plus 930 worksheet cells took 382 to 568 s per arm. Here: 252
  GB to download (about 38 min) and 370 cells per arm (about 4 min each with the load, 50 min
  for twelve), plus about 15 min of boot, venv and checks: **about 1 h 45 min**.
- **Cost at the logged $0.53/hr: about $0.93**; $1.33 at 2 h 30 min. **Card cap $6**, as the
  instruction sets, which is about 11 hours.
- **Container disk 100 GB**, weights on the overlay, each arm's weights deleted once its
  artefacts are written and its consumption checks pass (`duty_on_base_pod_batch.sh`), so
  the peak is one repo (37 GB) plus the venv.
- **Shut down**: the instruction says to shut the pod down the moment the last model is read.
  Before that, every artefact is pulled to the Mac and verified by sha256, and mirrored to
  the NAS, as the standing rule requires; the pod is then terminated without waiting.

## A0.12 Order of work

0. **Now: STOP with the estimate.** No pod is rented.
1. On ruling: freeze the frames, pin the sha, run the selftests (analysis 7 of 7) and the CPU
   dry run again on the frozen file, commit and push.
2. Rent the A6000, deploy the committed tree, run `duty_on_base_pod_batch.sh`.
3. Pull and verify, mirror, terminate. Analyse (`analyse_duty_on_base.py`, written before
   the pod), report.

## A0.13 Written before any result: what each outcome would mean

The claim is that pretraining compresses the structure of the allowance, the thought that a
person who did something as a favour is owed some slack, and that post-training lays rules
over it. **A residue result** would be the claim's first direct support: on one frame and one
load, the checkpoint before post-training gives the private person more slack than the one
after, so whatever the releases withhold was present before them. It would also make the
larger checkpoints worth reading. **A nothing-there result** would cut against the claim at
its root: the base would treat a careless favour exactly as a careless trade, so the allowance
the side-by-side condition elicits from deployed models would have to be installed later, by
post-training or by the comparison itself, and strict causal blame would be the base
disposition. **Both failing** would say the legs are separated before post-training and not
reduced by it, which supports neither the residue story nor its absence: the separation
would be in the weights, and post-training would be neutral to it. **Both passing** would say
post-training makes the private person worse off, which would be a finding about alignment
rather than about pretraining. In every case this is a reading on the worksheet, on 7 to 9
billion parameter models, of a gap between two separately read cases, and it says nothing
yet about how the stated slack, which a base model cannot be asked for, compares.

# Ruling (the author, 2026-11-06, before any pod)

1. **The ruler (A0.4)**: "each model's own median C − N from the same load is the right
   substitute; accepted, and the prawns point is exactly why."
2. **Units (A0.6)**: "ruler units decide (0.16 of the model's range), with raw digits
   reported beside. The paper's rule exists for this reason."
3. **Release on the worksheet (A0.0.3)**: "accepted, with the caveat recorded as you've
   worded it: this compares base and release on one frame; it says nothing directly about the
   deployed models."
4. **Both predictions passing (A0.9)**: "register the four readings as drafted."
5. **Licence (A0.5)**: "4 of 6 scenarios, as the default."
6. **duty_on_base P3 (A0.8)**: "at least 10 of 12, not every model. Driving is a control, and one
   model's noise shouldn't decide it." **Operational: PASS iff |gap| ≤ pooled band on at
   least 10 of the 12 arms; an ungated arm counts as not within; UNTESTABLE if none is
   gated.** `analyse_duty_on_base.py` changed accordingly before the freeze, with paired tests
   (10 within passes, 9 fails); selftest 7 of 7.
7. **Access**: "if a release's weights aren't available on the token, that model is unread
   and reported, not substituted." **Checked on the author's pointer, 2026-11-06: the deploy's token
   fetched config.json from gemma-2-9b-it, Llama-3.1-8B-Instruct
   and the other six release or gated repos; all have access.**
