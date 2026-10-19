# completeness_fill amendment

2026-10-17: one consolidated v1.1 fill.

**Committed before any call. No reading of any cell below exists at the time of commit.**

This amendment registers the rulings (2026-10-17) on the completeness audit (its
proposal, `AUDIT_AND_PROPOSAL.md`, pinned by sha256 below). It
provides for one amendment, one bank build, one clean-clone read, one ingest and one
recompute.

**It supersedes** the prawns neutral-sentence amendment of 2026-10-17. That amendment and
its Addendum 1 are incorporated by reference as group H4.
Nothing they fixed changes, except the three rulings recorded under H4 below.

**The cell lists are the audit's, pinned by sha256.** Each group names the file and the
filter that selects its cells. A rebuild of those files cannot move a cell into or out of
a group.

| file | sha256 |
|---|---|
| `excuse_empty_classified.json` | `93225d9caaaed2ca299c4289fedaab4542bb27633704b32667fd7a2d16c34ef8` |
| `duty_empty.json` | `3ce1cfe069b21880d30cac156b7e59571897f1e506d91bdcd938a3c8b1fae3f6` |
| `later_empty.json` | `7599c2c001bca3061e48bf6a41951cd28c847c11c86ff62b62c9265dcc80770e` |
| `costs.json` | `151a38d3b425c5ac6a346b7fe35ca5faadffb82098879816b51adb50eea69847` |
| `EMPTY_CELLS.md` | `dd2718c3e14d0823cd9e91d2e048691deef634b089e8b6377dd53de767f8b04d` |
| `AUDIT_AND_PROPOSAL.md` | `e77dd02a9c79148987f1ecb4eedd9c9e24b2af27e1395396ad53eb879c196c00` |

The registered numbers are those of database **781e1e83** (the results database,
sha256 `781e1e836eeb45cef95cc55686c0828f4bc35791ebbd7c71713704becdf84a6b`), 799 ids.

## 0. Rules for every group

- **Wires and draws:** each arm reads on its own banked wire for the channel group, taken
  from due-care-eval `models/` (61 entries at `ba96e18`; `wire_sha` equal to the
  harness's). Draws are the entry's, with the exceptions ruled below. One provider, no
  fallbacks. The served model is recorded and must be constant per cell.
- **The void rule:** a cell losing more than 10% of its draws to voids, truncation
  included, is reported with its void count and not used. Counts are per cell, never per
  arm.
- **Qwen3-235B:** every group's cells are read if the re-probe on or after 2026-10-18
  17:00 BST answers on GMICloud. Otherwise every Qwen3-235B cell is recorded UNREAD with
  the response.
- **Qwen3-30B:** recorded UNREAD in every group, because StreamLake, its banked
  provider, no longer serves it. No other provider is substituted.
- **deepseek_s:** remains a check readout, shown and not counted
  (the study's one-readout-per-model rule).
- **Provenance and pre-flight:** see §3.
- **New cells only:** new cells enter the database as dated readings under this
  amendment. No banked cell changes.

## 1. The groups

### H1: bicycle gaps (306 cells). FILL.

- **Cells:** `excuse_empty_classified.json`, `cls == "H"` and `grp == "E-bicycle"`.
- **Arms, cells each:** gpt6l_r, gpt6l_s, gpt6s_r, gpt6s_s, grok43_r, grok43_s and
  haiku_s 26; mistral24b 24; haiku_r 22; deepseek_r 20; gemma27b 10; claude, deepseek,
  deepseek_s, gemini_r, gpt4o, kimi, llama70b and qwen80b 6.
- **Texts:** banked (due-care-eval `banks/excuse_cases.jsonl` and
  `excuse_questions.json`, v1.0, unchanged).
- **Wire:** each arm's `bicycle` block.
- **Reason:** §3.3 says "all four single-case questions on every role (except Reasonable
  and Careless on anchors N and I)". This fill makes that true.
- **Ids it may move:** Table A.8 and ids 327 to 335 (denominators n = 75 and 67), 399 to
  448 and 564. mistral24b's roles: ids 294 to 301, 341 to 353, 561 and 562. gemma27b's I
  lifts the "I was not read" footnote on its bicycle gate (A.2).

### H2: gpt6s_r on the cheque (15 cells). FILL.

- **Cells:** `excuse_empty_classified.json`, `cls == "H"` and
  `grp == "E-gpt6sr-cheque"`.
- **Why they are empty:** deployed_scenarios stopped mid-family. The recovered cells are
  in its record recovered from the call log; these 15 were never logged.
- **Wire:** gpt6s_r's `scenarios` block, 20 draws.
- **Ids it may move:** 290 to 303, 341 to 353, and gpt6s_r's rows of A.2, A.5 and A.8.
  The I clause of gpt6s_r's gates becomes evaluable.

### H3: cells present but empty (13). FILL.

Twelve were checked as void rows in `cells` at 781e1e83. The thirteenth sits in gpt6s_r's
Blame-only bicycle read, with no row in `cells`.

- **gpt6s_r** (scenarios wire, 20 draws), 9 cells:
  - I on Blame: bicycle, cheque, prawns_home, prawns_restaurant;
  - prawns_home BYSTANDER on Blame and on Cause;
  - prawns_restaurant C on Reasonable and on Careless;
  - scaffolding P1 on Reasonable.
- **gemini_r** (bicycle wire), 2 cells: bicycle C on Cause; bicycle P2_other on Careless.
- **claude** (scenarios wire), 2 cells: prawns_home P2_other on Reasonable and on
  Careless.
- **Rule:** each new reading is a dated reading. The empty row stays as banked.
- **Ids it may move:** as H2, and claude's and gemini_r's rows of A.5 and A.8.

### H4: prawns neutral sentences and the full-text joint prompt. FILL, as built.

- **Incorporated by reference:** the prawns neutral-sentence amendment and its Addendum 1.
  That
  covers the three neutral sentences and their six hashes, the two full-text joint
  prompts and their hashes, the rules they were built under, the pooled wording floor as
  primary, and the arms.
- **Built bank:** due-care-eval branch `v1.1-prawns`, commit `fb0915d`,
  `banks/duty_texts_v1_1.jsonl`, 8 rows.

**Three rulings change Addendum 1:**

1. **mistral24b's full-text joint prompt is read at 20 draws**, matching its own summary
   read.
2. **The full-text stated slack becomes PRIMARY for prawns.** The summary reading stays
   as the original record, reported beside it. This reverses Addendum 1's "the banked
   summary prompt stays primary". From the recompute on:
   - prawns' stated gap, share, verdict, stated-condition class and signal-to-noise
     come from the full-text prompt;
   - the summary-based values are kept and reported as the original record.
3. **The same-session re-read of the summary prompt is IN** (`conditions=joint`, 2 cells
   per arm, each arm's `duty_comparison` wire). The full-text and summary prompts are
   then compared like for like, read in one session. The registered comparison is now:
   - full-text minus same-session summary, beside full-text minus the banked summary;
   - each judged against √2 × the arm's draw floor.

**Cells:** 132 neutral, 44 full-text joint, and 44 summary re-read, over 22 arms (Qwen3-30B
unread; Qwen3-235B conditional).

**Ids it may move:**
- **The pooled floor** (18 deviations replacing 15): the 171 ids referencing a floor or
  margin, among them 342, 454 to 464 (even ids), 470, 487, 502 to 509, 576 to 582, 587,
  588, 591, 592 and the class margins 595 to 728. Also Figure 7 (677 to 728), Table A.4
  and Table A.9.
- **Primacy of the full-text stated slack:** every id using prawns' stated gap. That is
  566, 567 (Figure 5), 569, 571, 578 and 586, plus the prawns rows of Table A.4
  (130 to 230) and Table A.9, and every pooled duty figure that includes prawns (ids 135
  to 229 in A.4, 566 to 583, 593, 594).

### H5: prawns reference case (comparand). FILL.

- **Texts:** 2 new rows, approved 2026-10-17. Each is built by pair 5's literal rule:
  "Reference case (for comparison only): " + the other leg's separate case with "Alaric"
  replaced by "Another man" + " Case to rate: " + this leg's separate case. The same rule
  reproduces all ten banked reference cases (pairs 1, 3, 4, 5 and 7, both legs) byte for
  byte.

| leg | sha256 | chars |
|---|---|---:|
| pro | `4646bca7d34c03d58a72fe1ec9dff887ac7598584635bef82871c882e50f6a2b` | 350 |
| priv | `46b58c2c0a0695e29203e29d279ed23e6dd7ce51292504d413d14ffce7aede26` | 350 |

- **pro:** *Reference case (for comparison only): Another man served the prawns to his
  guests without checking the date or smelling them. They had gone off. Three of the guests
  were ill. Case to rate: Alaric is a chef at a restaurant. He served the prawns to his
  diners without checking the date or smelling them. They had gone off. Three of the
  diners were ill.*
- **priv:** *Reference case (for comparison only): Another man is a chef at a restaurant.
  He served the prawns to his diners without checking the date or smelling them. They had
  gone off. Three of the diners were ill. Case to rate: Alaric served the prawns to his
  guests without checking the date or smelling them. They had gone off. Three of the
  guests were ill.*
- **Question:** Blame, the banked body and digit system message, as on the other pairs.
- **Wire:** `duty_separate`, banked draws.
- **Cells:** 44 (22 arms × 2 legs).
- **Analysis:** the remedy effect against prawns' own neutral baseline (H4), exactly as
  pairs 1 to 7 (duty_remedies and duty_hair_dye, Amendment 2).
- **Ids it may move:** 590 to 592 (n = 77 cells) and the comparand class counts.

### H6: prawns duty CAUSE. FILL.

- **Text:** 1 new question, approved. One question serves both legs.
  - Body: `cause_prefix` + "the illness" + `cause_suffix` from deployed_scenarios' frozen
    frames,
    sha256 `1d11458b5b8bcaf8590ed3a6c35565b5a76a27921627eb3baee454616d06fc05`.
  - *"{item} How much did {agent} cause the illness, on a scale from 0 to 9, where 0
    means not at all and 9 means entirely? Answer with a single digit."*
  - Asked of the bare separate case on both legs, under the digit system message.
- **duty_hair_dye's harm-noun rule:** "illness" occurs in neither leg's case, so the question
  is the same on both legs. The excuse-test nouns ("the diners' illness", "the guests'
  illness") are not used, because they would differ between legs.
- **Wire:** `duty_separate`, banked draws. **Cells:** 44.
- **Ids it may move:** none registered.

### H7: syllogism_duty on prawns. FILL, and POOL with the other pairs.

**Text A** (1 new, approved): syllogism_duty's frozen template (its frozen frames,
`texts.A_template`), head + private phrase + mid + professional phrase + tail, under run
syllogism_duty's yes/no system message.
- Private phrase "a person serving prawns to his guests"; professional "a chef". The
  rule is A0.1's: "at home" only where the case places it at home, which the prawns case
  does not.
- Body sha256 `75ad914528a3175fce18d380a2f52b3a3e9dffad3c8800e781e829a34ab15ee3`; prompt
  sha256 `37ad821db33b383678e36191f8102fcb6fcc36e26c584465c6e982012849bda7`.
- The same assembly reproduces pair 5's banked A byte for byte.
- *"Under the standard of care, is a person serving prawns to his guests held to a less
  strict standard than a chef who does it for payment? Answer yes or no."*

**Text B** (mechanical): the banked prawns separate case, a blank line, then syllogism_duty's B
questions verbatim, under syllogism_duty's B system message. The rule reproduces pair 5's banked
B prompt.

| | user sha256 | prompt sha256 |
|---|---|---|
| pro | `c4de0dc45995409bdb72efbc0819c1dfa1517c6739b2d046fdc181e0c23fc5b2` | `3ff7e8a69ec039f89c79df19065c67dc035fa429ac659a0e0645cf4daa87bbee` |
| priv | `5c14e1cc57518056b012d6d82f4df5f474a98a9918bc28814ac939b4f2c2ca89` | `dca51dc28a01e728d0df45f586b34a2c1c41936bf30917bf56e7ad56eb69cc74` |

**The rest, as syllogism_duty:**
- The same-session bare re-read on both legs, as syllogism_duty did for the other pairs.
- syllogism_duty's 13 reasoning-off arms, on syllogism_duty's settings: A at 10 draws per pair, B at 10
  per cell.
- **Cells:** 65 (`later_empty.json`, syllogism_duty, `grp == "L-233-prawns"`).

**Pooled:** prawns joins the other pairs in syllogism_duty's counts.
- syllogism_duty.P1's "yes on all four pairs other than driving" becomes "all five".
- Every "of 4" becomes "of 5".
- The comparands for prawns (stated gap, separate gap, floor) are frozen at ingest from
  the H4 recompute, in the manner of syllogism_duty's own frame build.

**Ids it may move:** 449 to 470 (syllogism_duty, §4.2 and Table A.10).

### H8: the reasoning arms in reasoning_traces, prevention_paraphrase, practical_syllogism, syllogism_duty, general_principle and subject_identity. SPLIT RULING.

**D, by design, recorded and not read:** prevention_paraphrase, practical_syllogism and
subject_identity on the reasoning arms
(deepseek_r, gemini_r, gpt6l_r, gpt6s_r, grok43_r, haiku_r).
- 324 cells: 14, 19 and 21 per arm.
- Gemini 3.1 Pro's 54 cells in the same runs fall under the same ruling (see C1).
- **Reason (2026-10-17):** these readings test why fault blindness occurs. With
  reasoning on, most models do not show it, so the syllogism and the naming test have
  nothing to explain on those arms.

**FILL, as a SEPARATE STRATUM** reported beside the non-reasoning results and never
pooled with them:
- syllogism_duty on the six reasoning arms and Gemini 3.1 Pro, 30 cells each (prawns included);
- general_principle on the same seven arms, 5 cells each;
- reasoning_traces's trace re-read on Gemini 3.1 Pro, 12 cells.
- **Cells:** 257 (`later_empty.json`, `grp == "L-reasoning-arms"`, syllogism_duty,
  general_principle and reasoning_traces).
- **Texts and settings:** each run's own frozen texts (syllogism_duty's and
  general_principle's frozen frames, reasoning_traces's coding guide). Each arm on its banked `duty_separate`
  wire (reasoning) and draws.
- **Ids it may move:** none existing. The stratum's figures are new ids.

### C1: Gemini 3.1 Pro on the excuse test. IN.

- **Wires:** `bicycle` and `scenarios` blocks identical to its `duty_separate` wire
  (`google/gemini-3.1-pro-preview`, provider `google-vertex`, max_tokens 8192,
  temperature 1.0, `want_logprobs` false, reasoning `"vendor_default"`). Readout
  "sampled", 10 draws. `wire_sha` is `94f0bcfaa46e2539228727327fda0d10`, equal to its
  duty wire's.
- **Cells:** 224. These are the eval's 216 chat cells (all ten roles, four questions,
  Reasonable and Careless not asked of N and I) **plus the 8 SUPPLIER cells** on the two
  food scenarios.
- **Why SUPPLIER is included:** the other deployed arms were read on SUPPLIER
  for the food scenarios, and a new arm should be complete in the same cells as the
  rest. 2,240 calls.
- **Registration:** read later, like gemini_pro_fill. Reported in the fault-blindness results
  with that status.
- **Its 54 cells in prevention_paraphrase, practical_syllogism and subject_identity are NOT
  read** (H8, D).
- **Ids it may move:** the fault-blindness counts that range over deployed arms. That
  includes ids 223 to 230, 290 to 303, 336, 337, 339 and 340 (which name it), and A.2,
  A.5 and A.8, which gain a row.

## 2. Recorded and not read

| group | cells | class | reason |
|---|---:|---|---|
| H8: prevention_paraphrase, practical_syllogism, subject_identity on reasoning arms, and Gemini 3.1 Pro's cells there | 378 | D | 2026-10-17: see H8 |
| C2: Yi-1.5-6B and 9B instruct on the worksheet | 124 | out | no figure uses them |
| H9: local instruct chat, CAUSE on N and I, SUPPLIER (8 arms) | 160 | out unless | read only if the local worksheet replication runs, then added to that reading; otherwise out of scope, since no figure uses them |
| H10: Yi-1.5-6B and 9B instruct, excuse test on chat | 448 | out unless | as H9 |
| One-word comparison (CMP3: chef / home / equally) | all | RETIRED | read on prawns as a check on order effects, which it showed; no result depends on it. Only the one-word choice is retired: the paired-scores comparison and H4's full-text joint prompt stay |
| Herbal pair (pair 2) | 61 | R | retired pair (ruled 2026-10-16) |
| prevention_paraphrase_rewordings paraphrases FELL, DIFF and NEGL | 189 | R | not reported (ruled 2026-10-16) |
| The audit's remaining D cells | as listed | D | each with its source in `AUDIT_AND_PROPOSAL.md` §1. Examples: API on the worksheet; Blame only on pretrained checkpoints; the duty test only on deployed models; control pair 6 supplies the draw floor |
| Qwen3-30B, every group | all | P, UNREAD | provider gone |

## 3. Provenance, pre-flight, and one open point

- **Eval groups:** H1 to H6 and C1 are read with due-care-eval from a clean clone at
  `v1.1-rc1`, with the clone's commit recorded. Every prompt is checked by `-T
  prompt_check` against a pre-flight file built **independently of the eval**, from
  the study's frames and banks. A read sending any prompt outside that file is refused
  before any call. Where the study already sent a prompt, its digest must also equal the
  study's (`replication/reference/prompt_sha16.json`).
- **OPEN, FOR RULING: H7 and H8 are not eval tasks.** The eval has no syllogism task
  (prevention_paraphrase, practical_syllogism, syllogism_duty, general_principle and
  subject_identity) and no trace-coding task (reasoning_traces). The paper repository lists
  `practical_syllogism`, `syllogism_duty`, `general_principle` and `reasoning_traces`
  as "not re-readable with the eval". There are two ways to read them:
  - **(a) Default:** read H7 and H8 in the same sitting with the study's banked readers
    (syllogism_duty's, general_principle's and reasoning_traces's readers). Each refuses a prompt
    whose sha is not the frozen one. Provenance is recorded as the study's repository at
    its commit, beside the eval clone's commit for the rest.
  - **(b)** Add those tasks to the eval before `v1.1-rc1`. That is a separate build: a
    task, a three-field parser, scorers and database views for each.
  - The amendment registers (a) unless ruled otherwise. The texts, cells, arms, settings
    and analysis above do not depend on the choice.
- **Order of work:** the bank (v1.1 files under `MANIFEST.json` "versions"), the tests
  (v1.0 byte identity over 1,386 prompts; open and refuse checks for every new condition;
  the paired-scores views reading only their own orderings), push, tag `v1.1-rc1`, STOP,
  read, ingest, and one diff of the registered numbers against 781e1e83.

## 4. No prediction

No group carries a prediction of size or direction. H4's full-text and summary comparison,
H7's pooled counts and H8's stratum are reported as measured.
