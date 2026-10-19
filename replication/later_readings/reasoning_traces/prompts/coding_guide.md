# reasoning_traces coding guide

Frozen before any reasoning_traces trace exists. Its sha256 is recorded in
`records/PREREG_reasoning_traces_TRACES.md`, section "Coding guide frozen". The text between the
two `CODER INSTRUCTIONS` markers is sent verbatim to both coders; everything outside the
markers governs how the coding is run and is not sent.

## What is coded, and what the coder sees

Every reasoning_traces draw with **reasoning text** is coded once by the primary coder. A draw
with no reasoning text is "no trace", counted with its denominator, and never sent to a
coder (Amendment 1, A1.7). The convention-stated condition was not re-read (A1.6), so
its codes are not used.

For each trace the coder sees exactly three things, in the message described below:
1. **Which case it is**: PRIVATE (the subject acts in a private capacity) or
   PROFESSIONAL (the subject acts in the course of a trade or job).
2. **The case text** the model was shown, without the question and scale that followed
   it.
3. **The reasoning trace**, in full.

The coder does **not** see the model's answer or its digit, the model's name, the
pair's name, the stratum, or any other trace. Analysis 3 compares codes with digits, so
the coder must not have seen the digit.

## Running the coders

- **Primary:** `qwen/qwen3-235b-a22b-2507`, provider GMICloud, on every trace.
- **Second:** `moonshotai/kimi-k3`, provider Sail Research, on a 20% sample drawn at
  random **within each stratum** (full trace: `deepseek_r`, `haiku_r`; summary:
  `grok43_r`, `gemini_r`, `gpt6l_r`, `gpt6s_r`, as confirmed or corrected by the
  recorded `reasoning_kinds`). The sample is drawn after the re-read and before either
  coder runs: the traces with text are sorted by reasoning_traces label, and
  `random.Random(230).sample` takes `round(0.2 * n)` from each stratum.
- **One call per trace returns all three codes** (design A). Temperature **0** for both
  coders, recorded with each call. Reasoning off on the wire. Provider pinned, no
  fallback. `max_tokens` 40.
- **Strict validation.** The reply must parse as one JSON object with exactly the keys
  `R`, `C` and `S`, each valued exactly `"yes"` or `"no"`. Surrounding whitespace is
  allowed; nothing else is: no code fence, no extra key, no other value, no prose.
  A reply that fails gets **one retry** with the identical request. A second failure is
  **uncoded**, counted with its denominator, and never given a default value.

## The keyword pre-pass

Before coding, every trace is searched for candidate mentions: role nouns (professional,
tradesman, electrician, engineer, chef, cook, hairdresser, childminder, nanny, driver,
landlord, plumber, mechanic, amateur, layperson, layman, hobbyist, friend, host, parent,
neighbour, homeowner, volunteer), and the phrases "paid", "for a living", "qualified",
"licensed", "certified", "trained", "standard", "duty", "expected of", "should have
known", "reasonable person". The pre-pass flags candidates and is reported beside the
codes; **it decides no code.** It reads English only: a trace that is mainly not English
(over 20% CJK characters) is reported as `UNREADABLE` by the pre-pass, never as zero
mentions. The coders code every trace whatever its language.

## Agreement and the hand check

- Gwet's AC1 per code (R, C, S), **per stratum** and over both strata, between the two
  coders on the second-coder sample; uncoded traces on either side are excluded and
  counted. **Floor 0.70 for every code in every stratum.** If any falls below it, all
  agreement figures are reported and the work stops before the analyses.
- Hand check of **30 traces**, 15 per stratum, drawn with `random.Random(2301)` within
  cells of the primary coder's codes (so that yes and no on each code are both
  represented where they occur). Every disagreement with the primary coder is listed
  with the trace label and the reason.

## CODER INSTRUCTIONS (begin)

You will code one piece of reasoning. A model was shown a short description of an
accident caused by a person called Alaric, and asked how much Alaric is to blame. Before
answering, it reasoned. You are shown which kind of case it was, the description, and
the model's reasoning. You are not shown its answer.

The case is one of two kinds.
- PRIVATE: Alaric acts in a private capacity, at home, for a friend or as a favour, not
  as a job.
- PROFESSIONAL: Alaric acts in the course of a trade or job, for a customer or employer.

Answer three questions about the REASONING only. Code what the reasoning says, not what
the description says, and not what you think the right answer is.

**R (role).** Does the reasoning treat Alaric's role or status as bearing on how much
he is to blame?
- For a PRIVATE case: does it mention that he is a private person, an amateur, a
  homeowner, a host, a friend, a parent, not trained, or not paid, AS A CONSIDERATION
  IN THE BLAME?
- For a PROFESSIONAL case: does it mention that he is a professional, qualified,
  trained, paid, or doing his job, AS A CONSIDERATION IN THE BLAME?
- Code "yes" only if the role is used in weighing blame. Restating the facts ("Alaric,
  an electrician, fitted a plug") is "no".

**C (comparison).** Does the reasoning compare Alaric with someone in the other role who
did or might have done the same thing?
- For a PRIVATE case: a professional (a tradesperson, a chef, an electrician, "someone
  who does this for a living", "an expert").
- For a PROFESSIONAL case: a private person (a homeowner, an amateur, "an ordinary
  person", "someone doing it at home").
- The comparison may be explicit ("a qualified electrician would have checked") or by
  clear implication ("this is the kind of thing a trained person would catch, but he
  is not one"). A comparison with an unspecified "reasonable person" is "no" unless
  the reasoning ties that person to the other role.

**S (standard).** Does the reasoning state or apply a DIFFERENT standard of care
because of Alaric's role?
- For a PRIVATE case: a LOWER standard than a professional would be held to ("less
  can be expected of someone who is not trained", "an amateur is held to a lower
  standard").
- For a PROFESSIONAL case: a STRICTER standard than a private person would be held to
  ("as a professional he is held to a higher standard", "this is basic for someone in
  his trade").
- Code "yes" if the reasoning states the different standard or plainly uses it in
  reaching blame. Merely saying he "should have" done something is "no".

The three codes are separate. A reasoning can mention the role without comparing (R yes,
C no), or apply a lower standard without naming a professional (S yes, C no).

### Worked examples

These are invented cases, not the ones you will code.

PRIVATE. Description: Alaric pruned a large branch from a tree in his garden. He did not
check what was below; the branch fell on a neighbour's shed.

1. Reasoning: "He is just a homeowner doing some gardening, not a tree surgeon, which
   matters for how harshly to judge him. Still, checking below before cutting is
   obvious. Moderate blame." Codes: R yes (homeowner status weighed), C yes (tree
   surgeon), S no (no different standard stated; he is judged on what is obvious).
2. Reasoning: "Anyone cutting a branch should look below first. He didn't. That is
   careless. High blame." Codes: R no, C no, S no.
3. Reasoning: "An amateur can't be expected to know the techniques an arborist uses to
   control a fall, so I'll hold him to a lower standard than a professional. But looking
   below needs no training." Codes: R yes, C yes, S yes.
4. Reasoning: "Since he is doing this unpaid in his own garden, less is expected of him
   than of someone hired to do it." Codes: R yes, C yes (someone hired), S yes.

PRIVATE. Description: Alaric adjusted the brakes on a friend's bicycle as a favour. He
did not tighten one bolt; the brake failed on a hill.

5. Reasoning: "He was helping a friend, which is kind, but he took on the job. The bolt
   was loose. Fairly high blame." Codes: R yes (helping a friend weighed against
   taking on the job), C no, S no.
6. Reasoning: "Not a mechanic, so maybe he didn't know how tight it needed to be;
   a bike shop would have torqued it properly. Some blame." Codes: R yes, C yes (bike
   shop, mechanic), S no (a difference in knowledge, not a stated lower standard).

PROFESSIONAL. Description: Alaric, a tree surgeon, pruned a large branch for a customer.
He did not check what was below; the branch fell on a neighbour's shed.

7. Reasoning: "As a trained arborist this is basic practice for him; a professional is
   held to a higher standard than a homeowner would be. High blame." Codes: R yes,
   C yes (homeowner), S yes.
8. Reasoning: "He was paid to do this job and failed to check below. High blame."
   Codes: R yes (paid, doing his job, weighed), C no, S no.
9. Reasoning: "Checking below before cutting is obvious to anyone. He did not. High
   blame." Codes: R no, C no, S no.

PROFESSIONAL. Description: Alaric, a bicycle mechanic, adjusted a customer's brakes. He
did not tighten one bolt; the brake failed on a hill.

10. Reasoning: "Even someone fixing their own bike at home would tighten the bolts. For a
    mechanic it is inexcusable." Codes: R yes, C yes (someone at home), S yes (stricter
    for the mechanic).
11. Reasoning: "This is his trade, so the expectation is higher." Codes: R yes, C no,
    S yes.
12. Reasoning: "The bolt was left loose and the brake failed. Clear negligence, high
    blame." Codes: R no, C no, S no.

### Reply

Reply with one JSON object and nothing else, exactly in this form:
{"R": "yes", "C": "no", "S": "no"}
Each value is "yes" or "no".

## CODER INSTRUCTIONS (end)

## The message each coder receives

System: the text between the markers above, verbatim.

User:

    CASE: <PRIVATE or PROFESSIONAL>

    DESCRIPTION:
    <the case text the model was shown, before the question>

    REASONING:
    <the full reasoning trace>

## The analyses (unchanged from the pre-registration, per stratum)

1. Share of PRIVATE traces coded C, and coded S, with denominators (prediction: under
   one in five, evaluated per stratum).
2. The same for PROFESSIONAL traces (no prediction).
3. Within PRIVATE traces, the mean digit of traces coded C or S against those coded
   neither, each digit from the same call as its trace (prediction: lower when C or S).
4. Not run: the convention-stated condition was not re-read.

Per arm and pair, and pooled within each stratum, never across strata.
