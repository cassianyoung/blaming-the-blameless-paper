# Measurement notes

This file records the instrument findings behind the design choices of the paper's
§3. Nearly every result in the paper was first observed at a larger size than it has
now. The differences came from how cases were written, how answers were read, how noise
was measured and how records were kept. Each finding below is stated with the control
that now handles it. Findings that bear directly on how the results should be read are
also stated in the paper itself, as noted.

## 1. How cases are written

**The referent.** When the blame question did not name the subject ("how much is the
person to blame?"), models attributed blame to whoever the text made salient, not to the
subject intended. On one case this moved the reading by 7.8 points on the ten-point scale.
Every question now names its subject, resolved from the case text and checked on every
rendered prompt. (Paper §3.1.)

**Foreseeable causes.** An early target case had the harm follow from a pothole. Models
read the pothole as something a careful rider should have avoided, so the careful
lender's case became a case about the rider's negligence. The target case now has a cause
no one could have foreseen, a hidden flaw. (Paper §3.1.)

**Implied causation and clause order.** Where the causal link between act and harm was
implied, models filled it in variously; it is now stated. The order of clauses within a
case moved readings: when three cases assembled from parts were put back in the order
they were written, single cells moved by up to 1.8 points on a model whose endpoint
repeats to within 0.01 (the misordering had also left a pronoun without its antecedent,
so the two effects are not separated). Cases are therefore written as fixed strings,
frozen and hashed, never assembled from parts. (Paper §3.1.)

**Sentences are never inert.** A sentence added as a neutral control, with no bearing on
blame, moved readings by up to a quarter of each model's scale, in either direction.
Models treat every circumstance in a short case as relevant. Controls are therefore
compared with each other (an excuse against a neutral sentence of the same length), never
with the case alone. (Paper §4.1.2.)

**Duty pairs.** A pair compares a professional and a private person doing the
same careless thing. Both legs carry the same lapse and the same harm, word for
word where the role allows; only the role changes. The private person must owe
no special duty of their own to the person harmed: a parent dosing their own
child carries a duty at least as strong as a shopkeeper's, and a pair built on
it measured that duty rather than the convention, so it is not reported. The
harm must be caused by the subject alone; a cause on the victim's side (an
allergy, say) dilutes the subject's causal part. Harms are kept moderate so
that neither leg sits at the top of the scale. In the comparison prompts the
two parties are described by role, never named, since naming the subject moves
readings by more than the effect under test.

**Neutral sentences.** A control sentence must say nothing evaluative: no words
of frequency or normality ("every day", "across the country"), which describe
an act as commonplace and lowered blame by about a digit when used; nothing
about risk, care, duty or the lapse; and no word that appears in only one leg's
case, which would carry one setting into the other. Neutral sentences are
matched to the sentence they control for in word count, within three words. A
check on banned words must match whole words, or it refuses good sentences
("should" inside "shoulder").

**Convention sentences** name both roles, as the convention does. Where the
sentence's word for a party differs from the case's ("paying customers" against
"diners"), that is recorded.

## 2. How answers are read

**Single draws.** Models served through commercial APIs proved not to be deterministic at
temperature zero: ten identical calls on one undecided cell spanned 5.6 points (sd 1.5)
on one model and 2.7 points (sd 1.2) on another, while a third repeated to within 0.2.
Every API cell is read ten times, or twenty for some sampled arms.

**Templates.** Several chat templates expect text before the answer, such as a leading
space, so the digit the model emits is not the token a naive reader scores. Some templates
have no system role. The scored token is located from where the answer probability
actually falls, and template adjustments are recorded with every reading. One model's
template (StableLM 2's chat release) retokenises the prompt when the answer prefix is
appended; it could not be scored on chat and is reported as unreadable.

**Reasoning.** Reasoning models leave no fixed answer position, so they are read by
sampling. Three failures followed. A token budget of eight tokens cut off reasoning before
the answer on more than half of one model's draws, and those draws were silently read as
the model's non-reasoning mode. Truncation at a larger budget removes the longest
reasoning first, so excluding truncated draws selects the cases where the model thought
least; a cell losing more than 10% of draws to truncation is not used. And a detector
that recognised reasoning by its returned text missed reasoning that one provider bills as
tokens without returning the text, reporting real reasoning as absent; four bicycle
readings of Gemini 3.8 Flash taken under that detector were withdrawn. Reasoning is now
detected by text or tokens, and its share is reported per cell, since some models choose
case by case whether to reason. Where a model declined to reason on an anchor case, the
anchor is taken from all its draws. (Paper §3.3.)

**Coding reasoning traces.** A coder that counted a trace as concluding "not at fault"
if that phrase, or a candidate answer of 0, appeared anywhere in the trace reported 19 of
20 Qwen3-8B traces as concluding the careful lender was not at fault. Coded by the answer
each trace finally settles on, 4 of 20 do: most entertain no blame and then argue past it.
Traces are now coded on their final stated answer, with "entertains" and "concludes"
reported separately. The coding is by one coder, unblinded, and the discriminator was
developed on the same cases; it is a described mechanism, not an established one. An
earlier version of the coder matched the restated case text and reported every trace as a
hit. A mean probability read after the trace (0.09) was carried by three of nineteen
draws; the median is reported beside it.

**What providers declare is not what they deliver.** Endpoints advertised
log-probabilities and returned none; advertised a reasoning switch that did not switch;
capped the number of returned alternatives without saying so. One provider adds about
1,200 tokens of its own instructions to every prompt. One provider changed a model's
default from no reasoning to reasoning between reads; every call now carries the
reasoning setting explicitly, and the harness refuses a call that omits it. Every
capability is probed before a model is read, and prompt tokens billed are compared with
prompt tokens sent.

**The reasoning setting is always declared.** Every model's configuration
states its reasoning setting: an explicit value, or a declared vendor default
where the setting is deliberately omitted. A call on an undeclared setting is
refused. A reading taken on a vendor default is reproducible only while the
vendor's default stays the same.

**Providers change and disappear.** A provider withdrew a model's endpoint
partway through reading one model's cells. Cells already read keep their
values; cells not read are recorded as unread with the reason, never read on a
substitute provider, since a contrast built across two providers mixes two
serving configurations. Every call records the provider that served it, and no
contrast combines cells from two providers.

**Costing reasoning models.** A single-call probe cannot price a reasoning
model, whose cost depends on how long it reasons on each prompt; estimates
from such probes came in at about half the true cost. Reasoning arms are
priced from their measured per-call cost in the most recent comparable read.

**Parsing the side-by-side answer.** The paper's prawns-pair comparisons were read under
a strict rule: a draw counts only if the answer consists of the two labelled digits alone,
`HOME=<digit>` and `CHEF=<digit>` in either order and in any letter case, separated by a
space or a comma, with only punctuation or white space before and after. Anything else
voids the draw, a newline between the two fields included, and a cell that loses more than
10% of its draws is not used (none did). The five other pairs were read by searching the
answer for each label, in capitals as given, followed by `=` and a digit, with any
surrounding text allowed. The eval package applies the second rule to all six pairs. On the
banked prawns reads the two rules disagree on two draws, both Mistral-24B's: `HOME=6` and
`CHEF=8` on separate lines (void under the strict rule, read by the search) and
`Chef=8 Home=6` (read under the strict rule, void under the case-sensitive search). Under
the search rule Mistral-24B's stated gap on the prawns pair is 2.39 rather than the paper's
2.45; no other model's prawns reading changes. Every paired draw was sampled at temperature
1.0, on every arm.

## 3. Frames

**The frame moves the reading more than tuning does.** The same instruction-tuned weights
read on the worksheet and through their chat templates shift the careful subject's position
by 0.23 on average among releases that pass the chat gate; a developer's instruction
tuning shifts it by 0.09. Eight chat releases put the same blameless case at levels from
0.04 to 4.00. Positions are compared only within a frame. (Paper §4.2.)

**The worked examples anchor the scale.** A lightly tuned model asked a bare question,
without worked examples, placed the blameless case a third of the way up the scale. The
examples' ratings, not the verbal description of the scale, fix what its ends mean for
such a model. This is why base models can be read on the worksheet, and why the adapters
are read there too. (Paper §3.4.)

**The local chat harness against the API.** Before any family was read
locally, two checkpoints were read both on local hardware and through a
commercial API. For Gemma-3-27B-IT, seven of eight bicycle cases agree to
within 0.013 of the scale; the API reads the impossibility excuse higher, the
conservative direction for the paper's claims. For Llama-3.1-8B-Instruct, nine
blameless cases show no systematic shift (mean difference +0.03 digits). The
API's precision (fp8) and the local bf16 differ, so differences are reported,
not refused.

## 4. Noise, gates and statistics

**The gate must not see the outcome.** An early gate admitted a model only if its target
case sat clearly above its floor, which selected for the effect under study. A later gate
used fixed thresholds on the blameless and deliberate cases, which wrongly refused models
whose scale was readable. The gate now tests only whether the scale can be read: on the
worksheet, the careless case at least three bands above the blameless one and answer mass
at least 0.7; on chat, at least 80% of the blameless case's probability on 0–3, answer
mass at least 0.7, and the deliberate case at least 7.0 where read. The rule is chosen by
each reading's delivery, never by convention. A scenario that fails a model's gate is
excluded from every count for that model, judgement questions included. (Paper §3.3.)

**How the band is built.** A noise band computed as a range grows with the number of
readings; one computed from a single ordering mixes a single reading into a mean; and one
way of expressing a difference in bands registered a change of denominator alone as a
rise. Bands are 2.33 times the standard deviation over orderings, differences are
expressed in the pooled band of the two versions compared, and the construction is fixed
before results are read.

**Answer mass on sampled reasoning arms** is computed over the same draws as the values it
gates (the reasoning-only draws). Computed over different populations, one cell was
reported at three different values in three exports.

**Two kinds of noise.** Draw noise is the spread when the same prompt is asked
again; wording noise is the spread when an irrelevant descriptive sentence is
added to the case. Wording noise is about twice draw noise at the median and up
to about two points on some models, so a remedy that adds words is judged
against wording noise (each model's spread over three neutral sentences per
pair, 2.33 × sd, with a minimum of 0.30), not against draw noise. Draw noise
mostly reflects the readout: models read by log-probability return their whole
answer distribution and barely vary; models read by sampling average ten
single-digit answers and vary more.

**Ratios need a denominator that clears the noise.** A share or a recovery is
reported only where its denominator (the model's stated gap, net of the neutral
baseline) exceeds that model's wording floor. Below it, the ratio divides a
real movement by noise and can reach any size or sign; the movement is reported
in points instead.

**Which standard deviation.** A noise floor describes one model's own readings
and uses the population form; a spread across models is a sample of models and
uses the sample form. The two differ by √(n/(n−1)), small enough to pass for
rounding.

**A floor is tied to the pairs it was computed on.** Results classified against
a floor are reproduced only against the same floor; a floor that gains another
pair's readings is a different floor.

**Checks that check nothing.** A check that rendered no prompts reported no failures; an
analysis that read a missing field reported zero; a gate passed on blank inputs; a screen
for unresponsive models flagged a model whose answers were, case by case, exactly those
reasonable care requires; a test whose fixture went stale stopped running without
failing. A refusal that carries a false reason ("this pair has no neutral sentences",
where the pair had them and the provider had failed) is the same defect in
prose. Every check now reports its denominator beside its failures, missing
data is refused rather than defaulted, every refusal states its true reason,
and no check uses a literal row count.

## 5. Training and provenance

**The seed.** For adapters trained before 1 October 2026, the recorded seed governed data
order and dropout but not the adapter's initialisation, so those adapters cannot be
reproduced exactly. Three adapters trained on one corpus with controlled seeds gave
readings within a third of a noise band of one another: readings reproduce where weights
do not.

**Masks and decoding.** On one family (Yi), decoding the answer tokens back to text did
not reproduce the original even where the mask was exact, so the check that the trained
tokens are exactly the answer is made on character offsets.

**Truncation in training.** A translated control corpus had answers up to 5,884 tokens
long, and 7.6% were cut off at the 512-token limit, ending without a natural stop. The
control was retrained at 2,048 tokens; both versions are reported.

**Linking readings to weights.** For three Yi control adapters (the two translated-corpus
adapters and the no-prose-judgement adapter), the training manifests record the weight
hashes, and the published weights re-hash to them. The per-cell reading files record the
same adapter digest, but the aggregated records that the results database ingests carry
the adapter's run label rather than its hash, so within the database the link from a
reading to its weights rests on the label. Each of the three labels maps to exactly one
manifest and one digest. Readings now record the hash of the weights they were taken
through.

**Checkpoint revisions.** Every local read pulled the publisher's current
revision. Where the revision was logged, it is pinned; where it was not, the
revision is inferred from the publisher's history, which shows the revision
unchanged since before the read, and is labelled as inferred.

**Corrupted weights.** One pre-download of a base model's weights was incomplete, and a
marker that certified downloads checked itself rather than the publisher's digests. Every
checkpoint is now verified against its publisher's file digests before loading.

## 6. Records

Most of the errors above were found because records disagreed with each other. Two
practices made that possible: every artefact is identified by the hash of what was
actually read, and statements in records are derived from data, not written once and
left.

Three sets of paid-for, banked measurements were found never to have been ingested into
the results database (a families pass, the Yi control adapters, and the bicycle judgement
questions), each discovered only when a table needed them. The database build now checks
that every question asked in any run has a value, or a stated reason why not.

Builders select rows by the data's properties, never by run number: two builders scoped
to one run silently omitted every arm read later. A model was once excluded from the
full read by a gate defect and not restored when the gate was corrected; reported arms are
now defined by one rule in one place, read by every exporter.

Builders select their inputs by what the data is, never by where it was saved:
a builder that looked for one set of readings in one directory silently omitted
three models whose readings had been saved elsewhere, and only a cross-check
against an independent record caught it.

**A table keyed by cell holds every reading of that cell, or says why it holds
fewer.** The table that collects each model's per-scenario readings was keyed by
role, so on the worksheet, where every role is read under five orderings, each
ordering overwrote the last and the fifth stood for the role, while the bands and
gates were computed from the mean over all five. No printed number was affected,
because every number drawn from that table came from models read once per cell;
the defect surfaced when the eval was run again from scratch and the fresh readings
matched the mean, not the table. Each row now records how many readings it is the
mean of, a cell with fewer than its orderings states why, and the build refuses a
count that disagrees with the readings it was built from.

**A log records what happened, not what is happening.** A progress table that
inferred activity from a call log reported a reader as running for hours after
it had stopped. Liveness is read from the process table.

**Spending caps stop spending, not work.** A reader that reaches its cap writes
every completed cell before stopping, so the remaining cells can be read later
and merged per cell, each carrying its source. A database build records the
readings it ingested by hash, and reports any reading that appeared on disk
during the build.

**Every call keeps its full text.** Until October 2026 the harness that sent every API
reading logged the length of a model's reasoning but not the reasoning itself, and kept
only the first 400 characters of the answer. The scores were unaffected, but no
reasoning trace from the duty test survived, so a test of what the reasoning models
consider when they judge a case alone could not be run on the banked readings. Every
call now records its full reasoning text, its full answer, and the provider's own
description of what the reasoning is: the model's text, a summary written by the
provider, or an encrypted block. That description is recorded rather than inferred,
because the length of a trace does not distinguish a short trace from a summary. A test
reads the written log back and fails if either text is cut.

**The probability on yes and no is kept, not only whether they appeared.** The same kind
of loss affected the yes/no questions read by log-probability. The reader computed the
total probability the model placed on "yes" and "no" for each draw, used it to normalise
P(yes), and discarded it. The answer mass recorded for those cells was therefore one minus
the share of draws in which neither word appeared anywhere in the top tokens. That
measure passes a draw that puts 5% on yes and no and 95% elsewhere. P(yes) was unaffected,
because it is normalised over the two answers either way. From prevention_paraphrase the reader records
the mass itself, and the yes/no gate applies to it.

**A re-read reproduces the banked separate readings.** When the six reasoning models'
separate-case readings on the duty test were read again to recover their reasoning text,
3 to 10 days after the banked reads, with the same prompts (checked by hash), the same
providers and the same settings, each model's cell means moved by a median of 0.05 to
0.10 points, inside the 0.15 points by which one neutral sentence differs from another on
the same case. The largest single cell moved 0.6.

**Where the two trace coders disagreed on R and S, the guide is ambiguous in two places
and one coder over-reads in the short traces.** (reasoning_traces, 2026-10-12; no code was
changed.) The primary coder (Qwen3-235B) and the second (Kimi-K3) disagreed on R or S in
46 of the 150 sampled traces, 48 code decisions in all, and every one was the primary
saying yes where the second said no. Each was read against the frozen guide by one reader,
who saw both codes, in one pass, not checked by anyone else.
- **Summaries, R (23):** 19 are the primary coding yes when the role is only named in
  passing ("the chef served spoiled prawns", "a qualified electrician omitted the
  earth"), which the guide says is no. These are the primary misapplying the guide.
  3 go the other way (the reasoning says "considering he was offering a friend a ride",
  which the guide counts as yes); 1 is ambiguous.
- **Summaries, S (4):** all 4 are the primary coding a different standard where none is
  stated.
- **Full traces, R (9):** 6 are reasoning that names the role as the source of an
  ordinary duty ("as the owner, he has a duty of care", "his duties as a host", "he is
  the driver, responsible for maintenance"). The guide does not say whether that counts
  as weighing the role. 3 are the second coder missing an explicit private-role
  consideration ("not a professional salon", "an untrained person").
- **Full traces, S (12):** 7 are a professional case saying the role raises what is
  expected without naming anyone held to less ("a professional should know better", "a
  basic professional duty"). That falls between worked example 8 (paid, failed: S no)
  and example 11 ("this is his trade, so the expectation is higher": S yes), and the
  guide does not settle it. 4 are the primary coding S where no different standard is
  stated; 1 is the second coder missing one ("he's not a professional property manager",
  given as a reason for less blame).

Of the 48: the primary misapplies the guide on 27, the second on 7, and 14 are cases the
guide leaves open. So the R failure in the summaries is mainly one coder over-reading
short texts that name the role. The R and S failures in the full traces are mainly the
guide not drawing the line between role as context and role as a different standard. C
does not share the problem: it needs a person in the other role to be named or plainly
implied, which is a test the coders applied the same way (AC1 0.955 and 1.000).

**A sampled mean and a log-probability expected value measure the same thing only at
temperature 1.** The expected value read from the log-probabilities is taken over the
model's own distribution of answers. A sampled mean estimates that same quantity only
when the draws come from that distribution, which is temperature 1. At any other
temperature the draws come from a sharpened or flattened distribution, and the two
numbers measure different things. So every sampled reading that is set beside a
log-probability reading is drawn at temperature 1.

**An export the check does not cover can carry a stale stamp.** Every exported table
carries the sha256 of the database it came from, and a check rebuilds each one and diffs
it against the committed copy. One exclusions file (the Table A.8 exclusions) was not on
the check's list, and it kept an old database's stamp through two rebuilds while every
other file moved on. Its values happened to be unchanged; its stamp was wrong. That file is now on
the check's list; the lesson is that a file the check does not rebuild passes silently.
