# PREREG yi_adapter_controls: is it the en_corpus corpus? Controls for the Yi result

Written and committed **before anything trains**. 2026-09-30.

## 0. THE RESULT UNDER TEST

On `01-ai/Yi-1.5-34B` (revision `58a29f6dca2a4eda38821c086c29c1906114aabb`), which is
the only base arm in local_tuning with the reasonable-care shape (P0 position 0.164, every
careful-agent row inside 1.4 bands of N, C at 7.02 bands and I at 11.30):

    arm                        P0 position   P0 - N digits   P0 - N bands   adapter digest
    yi34b_base                       0.164          +0.401           1.15   -
    yi34b_adapter_en_corpus             0.349          +1.153           3.95   e2465c9d89ab67e8
    yi34b_adapter_zh_corpus             0.186          +0.472           1.49   4c96ef616f13b3c4

en_corpus raised P0 - N by **+2.80 bands**, past the ruled two-band line. zh_corpus, same LoRA
spec and step count, moved it **+0.34**.

**TWO CONFOUNDS REMAIN.** Language: zh_corpus is Chinese and the evaluation is English.
Seed: each figure is one training run.

## 1. THE RULE FOR "A RISE", FIXED HERE

A **RISE** is `P0 - N` greater than **2.00 bands above the base arm's**, where:

- a row's value is the **MEAN of its ev over that arm's permutation frames**;
- the **band** is the mean over {P0, P1, BYSTANDER} of `2.33 x pstdev` across those
  same frames;
- `P0 position = (P0 - N) / (C - N)`, from the same means, is **reported beside it** and
  never substituted for it.

This is the single construction ruled on 2026-09-30. Frame-1 numbers are not used.
Base arm comparand: **P0 - N = 1.15 bands** (five permutations) / **1.02** (ten). The
two-band test is applied against the five-permutation figure, because every arm below is
read on five.

Every arm is also reported with **C - N bands, answer mass, mass(0-3) and its adapter
digest**, and no arm is excluded for showing or not showing the effect: `P0 - N` is the
OUTCOME and never gates (ruling of 2026-09-30).

## 2. MATERIAL, BY SHA

    base model     01-ai/Yi-1.5-34B   rev 58a29f6dca2a4eda38821c086c29c1906114aabb
    en_corpus         instruction_corpus_en.jsonl                             960 pairs
                   sha256 8df234ca2d836eeb51d750e9800e8564efc69c653f4181b5c0aeb9f0ac26f87f
    zh_corpus  instruction_corpus_zh.jsonl                958 pairs
                   sha256 bf17099b553052d4e761aa24b189a92529670102427dddd15e3d761c60e34bb3
    lora_spec      v2, digest 89b8d51ca119be9a  (r 32, alpha 64, dropout 0.05,
                   q/k/v/o/gate/up/down, 2 epochs, lr 1e-4 cosine, batch 4 x 4,
                   max_seq 512, bf16)
    steps          120 (60 per epoch at effective batch 16)
    masking        character_offsets / offset_span_equals_completion

## 3. SEEDS, AND A DESIGN DECISION THAT HAS TO BE DECLARED

**DECLARED SEEDS: the original 20260909, plus 20260910 and 20260911.** Chosen as the two
days after the banked seed, before any training, and recorded here so they cannot be
chosen after a result.

**THE TRAINER HAS NO SEED FLAG, BY DESIGN.** `school_tune_instruments.LORA_V2` carries
`seed: 20260909` and `school_tune_tune.py` has no overrides: *"the choice is between two
committed dicts, each with its own digest, and neither can be edited from the command
line"*. Step A therefore needs one of two changes, and the choice is declared here:

- **CHOSEN: add `--seed`**, which overrides ONLY the seed, is written into the manifest
  and the provenance block, and leaves `lora_spec_digest` unchanged because the spec is
  unchanged. A run without the flag is byte-identical to today's behaviour.
- Rejected: banking two new spec dicts differing only in seed. It would give each a
  distinct digest and make three runs of one recipe look like three recipes.

**THIS IS A REPLICATION, NOT A SEARCH.** The §5 rule against hyperparameter sweeps is
about searching for a tune that certifies. Here **all three seeds are reported whatever
they show**, the reading is fixed below before they run, and no seed may be dropped.

## 4. THE THREE PRE-REGISTERED READINGS

**STEP A, seed replication.** Train en_corpus on Yi at seeds 20260909 (already done),
20260910, 20260911. Read each on completion, ten rows, five permutations.

- **all three rise (> 2 bands)** -> the effect is the corpus, not the draw
- **one of three rises** -> the original was the seed, and the local_tuning finding is withdrawn
- **two of three** -> `__UNLABELLED`; no sentence is written for this in advance and none
  will be invented afterwards. The three values and their spread are the result.

**STEP B, language against content.** An English control corpus of 960 pairs.

- **English control flat, en_corpus up** -> the content of en_corpus
- **both up** -> English instruction tuning in general, not en_corpus specifically
- **translated zh_corpus up while Chinese zh_corpus was flat** -> the language, not the content

**STEP D, ablation** (only if step C finds the register materially present). Remove the
flagged pairs and replace them with the same number of unflagged en_corpus pairs, so the set
stays 960. **REPLACEMENT RULE, DECLARED NOW: the replacements are drawn from the
unflagged en_corpus pairs not already in the set, in file order, and if there are not enough
the set is reported short rather than padded from elsewhere.**

- **P0 within 2 bands of base** -> the flagged register is the carrier
- **still up** -> it is something else in en_corpus

## 5. WHAT WAS ALREADY KNOWN BEFORE ANY TRAINING, AND TWO ALTERNATIVES IT RAISES

Counted from the two banked sets before step A was queued. Recorded here so it cannot
look like a post-hoc account.

    source class                       en_corpus        zh_corpus
    general instruction pairs             769                     767
    predicate / rating pairs              191                     191
      of which DIGIT-RATING                79                     191
      of which PROSE JUDGEMENT            112                       0

**ALTERNATIVE 1, AND IT IS BETTER SPECIFIED THAN THE CAUTIONARY REGISTER.** The two
corpora carry **exactly the same number of rating pairs, 191 each**, so a bare
rating-format count cannot explain the difference. What differs is their KIND: en_corpus has
**112 pairs whose completions are PROSE JUDGEMENTS ON BORDERLINE PREDICATES**
(`predicate_heap` 46, `predicate_tall` 35, `predicate_weight` 31), e.g.
*"Q: Someone is 58.5 inches tall. Are they tall? A: Not especially; that is around
average."* zh_corpus has **none**: all 191 of its rating pairs are bare digits.
Prose judgement on a borderline case is far closer to *"how much is he to blame"* than a
bare digit is. **So step C codes for this as well as for the cautionary register**, and
both codes are declared here before any pair is read.

**ALTERNATIVE 2, LENGTH.** The two sets do not match in length and step B cannot make
them: en_corpus completions are mean 165 / median 71 characters, zh_corpus's are mean 243 /
median 144, and translation from Chinese to English lengthens text further. **The
errand's two step-B requirements are in tension** ("same length distribution as en_corpus"
and "preferred: zh_corpus translated"), and translated-zh_corpus is chosen because it holds
CONTENT fixed and changes only language, which is the confound under test. **Length is
therefore NOT matched in step B and is reported as an uncontrolled difference**, with
both distributions given.

## 6. STEP C's CODES, DECLARED

1. **CAUTIONARY / RESPONSIBILITY REGISTER**: precautionary imperatives ("always check",
   "make sure to", "be sure to inspect"), responsibility or duty language ("it is your
   responsibility"), safety and liability caveats.
2. **PROSE JUDGEMENT ON A BORDERLINE PREDICATE**: a completion that renders a graded
   verdict in words rather than a digit or a fact.

Pattern-based first pass with **every hit written out with context**; then a **blind
second coder** that has not seen this document, on all flagged pairs plus a random 100
unflagged. Counts, agreement and a sample reported for en_corpus, translated zh_corpus and the
step-B control side by side.

**A CODE THAT FIRES ON NEARLY EVERY PAIR IS CODING THE FORMAT, NOT THE REGISTER.** Run
216 produced two instances of exactly that (a duty pattern matching the restated stimulus
at 140 of 140, and a degeneracy predicate pinned at its failing end), so a rate above
roughly 60 per cent is treated as a broken code and reported as one before it is believed.

## 7. WHAT WOULD MAKE ME WRONG

The local_tuning result is withdrawn if step A gives one rise in three. It is narrowed to
"English instruction tuning" if step B's control also rises. It is attributed to language
rather than content if translated zh_corpus rises where Chinese zh_corpus did not. Each of
those is written above with its outcome fixed, and the figures are reported whichever
fires.

---

## 8. AMENDMENT, MADE BEFORE STEP A RAN AND DECLARED AS ONE

Added 2026-09-30, hours after §1 and **before any yi_adapter_controls training**, on evidence from
recomputing local_tuning's Q2 on the single construction.

**§1's rule is band-only and that is not sufficient.** Adapters TIGHTEN the band, so a
band-normalised shift can be almost entirely the denominator:

    family        base band  adap band   d digits   d bands   d position
    qwen3             0.987      0.435     +0.077     +3.03       -0.083
    gemma27           0.277      0.187     +0.204     +5.38       +0.018
    llama31           0.399      0.323     +0.467     +2.94       +0.032
    stablelm12b       0.427      0.357     +0.769     +2.74       +0.109
    yi34b (en_corpus)    0.349      0.292     +0.752     +2.80       +0.186

A two-band test on `P0 - N` alone calls **five of nine** local_tuning families a rise. In the
two units a shrinking denominator cannot inflate, **two** move: digits over +0.5 and
position over +0.10 both name `yi34b` and `stablelm12b` and nothing else.

**AMENDED RULE.** A **RISE** requires all three of:

1. `P0 - N` up more than **2.00 bands**; AND
2. `P0 - N` up more than **0.50 digits**; AND
3. `P0` position up more than **0.10**.

Any arm satisfying some but not all is reported as **`__PARTIAL`**, with all three columns
given and no sentence invented for it. Both bands are also reported for every arm, so a
reader can see whether the numerator or the denominator moved.

**This is the ruling of 2026-09-30 on the negligence table**: a band-normalised figure
conceals which term changed, so raw digits travel beside bands.

**AND ONE local_tuning CLAIM IS NARROWED BY THE SAME RECOMPUTATION.** "The en_corpus adapter does
not move the ladder on any family" was read from frame-1 positions and is withdrawn. On
the single construction it moves two of nine. Yi remains the only family where the move
happens on a base that did NOT already have the bias (base position 0.164 against
stablelm12b's 0.514), which is what makes it the informative case, but it is no longer
the only family where en_corpus moves P0.

---

## 9. AMENDMENT, MADE AFTER STEP C AND BEFORE ANY STEP D WORK, DECLARED AS ONE

Added **2026-10-01**, on the rulings on step C. Appended, not edited into the text
above: §4 and §6 stand as written and are the record of what was predicted.

### 9.1 WHAT STEP C FOUND

Corrected rates are `p*f + q*(N-f)`: precision `p` from three blind coders on the
pattern-flagged set `f`, unflagged positive rate `q` on a random 100, Wilson 95% on `q`
carried through. Raw flags beside every estimate.

    code              corpus     raw flags      precision   corrected    95%
    CAUTIONARY        en_corpus       12 (1.25%)    7/12  .58      1.72%   [0.90, 6.11]
                      zh_corpus      116 (12.11%)  58/116 .50     12.21%   [9.07, 18.14]
    PROSE_JUDGEMENT   en_corpus      112 (11.67%)  112/112 1.00   14.32%   [12.57, 19.13]
                      zh_corpus        0 (0.00%)     none          0.00%   [0.00, 3.70]

**The cautionary register is NOT materially present in en_corpus and is INVERTED against
zh_corpus**, intervals not overlapping, and the inversion survives correction for precision
(poor on both sides, 0.58 and 0.50), for completion length (7.1x per pair falling to
4.81x per character) and for the advice-against-topical split (5.3 pairs against 51.7).
**PROSE JUDGEMENT separates the two corpora in the direction the local_tuning result needs**,
also without overlap, at precision 112 of 112.

**RULING 3 OF 2026-10-01, CARRIED HERE BECAUSE IT BINDS THE WRITE-UP.** The zh_corpus
cautionary MAGNITUDE may not be quoted in the paper unless a native Chinese reader has
checked the thirty rows. No one on the project reads Chinese. What may be reported is that **the cautionary hypothesis was
not supported**; the decision needs no more than that, because the inversion holds at
the poorest precision measured.

### 9.2 §4 NEVER NAMED WHICH CODE'S FLAGS STEP D REMOVES

§4's step D says "remove the flagged pairs" and gates itself on "step C finding the
register materially present". §5 then required step C to code for prose judgement "as
well as for the cautionary register". **So §4 was written when there was one candidate
register and step C returned two codes with opposite results.** The gate reads NOT
MATERIALLY PRESENT for the cautionary register: 16.5 estimated pairs of 960, 5.3 of them
judged genuine advice, and ablating five pairs cannot move a tune. **No ablation is run on
the cautionary code.**

### 9.3 THE TARGET NOW CHOSEN, AND WHEN THE CHOICE WAS MADE

**Step D's removal set is the 112 structural PROSE_JUDGEMENT pairs** (`source` matching
`predicate_(?!rating_)`: `predicate_heap` 46, `predicate_tall` 35, `predicate_weight` 31).

**PROSE_JUDGEMENT is a code this prereg declared in §5 and §6 before any pair was read.
Its DESIGNATION AS THE ABLATION TARGET is a decision taken AFTER seeing step C's results
and BEFORE step D runs, and is recorded here as such.** The two facts are different and
collapsing them would overstate what was predicted: the code was pre-registered, the
target was not.

### 9.4 THE REPLACEMENT RULE, IN FULL

1. **Remove** the 112 structural PROSE_JUDGEMENT pairs.
2. **Insert** 112 unflagged en_corpus pairs, **matched on completion length by
   nearest-neighbour without replacement**: the removed pairs are taken in ascending
   completion length with `uid` as tie-break, and each takes the not-yet-used unflagged
   pair whose stripped completion length is closest, ties broken by `uid` after a shuffle
   seeded at **20261001**.
3. **The set stays 960.** Training seed is **en_corpus's original 20260909**, so the only
   variable against the banked `yi34b_adapter_en_corpus` is the swapped pairs.
4. Everything else is unchanged: `lora_spec` v2 digest `89b8d51ca119be9a`, 120 steps,
   `character_offsets / offset_span_equals_completion` masking.

**A HARD LENGTH WINDOW WAS REJECTED BECAUSE IT CANNOT SUPPLY THE SET.** Only **100** of
the 848 unflagged pairs fall inside the removed pairs' length range of 37 to 70
characters, so a window rule would report the set short at 948 and the ablation would
differ from en_corpus in SIZE as well as in content. Nearest-neighbour supplies 112 and the
achieved match is computed in advance, because the rule is deterministic:

    removed  112   median  40   mean 48.8   range 37-70
    inserted 112   median  48   mean 49.9   range 29-73
    |delta| per pair   mean 3.77   median 3.0   max 11   exact matches 12 of 112
    inserted sources   dolly 53, alpaca 52, flan 5, nq_open 1, squad 1

### 9.5 THE READING, FIXED HERE

Against the banked **Yi base** arm (`P0 - N` = 1.15 bands on five permutations), on the
single construction ruled 2026-09-30 and under §8's three-part rise rule:

- **`P0 - N` within 2 bands of Yi base** -> prose judgement on borderline predicates
  carries the en_corpus effect
- **`P0 - N` still more than 2 bands above base** -> something else in en_corpus
- anything between is `__PARTIAL`, with all three columns given and no sentence invented

### 9.6 A RESIDUAL THE ABLATION CANNOT REMOVE, AND ITS DECLARED SECOND ARM

**Step C's coders confirmed prose judgement in 3 of the 100 sampled unflagged pairs**, all
`dolly`, and they are genuine: *"Is a hotdog a sandwich?"* answered *"That's a tricky
question because most people would consider a hotdog to not be a sandwich; however..."* is
a graded verdict on a borderline predicate. **At 3% that implies roughly 25 such pairs
among the 848, uncoded and unidentified**, so the 112-pair removal leaves some of the
register in the set.

None of the three would be selected by the rule in 9.4 (they are 174 to 486 characters,
far outside the 37 to 70 target band), and the rule additionally **excludes any pair a
coder has confirmed**. But exclusion cannot reach the ones nobody has coded.

**CONSEQUENCE FOR THE READING, STATED BEFORE THE RESULT.** The first branch of 9.5 is
unaffected: if removing 112 pairs drops `P0 - N` to base, the register carries it. **The
SECOND branch is weakened**, because "something else in en_corpus" cannot be separated from
"the ~25 prose-judgement pairs that stayed in".

**SO A SECOND ARM IS PRE-REGISTERED, TO RUN ONLY IF THE SECOND BRANCH FIRES.** The three
coders code all 848 unflagged pairs on the step-C prompt, every confirmed pair joins the
removal set, and the set is rebuilt by the same rule in 9.4 with the same seed. **It is
not run first**, because step D runs only if step A replicates and the coding would be
spent for nothing otherwise.

### 9.7 ORDER, AND THE STOP RULE THAT PRECEDES ALL OF THIS

**Step A first, read before anything else trains.** en_corpus on Yi at seeds 20260909
(banked), 20260910 and 20260911. **If fewer than two of the three raise `P0 - N` by more
than 2 bands, the run stops there: steps B and D are not run, because there is nothing
for them to explain.** Step B follows only if A replicates; step D follows only if A
replicates and this amendment is committed, which it is as of this commit.
