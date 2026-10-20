# prevention_paraphrase

This reading asks whether the models' answer to the prevention question ("Could Alaric
reasonably have prevented this?") survives rewording, and whether "careless" is read as a
verdict on the outcome. The deployed models were asked five yes/no questions, each in its
own call, on the careful subject (the target case) in all six scenarios and on the
careless subject of the bicycle as a check. Two of the questions are the original
prevention and carelessness questions, re-read in one session on byte-identical prompts;
that part supplies the particular premise of the practical syllogism and is reported. The
other three are rewordings (prevention_paraphrase_rewordings). They are not reported in
the paper: the rewordings measured the verdict, not the fact, because asking whether he
"fell short of the care a reasonable person would take", "should have done anything
differently" or "was negligent" asks for a judgement of fault rather than for the factual
premise the verdict rests on.

## Pre-registration

`../../../pre-registration/prevention_paraphrase.md`, banked on 2026-10-12 before any
call of this reading (the reads ran later the same day). It contains the instruction
verbatim and one amendment, made and reviewed before any call:

- **Amendment 0, A0.1 to A0.4 (frozen):** fixes the prompt layout and checks the re-read
  prompts hash to the banked ones; fixes the 15 arms, their providers, settings and draw
  counts; defines P(yes), the answer-mass gate (below 0.70 fails), the modal answer (a
  cell at exactly 0.5 has none and is excluded from AC1) and the banked gate exclusions;
  fixes the statistics (Gwet's AC1, Pearson with Spearman beside it, a 10,000-resample
  model bootstrap).
- **A0.5:** the earlier r = 0.07 was computed on continuous P(yes), not on modal answers;
  the replacement figure is justified only as a same-session, like-for-like reading.
- **A0.6:** a model is excluded from a within-model correlation if its P(yes) has sd below
  0.01, and the count of models is reported every time the figure is quoted.
- **A0.7:** the pooled figure, not the within-model median, decides prevention_paraphrase.P2.
- **A0.8:** cells with no banked comparand are listed as such in the drift check and still
  count in prevention_paraphrase.P1 and P2.
- **A0.9:** an arm whose banked provider is unavailable is reported unread, not moved to
  another provider.

The registered figures were later recounted under the study-wide rule that a model read by
two readouts counts once, by its log-probability readout (DeepSeek-V4.1-Flash; its sampled
readout is kept as a check). Nothing was re-read; only pooled figures changed.

## What was read

- **Models:** 13 of the 15 reasoning-off deployed models of Figure 1: Claude Sonnet 5,
  DeepSeek-V4.1-Flash (log-prob and sampled), Gemma-3-27B-IT, GPT-4o, gpt-6-luna,
  gpt-6-sol, grok-4.3, Claude Haiku 4.5, Kimi-K3, Llama-3.3-70B-Instruct,
  Mistral-Small-3.2-24B and Qwen3-Next-80B, each on its banked provider, temperature 1.0,
  served model constant on every arm. **Unread, not moved:** Qwen3-235B-A22B (its provider
  returned HTTP 429 throughout) and Qwen3-30B-A3B (its provider no longer serves the model).
- **Questions:** Reasonable and Careless in their banked wording; fell short, should have
  done differently and negligent (the rewordings).
- **Cells:** 7 per arm (the target case on six scenarios, the careless case on the
  bicycle), 455 in all (13 arms x 5 questions x 7 cells).
- **Draws:** 10 per cell; 20 on the bicycle cells for Claude Sonnet 5 and DeepSeek-V4.1-Flash
  (sampled). 4,750 calls.
- **Void and unread:** 0 gate failures (yes/no mass below 0.70), 0 unparsed answers, 0
  refusals on any question; on the log-prob arms the yes/no mass on "negligent" was 0.993 to
  1.000. Two arms unread (above).
- **Population:** 78 target-case cells less 3 banked gate exclusions (the cheque scenario on
  DeepSeek-V4.1-Flash, Kimi-K3 and Mistral-Small-3.2-24B) leaves 75 cells over 13 arms; with
  DeepSeek-V4.1-Flash counted once, **69 cells over 12 models**, the population of every
  registered figure.
- **Drift check:** the re-read Reasonable reproduces the banked cells to within 0.055 on
  every log-prob arm; sampled arms move by up to 0.3 on 10 draws. 17 cells have no banked
  comparand (the bicycle careless case on every arm, the bicycle target case on four arms).

## Where it is reported

- **Reported (the original wording):** the particular premise of the practical syllogism,
  §4.1 ("could this man reasonably have prevented it? The models say no in 59 of 69 cells"),
  Table 4 (the particular premise column) and Table A.10 (the Fact column); also cited in the
  abstract ("most agree that he could not have prevented it") and §5 ("several deny the fact
  in half the scenarios or more (Table 4)"). Headline figures, registered under
  practical_syllogism with this reading's Reasonable answers as the fact:
  - **431**: cells with the fact held, 59 of 69.
  - **430**: cells with both premises held, 59 of 69.
  - **432**: of those, blame position above 0.10, 47 of 59 (0.797); **436**: above 0.30,
    30 of 59 (0.508).
  - **434** and **438, 439**: the "fell short" answer conditional on both premises (21 of
    59) and its combinations with the blame position.
- **Not reported (the rewordings):** registered as not reported, ids 399 to 427.
  - **399, 403**: prevention_paraphrase.P1 AC1 for "fell short" against Reasonable, 0.4584
    (model bootstrap [0.1210, 0.7529], id 401), FAIL against the 0.60 floor.
  - **404, 408**: AC1 for "should have done differently", 0.1846 ([-0.2488, 0.6011], id
    406), FAIL.
  - **411, 415, 417**: prevention_paraphrase.P2, negligent minus careless, +0.1754
    [-0.0145, 0.3897] with Reasonable and -0.0585 [-0.1764, 0.1429] with the blame
    position, FAIL.
  - **420**: Reasonable with Careless, pooled r 0.1427 over 69 cells (the like-for-like
    replacement for the earlier 0.07).
  - **423 to 427**: the careless-case check, 12 of 12 models answer yes on every question.

## Contents

| path | files | |
|---|---:|---|
| `prompts/` | 2 | frozen prompts and the prompt check: `frames.json`, `prompt_check.json` |
| `code/` | 3 | reader and analysis scripts, as run: `analyse_prevention_paraphrase.py`, `build_prevention_paraphrase_frames.py`, `read_prevention_paraphrase.py` |
| `readings/calls/` | 15 | every call, one JSON line each; 4,750 lines: `or_claude.jsonl`, `or_deepseek.jsonl`, `or_deepseek_s.jsonl`, `or_gemma27b.jsonl`, `or_gpt4o.jsonl`, `or_gpt6l_s.jsonl`, `or_gpt6s_s.jsonl`, `or_grok43_s.jsonl`, `or_haiku_s.jsonl`, `or_kimi.jsonl`, `or_llama70b.jsonl`, `or_mistral24b.jsonl`, ... |
| `readings/records/` | 17 | per-model read records and result files: `RECOUNT_prevention_paraphrase.json`, `prevention_paraphrase_READ__claude.json`, `prevention_paraphrase_READ__deepseek.json`, `prevention_paraphrase_READ__deepseek_s.json`, `prevention_paraphrase_READ__gemma27b.json`, `prevention_paraphrase_READ__gpt4o.json`, `prevention_paraphrase_READ__gpt6l_s.json`, `prevention_paraphrase_READ__gpt6s_s.json`, `prevention_paraphrase_READ__grok43_s.json`, `prevention_paraphrase_READ__haiku_s.json`, `prevention_paraphrase_READ__kimi.json`, `prevention_paraphrase_READ__llama70b.json`, ... |

## Prompt check

4,750 of 4,750 calls in `readings/calls/` carry the hash of a prompt in `prompts/`; 35 of 35 distinct prompts were sent in this folder's calls. Per prompt: `prompts/prompt_check.json`; the method: `../README.md`.
