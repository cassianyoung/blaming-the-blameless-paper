# reasoning_traces pre-registration

Pre-registration for the trace test behind §4.3. **The instruction is reproduced
verbatim first; Amendment 1 follows and governs where they differ.** Committed before
any trace exists: no duty-test reasoning text was ever stored (step 0 below), so no
trace has been or could have been read.

## Step 0 result (2026-10-12): no trace stored

The API harness read the reasoning text off every response and logged only its length
(`reasoning_text_len`); the answer was cut at 400 characters. Every log for the six
reasoning arms was scanned (16,000+ records): **0 usable traces for any arm, pair, leg
or condition.** Providers had returned text on 64 to 100% of draws, depending on the arm;
that text is lost. The harness now keeps it.

## The instruction, verbatim (2026-10-12)

> # Instruction: do the reasoning models raise the comparison on their own?
>
> §4.3 argues that reasoning does not correct Bias 2 because a single case does not
> prompt the comparison the convention needs: judging the careless home cook alone,
> a model would have to bring in a professional who did the same thing, an
> auxiliary construction, and the results suggest it does not. The reasoning
> traces can test that directly. Retrieval and coding of existing traces only; no
> new reads.
>
> ## 0. INVENTORY FIRST, THEN STOP
>
> For each reasoning arm on the duty test (DeepSeek-V4.1, Claude Haiku 4.5,
> grok-4.3, gpt-6-luna, gpt-6-sol, Gemini 3.8 Flash, all with reasoning), report:
> whether its reasoning text is stored (full text, a provider summary, or nothing
> but token counts), and how many separate-case draws have usable text, per pair
> and leg, for the separate condition and the convention-stated condition.
>
> Report the inventory, and stop.
>
> ## 1. CODING SCHEME (freeze before reading any trace)
>
> Each trace from a **private** case read alone is coded on three questions:
>
> - **R (role):** does the trace mention the subject's role or status as bearing on
>   blame (that he is a private person, a host, a friend, an amateur, not paid)?
> - **C (comparison):** does it compare him, explicitly or by implication, with a
>   professional who did or might have done the same thing (a chef, an
>   electrician, a landlord, "someone doing this for a living")?
> - **S (standard):** does it state or apply a lower standard of care for a
>   private person than for a professional?
>
> Each trace from a **professional** case read alone is coded on the mirror
> questions (role as bearing on blame; comparison with a private person; a
> stricter professional standard).
>
> Each trace from the **convention-stated** condition is coded on whether it
> refers to the stated sentence, and whether it treats it as a rule to apply or a
> fact to weigh.
>
> Write the coding guide with two worked examples of each code, from traces you
> have not yet read in the duty data (construct them), and freeze it with its sha.
>
> ## 2. CODING
>
> Use the project's existing trace-coding approach: a keyword pre-pass to find
> candidate mentions (role nouns, "professional", "paid", "amateur", "standard",
> "duty", "expected of"), then a model coder applying the frozen guide to every
> trace, with a second coder from a different developer on a random 20% sample.
> Report agreement (Gwet's AC1) against a pre-set floor of 0.70; below it, report
> and stop. Hand-check 30 traces stratified by code and report disagreements.
>
> ## 3. ANALYSIS (pre-registered here)
>
> Per arm and pair, and pooled:
> 1. The share of private-case traces coded C (comparison) and S (standard).
>    Prediction: low, under one in five.
> 2. The same shares for professional-case traces. No prediction.
> 3. Within private cases, the mean score of traces coded C or S against those
>    not. Prediction: traces that raise the comparison give a lower score, and so
>    more slack.
> 4. In the convention-stated condition, the share treating the sentence as a rule
>    to apply, and how that share relates to over- and undershoot (§4.2.3).
>
> Report every count with its denominator. Arms whose traces are not stored are
> listed as such, never estimated.
>
> ## OUTPUT
>
> The inventory; the frozen guide and its sha; agreement; the four analyses; and
> one sentence each for §4.3 stating what the traces show, worded to the result.
> Register the headline numbers in `paper_numbers`. Nothing else in the database
> or exports changes.

## Amendment 1 (2026-10-12): a scaled re-read, text kept

Made after step 0 found no stored trace, and before any trace exists. It replaces "no
new reads" and the steps it touches; everything not named here stands as written above.

**A1.1 Scope.** Re-read the **separate condition only**, question BLAME, for the six
reasoning arms (`deepseek_r`, `haiku_r`, `grok43_r`, `gpt6l_r`, `gpt6s_r`, `gemini_r`),
over **all six reported pairs** (prawns, 1 electrical work, 3 gas safety, 4 childcare,
5 driving, 7 hair dye), **both legs**, at the **banked draw counts**: 10 per cell, 20 on
`gpt6s_r`. That is 12 cells per arm, **840 draws**. The retired pair (2) and the control
(6) are not read.

**A1.2 Same instrument.** Each arm is read on its banked separate-condition wire: same
model id, provider pinned with no fallback, same reasoning setting, `max_tokens` and
temperature, as recorded in the banked artefact. The prompt for each cell is built and
its `prompt_sha256_16` compared with the banked call's for that cell **before any call
is paid**; a mismatch refuses the cell. Prawns prompts come from the families bank with
the families frame (deployed_scenarios and deployed_added_models), the other five pairs
from the duty bank (duty_pairs and duty_hair_dye).

**A1.3 Text kept.** Through the harness version that keeps the text, or later: full reasoning text,
full answer text, `reasoning_details` and `reasoning_kinds` on every call.

**A1.4 Scores.** Traces are analysed against **the re-read's own scores**. Analysis 3
pairs each trace with the digit from the same call; no trace is paired with a banked
score.

**A1.5 Drift check, reported and not gated.** Per cell, the re-read mean against the
banked mean, with the absolute difference; per arm, the median absolute difference over
its 12 cells. The comparand is the duty test's same-session neutral-against-neutral
median on one case, **0.148 points** (paper_numbers, registered 2026-10-12). Served
model and served provider are asserted constant across the pass, and any difference
from the banked artefact's is reported.

**A1.6 The convention-stated condition is not re-read.** Its coding (step 1, third
paragraph) and analysis 4 are **not run**, and are reported as not run.

**A1.7 Two strata, coded and reported separately, never pooled across them**
(2026-10-12).
- **Full trace:** `deepseek_r`, `haiku_r`.
- **Provider summary:** `grok43_r`, `gemini_r`, `gpt6l_r`, `gpt6s_r`.

This grouping is an expectation from trace length (median 1,686 to 2,088 characters
against 295 to 458) and from the summary models' not returning text on every draw. **It
is confirmed or corrected by the recorded `reasoning_kinds`**: an arm whose recorded
kinds contradict its stratum moves by measurement, and the move is reported. "Pooled" in
step 3 means pooled **within a stratum**. Two further rules follow from the strata:
- A draw with **no reasoning text** is counted as "no trace", with its denominator. It
  is never coded as a trace that does not raise the comparison.
- **The absence of a code in a summary is weaker evidence than its absence in a full
  trace**, because a summary may omit a step the model took. The analysis 1 prediction
  (under one in five) is evaluated per stratum, and a summary-stratum result is stated
  as a property of the summaries, not of the reasoning.

**A1.8 Records.** Call logs, and one trace artefact per arm, write-once.

**A1.9 Order of work.** (i) This amendment, committed. (ii) The reader, with its
offline gate-open test and the prompt-hash check of A1.2. (iii) The coding guide with
constructed examples, frozen with its sha. (iv) The re-read. (v) Coding, agreement,
analyses. **Items ii and iii both precede iv**, so the guide is frozen before any trace
exists.

## Draws (from the banked cells)

| Arm | Draws | Median reasoning tokens |
|---|---|---|
| `deepseek_r` | 120 | 306 |
| `haiku_r` | 120 | 384 |
| `grok43_r` | 120 | 442 |
| `gpt6l_r` | 120 | 60 |
| `gpt6s_r` | 240 | 42 |
| `gemini_r` | 120 | 242 |
| **Total** | **840** | |

## Coding guide frozen (2026-10-12)

The coding guide, sha256 `52c80dfc0bdedaa73982bf1ffe3fcee061327b5be7b0e816fc0bb0ceb6101322`, frozen before the re-read: at
freezing the reading's log folder did not exist and no reasoning_traces call had been made. It fixes
three coding rules of the same day:
- **Design A**: one call per trace returns all three codes.
- **Temperature 0** for both coders, recorded with each call.
- **Strict JSON validation**: exactly R, C and S, each "yes" or "no"; one retry, then
  uncoded and never defaulted. The 20% second sample is drawn at random within each
  stratum (`random.Random(230)`).

Coders: `qwen/qwen3-235b-a22b-2507` (GMICloud) primary, `moonshotai/kimi-k3` (Sail
Research) second; neither developer is among the coded models. The coder sees the case
type, the case text and the trace, never the answer or digit. The coder instructions
run to about 1,021 words.

## Amendment 2 (2026-10-12): Gemini stays in the summary stratum

Made after the re-read and **before any trace was coded or read**. A1.7 said the
recorded `reasoning_kinds` confirm or correct the strata. On all 120 `gemini_r` draws
the routing layer labels the text `reasoning.text`, which read literally would move
Gemini to the full-trace stratum. **The stratum is decided instead by what A1.7 was for:
separating texts that are the model's whole reasoning from texts that are not.** The
length of a trace against the reasoning tokens it was billed for measures that directly;
the label is the routing layer's description of it.

The evidence, from the reasoning_traces logs (draws with both text and billed reasoning tokens):

| Arm | Label | Chars per billed reasoning token, median [q25, q75] | Median chars | Median reasoning tokens |
|---|---|---|---|---|
| `deepseek_r` | text | 4.25 [4.14, 4.37] | 1,286 | 303 |
| `haiku_r` | text | 4.24 [4.14, 4.34] | 1,610 | 382 |
| `gemini_r` | text | **1.11** [0.95, 1.36] | 277 | 256 |
| `grok43_r` | summary | 0.61 [0.48, 0.72] | 270 | 460 |
| `gpt6l_r` | summary | 7.39 [6.35, 8.90] | 455 | 63 |
| `gpt6s_r` | summary | 9.77 [8.59, 11.32] | 438 | 44 |

At the full-trace ratio of about 4.25, Gemini's median 256 reasoning tokens would be
about **1,088 characters**; its median trace is **277**, about a quarter. **Caveat:**
tokenisers differ, so characters per token is approximate across vendors. No tokeniser
for English text produces 1.1 characters per token, so the conclusion does not depend on
the exact figure. (The gpt-6 summaries run longer than their billed reasoning, so they
are generated separately from it; they are labelled summaries and stay so.)

**Gemini is also reported on its own** inside the summary stratum's results, for every
analysis, so a reader who prefers the label can see what its traces show without
regrouping anything.

Strata as coded: **full** `deepseek_r`, `haiku_r` (240 traces of 240 draws; second
sample 48); **summary** `grok43_r`, `gemini_r`, `gpt6l_r`, `gpt6s_r` (508 traces of 600
draws, 92 no trace; second sample 102).

## Amendment 3 (2026-10-12): primary coder on Nebius

The primary coder, `qwen/qwen3-235b-a22b-2507`, could not be served by GMICloud: every
call returned HTTP 429 "temporarily rate-limited upstream" (OpenRouter's shared pool)
from about 16:50 BST to the last probe at 20:13 BST. No primary call was ever answered,
so no trace has been coded by the primary coder on any provider.

The provider was switched rather than waiting. Probed
at about 20:20 BST, Parasail, DeepInfra, Venice and Google all returned the same
upstream 429. **Nebius was the only endpoint answering** and returned valid JSON on a
one-call probe at temperature 0 with reasoning off. Nebius serves the same model at the
same **fp8** quantisation as GMICloud (OpenRouter endpoint listing). So the whole
primary pass runs on Nebius, pinned with no fallback; nothing else changes: same model,
same frozen guide (sha `52c80dfc…`), temperature 0, design A, strict JSON with one
retry, same strata. Served provider is recorded per call and asserted constant.

## Amendment 4 (2026-10-12): the agreement stop applies per code; analyses on C alone

**Written and committed before any C share has been computed.** At this commit the
primary codes exist and agreement has been
computed (the agreement analysis, which stopped), but no share, count of C codes
by group or score split has been computed or looked at.

**A4.1 The stop applies per code.** §2's floor ("Report agreement (Gwet's AC1) against a
pre-set floor of 0.70; below it, report and stop") is read per code: a code below the
floor in any stratum is stopped; a code above it in every stratum goes on.

**A4.2 R and S are stopped.** They are reported with their AC1 and the direction of
disagreement, and no share or analysis uses them:

| Code | Full (48) | Summary (102) | Gemini alone (23) | Direction |
|---|---|---|---|---|
| R | 0.625 | 0.622 | 0.653 | every disagreement primary yes, second no (full 29 v 20, summary 40 v 17) |
| S | 0.574 | 0.958 | 0.897 | every disagreement primary yes, second no (full 20 v 8, summary 5 v 1) |

The reading of the 46 disagreeing traces is recorded separately: the primary misapplies the guide on 27 code
decisions, the second on 7, and the guide leaves 14 open.

**A4.3 C passed in every stratum** (full 0.955, summary 1.000, Gemini alone 1.000), so
the pre-registered analyses proceed on C alone, from the primary codes:
1. **Analysis 1:** the share of private-case traces coded C, per group (full, summary,
   Gemini alone), with per-arm and per-pair breakdowns. Prediction, as registered: under
   one in five. Read per stratum, a summary result stated as a property of the
   summaries (A1.7).
2. **Analysis 2:** the same share for professional-case traces. No prediction.
3. **Analysis 3:** within private cases, the mean score (the re-read's own digit, A1.4)
   of traces coded C against traces not coded C. Prediction, as registered: lower when
   coded C. Where the registered text says "C or S", it now reads "C".
Every count carries its denominator, with draws without a trace and uncoded traces listed
beside it. Analysis 4 stays not run (A1.4).

**A4.4 Hand check on C.** 30 traces, 15 per stratum (full, summary), stratified by the
primary's C code: within each stratum, round-robin over C yes and C no, each shuffled
with `random.Random(2301)`, so C yes gets up to half the draws if it has that many. **The
46 traces already read with both coders' codes visible are excluded from the draw**, so
the hand coder (an AI assistant) codes blind, from a sheet showing case type,
description and trace only. C only is coded. Disagreements with the primary are reported
one by one, with the reason; the hand check is reported, not gated.

**A4.5 Records.** The C-only analysis writes its own record (write-once); the agreement
analysis's record stays as the record of the stop.
