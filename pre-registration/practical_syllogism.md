# practical_syllogism pre-registration

Banked 2026-10-13, before any practical_syllogism call. Texts frozen in the practical_syllogism frames file
(sha256 `6fc50e644efbd2e6c56d922b6e9c76a79c5d2ae474dd468cc993ef6991d1525f`), built by
the frames build script (sha256
`2f7506c09b32892bec1ad2718c5df115f3250def6ce2eec953b9c6e59ffcafc2`). The instruction
follows verbatim (only its title's dash is rendered as a colon, per house style), then
Amendment 0, which fixes what the instruction leaves open. Points marked **FOR RULING**
carry a default that applies unless ruled otherwise.

---

# Instruction: practical_syllogism: the practical syllogism

The paper's claim for Bias 1 has the form of Aristotle's practical syllogism:
the models hold the principle (a person who could not reasonably have prevented
a harm is not at fault), they hold the fact (this man could not reasonably have
prevented it), and they do not draw the conclusion. prevention_paraphrase showed the fact is
held and the conclusion is not drawn. This run tests the principle, and whether
the models draw the conclusion when they assemble the premises themselves.

The test is made in **separate calls**, so that no answer can be shaped by
another: the principle, with no case; the fact, on the case; the conclusion, on
the case. A single call containing all three would put the answers under
pressure to agree, and would test that pressure, not the syllogism. Two of the
three readings already exist; this run adds the third.

## 1. THE THREE PREMISES, EACH IN ITS OWN CALL

**The principle (new; condition A).** No case. One call, system message and
answer instruction as for the banked Reasonable question:

> "Under the standard of reasonable care, is a person at fault for a harm he
> could not reasonably have prevented? Answer yes or no."

Freeze with its sha before any call.

**The fact (existing).** The Reasonable question on each scenario's target case,
from prevention_paraphrase's same-session re-read.

**The conclusion (existing).** Two readings of the target case: prevention_paraphrase's
"Did Alaric fall short of the care a reasonable person would take?", and the
banked Blame position.

**Optional remedy check (condition B), reported separately and never as the
syllogism test.** On each target case, one call asking all three in order and
answering `PREVENT=<yes or no> PRINCIPLE=<yes or no> BLAME=<digit>`, read by
sampling at temperature 1. This measures whether setting out the premises in one
answer brings the verdict down, the "judgement first" remedy. Read it only if
approved.

## 2. ARMS AND DRAWS

The 13 reasoning-off arms read in prevention_paraphrase (Qwen3-235B and Qwen3-30B are
unavailable on their banked providers and are not moved). Settings and providers
as banked, asserted. Condition A: ten draws per arm. Condition B, if approved:
six scenarios, ten draws per cell.

## 3. PRE-REGISTRATION (bank before any read)

- **practical_syllogism.P1 (principle held):** in A, every arm answers "no" on at least 9 of 10
  draws.
- **practical_syllogism.P2 (the syllogism, from separate calls):** over the 13 arms' target-case
  cells, report the share of cells where the principle is held (practical_syllogism.P1 for that
  arm), the fact is held (Reasonable modal "no" in prevention_paraphrase), and the conclusion
  is not drawn: (a) "fell short" modal "yes" in prevention_paraphrase; (b) the blame position
  more than the arm's draw band above its blameless anchor. Report each with its
  denominator, per arm and pooled. No pass mark: this is the measurement the
  paper reports.
- **If B is read:** practical_syllogism.P3, the blame position in B falls below the banked
  direct Blame position, median shift with a 95% bootstrap interval over arms;
  pass if the interval lies below zero. Reported as a remedy result only.

**For the paper.** One sentence from practical_syllogism.P1–2: every model states the
principle, nearly every model states the fact, and in [share] of cases the same
model does not draw the conclusion, in the blame verdict or when asked whether
the subject fell short of reasonable care. If B is read, one sentence on whether
stating the premises together brings the verdict down.

## 4. ORDER OF WORK

0. Freeze texts and pre-registration; report and stop.
1. On approval, read all arms. No halt.

## 5. OUTPUT

Ingest; rebuild; register the pre-registered figures in `paper_numbers`. Report
practical_syllogism.P1 and practical_syllogism.P2 (and practical_syllogism.P3 if B is read), the database sha, and the
sentence for the paper.

---

# Amendment 0 (2026-10-13, before any call)

## A0.1 Texts, frozen

- **Principle (A)**: body verbatim from §1, sha256
  `9d92eb82f95e7a8fd073858ca0b214b05d1f9e0cc775f57905b4d4076f3b1457`.
  - System message: the banked yes/no one, "Answer with one word, Yes or No, and nothing
    else.", taken from the prevention_paraphrase frames.
  - Wire prompt sha256 `d3b4dbf850fe277b2c65420e92c7f76b7d374f7eb509153f2321b460e58332c6`.
- **B**: 18 prompts, six scenarios by three roles (P0, N, C; see A0.7 for why N and C).
  - System: "Answer in exactly the form PREVENT=<yes or no> PRINCIPLE=<yes or no>
    BLAME=<digit>, and nothing else."
  - User: the case text, a blank line, "Answer three questions, in this order.", then
    three numbered stems, then the answer form.
  - The PREVENT and BLAME stems are copied from the deployed_scenarios frames. The PRINCIPLE stem
    is the A text. Each stem drops its own answer instruction.
  - The build asserts each stem appears once and in order in the built prompt.
  - It also asserts the P0 row texts are the bytes prevention_paraphrase read.

## A0.2 Arms

The 13 arms READ in prevention_paraphrase, with exactly prevention_paraphrase's settings: model, provider, readout,
max_tokens and top_k (the prevention_paraphrase reader's arm table). Every arm runs at temperature 1.0
with reasoning off.
- A served provider other than the banked one makes the arm UNREAD with its reason, as
  in prevention_paraphrase (A0.9 there).
- Qwen3-235B and Qwen3-30B are not attempted.
- A: 10 calls per arm, 130 calls in all.

## A0.3 practical_syllogism.P1 on the log-prob arms

On a log-prob arm each of the ten calls returns a probability of yes, not an answer. That
probability is the same readout prevention_paraphrase used for the fact and the conclusion.
- **Default**: a log-prob arm holds the principle if its mean P(yes) over the ten calls is
  at most 0.10, which is "no" on at least 9 of 10 draws in expectation.
- Each call's sampled token is reported beside it.
- A sampled arm holds the principle if at least 9 of 10 draws parse as "no". An unparsed
  draw counts against.
- An arm whose A cell fails the yes/no mass gate (below 0.70, as prevention_paraphrase) is counted as
  **not holding** the principle, and listed.

## A0.4 practical_syllogism.P2, the definitions

- **Population**: prevention_paraphrase's 75 target-case cells, which are 13 arms by 6 scenarios less
  the banked gate exclusions (deepseek, kimi and mistral24b on the cheque).
- **Principle held**: the arm meets practical_syllogism.P1.
- **Fact held**: prevention_paraphrase's Reasonable P(yes) on the cell is below 0.5. A tie at 0.5 is not
  held.
- **Conclusion not drawn, (a)**: prevention_paraphrase's Q-fell P(yes) is above 0.5. A tie is not
  counted.
- **Conclusion not drawn, (b)**: the banked blame position (the judgement table, published as
  `data/A8_judgement_long.csv`, reasoning off, P0) is above the band (A0.5).
- **Two shares, each with its denominator, per arm and pooled:**
  1. all three conditions, over all 75 cells;
  2. conclusion not drawn, over the cells where both premises are held.
- **FOR RULING**: the paper sentence's "[share] of cases the same model does not draw the
  conclusion" reads as the second, conditional share. **Default: the sentence quotes the
  conditional share and gives the unconditional one beside it.**
- Also reported: the share of cells where (a) and (b) both hold.

## A0.5 "The arm's draw band": FOR RULING

No per-arm draw band exists for a blame position.
- A position is already normalised by the arm's own N-to-C span.
- The paper's ruled threshold is a single band of **position above 0.10**: the
  introduction's "beyond the instrument's noise", 74 of 86 cells
  (as computed for the introduction).
- **Default: (b) is position > 0.10.** The three-band figure (above 0.30) is reported
  beside it.

## A0.6 What (a) re-reads: FOR RULING

practical_syllogism.P2(a) counts as **"conclusion not drawn"** the very cells that prevention_paraphrase's
pre-registered §5 ruled to be **wording disagreement**: Q-fell yes where Reasonable says
no, 24 such cells against 2 the other way. The fact premise also rests on Reasonable,
the wording prevention_paraphrase found not robust.
- So the instruction's statement that "prevention_paraphrase showed the fact is held and the
  conclusion is not drawn" is a second reading of prevention_paraphrase's data. It is not the reading
  prevention_paraphrase's decision rule produced.
- Both readings fit the same cells. prevention_paraphrase cannot tell them apart, and neither can this
  run, because (a) adds no new reading.
- **Default**: (a) is computed as specified.
  - Wherever it is quoted, it carries a clause saying it uses the cells prevention_paraphrase reported
    as wording disagreement.
  - (b), which rests on a different instrument (the blame scale), is quoted first.

## A0.7 Condition B, if approved

- **B.1 Readout.** Sampled at temperature 1 on all 13 arms, the log-prob arms included.
  - The sampled arms keep their banked max_tokens.
  - The log-prob arms get max_tokens 32, since the form needs about 15 tokens.
  - A draw parses when all three fields are present and valid, each matched by a
    case-insensitive field regex. An unparsed draw is dropped, counted and kept verbatim.
  - A cell fails its gate if fewer than 7 of 10 draws parse.
- **B.2 The ruler.** A blame position needs N and C read in the same frame. The study's standing
  rule is a ruler per frame. Also, on the log-prob arms the banked direct Blame is a
  digit-probability expectation, while B is sampled digits.
  - **Default: read B on N and C as well as P0**, giving each arm-scenario its own
    position in B.
  - Cost: 2,340 calls against 780 for P0 alone.
  - **Known defect**: on N the PREVENT stem ("Could Alaric reasonably have prevented
    this?") has no referent, because N ends "Nobody came to any harm." This is the
    Reasonable-at-N defect found in an earlier run. deployed_scenarios handled the same case for CAUSE: read it, report it
    as not interpretable, never use it.
  - Here N's PREVENT field is reported as not interpretable. **BLAME on N is the zero
    anchor**, read under the same three-question prompt, so whatever the unanswerable
    first question does to it is part of B's own ruler.
  - B gate, mirroring the banked one: N's sampled BLAME has at least 80% of draws in 0
    to 3, and C differs from N.
  - **Alternative (not recommended)**: P0 only, with practical_syllogism.P3 in raw digits against the
    banked direct P0 expectation. That compares raw digits across readouts and pools
    them across arms, which the per-arm ruler rule forbids.
- **B.3 practical_syllogism.P3.**
  - Per arm: the mean, over its gated scenarios, of (position in B minus banked direct
    position).
  - Across arms: the median of those means, with a 95% bootstrap over arms (10,000
    resamples, seed 232).
  - Pass if the interval's upper end is below zero. Reported as a remedy result only,
    never as the syllogism test.
- **B.4 Also reported**: the PREVENT and PRINCIPLE fields on P0, set against the separate
  calls (the fact from prevention_paraphrase, the principle from A), so the remedy's premises can be
  compared with the syllogism's.

## A0.8 Calls

| Condition | Calls |
|---|---|
| A (principle) | 130 |
| B, P0 only | 780 |
| B, P0 + N + C (default, A0.7 B.2) | 2,340 |

## A0.9 Output

- Ingest, as new questions on the excuse test: PRINCIPLE (A) and B_PREVENT,
  B_PRINCIPLE and B_BLAME (B).
- Rebuild the database.
- Register every pre-registered figure in `paper_numbers`, gated on recomputation from
  the ingested cells (the prevention_paraphrase pattern).
- The result file is write-once.

# Ruling (2026-10-13, before any call)

"Approved with all five defaults, read A and B."

So A0.3 to A0.7 stand as their defaults. **B is read on P0, N and C** (2,340 calls),
and A is read on all 13 arms (130 calls).

# Amendment 1 (2026-10-13, during the read and before the result was written)

A fall in position says how much B helps only alongside where B's blame ends up. A fall
of 0.31 from a typical 0.5 leaves the careful subject still blamed, while the same fall
from 0.35 nearly clears him. So practical_syllogism.P3 also reports, over the same gated cells:
- B's median position beside the direct reading's median;
- the share of cells still above 0.10 in B beside the direct share, and the count above
  0.30 beside the direct count.

These are descriptive and carry no pass mark. They are registered in `paper_numbers` with
the rest. The provisional figures on 11 arms had already been seen when this was added;
the request was for the figure's existence, not its value, and it does not change practical_syllogism.P3
or its rule.
