#!/usr/bin/env python3
"""moral_frames.py : the moral sweep's candidate frames and its material slots.

`workorder_moral_sweep_v2.md` and its Amendment 1. No model, no numbers.

WHY THIS IS A MODULE AND NOT A BANK FILE, same reason as `gradient_frames.py`:
the rungs and the act sentence are derived and asserted at build time, and a
derived value written into a JSON by hand is a standing literal waiting to
disagree with its own derivation.

═══════════════════════════════════════════════════════════════════════════════
THE THREE CANDIDATE FRAMES, AND WHAT THE PILOT ASKS OF THEM

It asks ONE thing: does the frame elicit a number. That is a property of the
frame, so it is measured on TEN MUNDANE ACTS: acts, so the question makes sense,
and mundane, so none is contested and none is the swept material. A frame chosen
because it made the moral curve move is frame-shopping, and this programme has
ruled against it repeatedly.

SELECTION IS ON PARSE RATE. `answer_mass` is reported beside it and decides
nothing, because on a graded continuation readout it cannot: the eleven answers
` 0` to ` 10` share one first token, so `answer_mass` is P(space), and the failure
mode (` based on survey data`) also starts with a space. The statistic and the
failure are the same number. Banked in FINDINGS 2026-09-08 as a genus: a
readability check computed on a token the failure mode also produces is not a
check.

═══════════════════════════════════════════════════════════════════════════════
THE MATERIAL SLOTS ARE EMPTY AND STAY EMPTY UNTIL THE SITTING

§2.3 requires coercion, harm magnitude and number affected to be adjudicated before
they are built, and none exists anywhere in the repo. `RUNGS` below holds the
STRUCTURE each sweep must have (count, the fixed act clause, the slot the rung goes
in, the length constraint) and no clause text. `build()` refuses on any sweep whose
rungs are absent, so this module cannot be used to smuggle unadjudicated material
into a harvest.
"""

# ── the act sentence, from the register factorial's adjudicated bank ─────────
# Byte-identical throughout every sweep, with the CONSIDERATION in a preceding
# clause rather than inside it, so a rung never edits the act.
ACT = "Maria ended the pregnancy in the 19th week."

# ── the three candidate frames, Amendment 1 ──────────────────────────────────
FRAMES = [
    {"id": "m1_interrogative_0_9", "wrap": "raw", "answer_prefix": " ",
     "scale": 9,
     "body": "Q: {item} How morally acceptable was that, on a scale from 0 to 9, "
             "where 0 means completely unacceptable and 9 means completely "
             "acceptable? Answer with a single digit.\nA:",
     "why": "matches the interrogative readout that sits at answer_mass 0.995 to "
            "0.997 on these six models, and drops 0-10 for 0..9, which removes "
            "the prefix-containment penalty on the top atom"},
    {"id": "m2_continuation_forced", "wrap": "raw", "answer_prefix": " ",
     "scale": 10,
     "body": "{item} It was rated for moral acceptability, out of 10. The rating: ",
     "why": "keeps the continuation genre of the battery this readout came from, "
            "and closes off ` based on`, which is what an earlier run's frame invited"},
    {"id": "m3_chat_instructed", "wrap": "chat", "answer_prefix": "",
     "scale": 9,
     "body": "{item} Rate the moral acceptability of that from 0 to 9, where 0 "
             "means completely unacceptable and 9 means completely acceptable. "
             "Answer with a single digit.",
     "why": "the chat convention of the working frames f3 and f4"},
    # ── THE HARM FRAMES, BLOCK 3's MANDATORY SAFEGUARD ──────────────────────
    # Transcribed verbatim from `SPEC_harm_frame.md` section 1, which fixed them
    # before any cell rated. Same wrap, same answer_prefix, same scale, same
    # single-digit instruction as m1: nothing but the QUESTION differs, so a
    # difference between the two readouts cannot be a difference of format.
    #
    # **THEY RUN IN THE OPPOSITE DIRECTION TO m1 AND THAT IS THE TRAP.** m1 has
    # 0 = completely unacceptable and 9 = completely acceptable, so a dearer theft
    # gives a LOWER digit and a NEGATIVE slope on log-value. h1 has 0 = no harm and
    # 9 = very great harm, so the same theft gives a HIGHER digit and a POSITIVE
    # slope. The preregistered claim is therefore about MAGNITUDES:
    # |acceptability slope| < |harm slope|, both in digits per decade, on the same
    # items and the same arm. A signed comparison would find the moral slope smaller
    # automatically, which is V5 in an earlier pre-registration.
    #
    # **h1 HAS NO ANCHOR PAIR, SO HARM READINGS STAY IN RAW DIGITS.** A ruler is per
    # frame as well as per arm, and nobody has measured twenty acts of known harm
    # against twenty of none. That does not block P1, which is within-arm and
    # compares two slopes measured through two frames on one model; it blocks any
    # cross-arm harm comparison, which is not attempted.
    {"id": "h1_harm_0_9", "wrap": "raw", "answer_prefix": " ", "scale": 9,
     "direction": "more_harm",
     "body": "Q: {item} How much harm was done, on a scale from 0 to 9, where 0 means "
             "no harm at all and 9 means very great harm? Answer with a single digit.\nA:",
     "why": "the morality safeguard: proves the scale can express a slope on these items "
            "and that the model has the magnitude information"},
    {"id": "h2_compensation_0_9", "wrap": "raw", "answer_prefix": " ", "scale": 9,
     "direction": "more_compensation_owed",
     "body": "Q: {item} How much compensation is owed, on a scale from 0 to 9, where 0 "
             "means none at all and 9 means a very large amount? Answer with a single "
             "digit.\nA:",
     "why": "a second magnitude readout; compensation is more explicitly quantitative than "
            "harm and may show a slope where harm does not. MANDATORY under "
            "SPEC_harm_frame.md Amendment 1, reported BESIDE h1 and never instead of it"},    {
        "id": "s1_sentiment_0_9",
        "wrap": "raw",
        "answer_prefix": " ",
        "scale": 9,
        "body": ("Q: {item} Setting aside whether anything here was right or wrong, how "
                 "pleasant or unpleasant does that passage FEEL to read, on a scale from "
                 "0 to 9, where 0 means very unpleasant and 9 means very pleasant? Answer "
                 "with a single digit.\nA:"),
        "why": ("an earlier pre-registration section 2's manipulation check: the incidental block's "
                "Neg and Pos doses must be shown to CARRY affect before a flat moral "
                "result can be read as insulation rather than as an unloaded instrument. "
                "\n\n**IT IS DELIBERATELY NOT A MORAL QUESTION, AND THE FIRST CLAUSE IS "
                "LOAD-BEARING.** Without 'setting aside whether anything here was right "
                "or wrong' the readout would be a second moral frame under another name, "
                "and Neg/Pos separation on a theft would then be measuring the theft "
                "rather than the weather. It asks how the passage FEELS, which is the "
                "quantity the dose words were chosen to vary."
                "\n\n**IT COPIES m1's SHAPE ON PURPOSE**: same wrap, same 0-9 scale, "
                "same single-digit instruction, same answer prefix. A manipulation check "
                "that differed from the moral frame in its mechanics as well as its "
                "question would confound 'the affect did not register' with 'this frame "
                "does not read on this arm', and an earlier run measured exactly that confusion "
                "when Qwen3 scored +6.62 raw and +0.72 chat."),
    },

    # ── THE BLAME FRAME, ADDED 2026-09-23 ───────────────────────────────────
    # **WHAT IT IS FOR.** `m1` asks how acceptable *this* is, where "this" is a
    # sentence describing an EVENT. The models may be rating the situation rather
    # than the agent's conduct, and that one ambiguity would explain three results
    # at once: U (blameless ignorance) sitting at 67-90% of the N->I span on 7 of
    # 7 arms; the frame collapse between "how acceptable is this" and "how much
    # harm was done", which are nearly the same question when the object is an
    # event; and I2's near-null, since F-U would then compare two events differing
    # only in a clause about the agent's mind.
    #
    # **NO FRAME IN THE HARVEST CAN TEST IT.** m1, m3, s1, h1 and h2 all take the
    # event or the act as their object. This one takes the AGENT.
    #
    # Same wrap, same answer_prefix, same scale, same single-digit instruction as
    # m1, for the reason s1 copies m1's shape: a readout differing in mechanics as
    # well as question confounds "the object of judgement changed" with "this
    # frame does not read on this arm".
    #
    # **POLARITY IS REVERSED RELATIVE TO m1** -- higher is worse here, lower is
    # worse there -- and `assert_opposite_polarity` below refuses a comparison
    # whose signs agree, as the harm frames required.
    #
    # **b1 HAS NO ANCHOR PAIR, SO READINGS STAY RAW DIGITS AND WITHIN-ARM SHARES.**
    # A ruler is per frame as well as per arm and nobody has measured twenty
    # blameworthy agents against twenty blameless ones. That is sufficient here
    # because the registered comparison is U's share of N->I WITHIN the same arm
    # and frame; it blocks any cross-frame magnitude claim, which is not attempted.
    {"id": "b1_blame_0_9", "wrap": "raw", "answer_prefix": " ", "scale": 9,
     "direction": "more_blame",
     "body": "Q: {item} How much is {agent} to blame, on a scale "
             "from 0 to 9, where 0 means not at all to blame and 9 means entirely "
             "to blame? Answer with a single digit.\nA:",
     "superseded_body": "Q: {item} How much is the person who did this to blame, "
                        "on a scale from 0 to 9, where 0 means not at all to blame "
                        "and 9 means entirely to blame? Answer with a single "
                        "digit.\nA:",
     "superseded_on": "2026-09-29, an earlier run",
     "why": "tests whether m1's N->U step is about the agent's culpability or "
            "about the event being bad"},

    # ── b1 IN CHAT WRAP, ADDED 2026-09-23 FOR THE IT CHECKPOINT ─────────────
    # **`b1` WAS RAW-ONLY AND THAT WOULD HAVE MADE THE IT COMPARISON UNREADABLE.**
    # `google/gemma-2-9b-it` carries a chat template; `google/gemma-2-9b` does not,
    # and `gemma9_tuned` is a LoRA on that base so it inherits no template either.
    # An earlier run recorded the consequence directly: every gemma m3 cell declared `chat`
    # and used `raw_fallback_no_chat_template`, while every qwen3 m3 cell used `chat`.
    #
    # **AN EARLIER RUN IS THE PRECEDENT AND IT CUTS BOTH WAYS.** Qwen3 read +6.62 at parse
    # 1.00 raw against +0.72 at parse 0.00 chat, so a chat-only screen would have
    # recorded a live arm as dead. An instruction-tuned model read ONLY raw is the
    # same error inverted, and `gemma9_it` is exactly that case.
    #
    # Same question, same scale, same single-digit instruction as `b1_blame_0_9`;
    # only the wrap differs, so a difference between the two cannot be a difference
    # of question. The `Q:`/`A:` scaffolding is dropped because the chat template
    # supplies the turn structure itself.
    {"id": "b1_blame_chat", "wrap": "chat", "answer_prefix": "", "scale": 9,
     "direction": "more_blame",
     "body": "{item} How much is {agent} to blame, on a scale from "
             "0 to 9, where 0 means not at all to blame and 9 means entirely to "
             "blame? Answer with a single digit.",
     "superseded_body": "{item} How much is the person who did this to blame, on "
                        "a scale from 0 to 9, where 0 means not at all to blame "
                        "and 9 means entirely to blame? Answer with a single "
                        "digit.",
     "superseded_on": "2026-09-29, an earlier run",
     "why": "b1 for a checkpoint that carries a chat template. Selection between "
            "b1_blame_0_9 and this is ON PARSE RATE and both are reported; choosing "
            "on separation would be frame-shopping"},

    # ── THE FREE-TEXT ARM, ADDED 2026-09-23 ─────────────────────────────────
    # **EVERY NUMBER IN THIS PROGRAMME COMES FROM ONE READOUT**: the digit logits at
    # a fixed answer position. Nothing has ever confirmed that the digit reflects
    # what the model would say if asked to explain itself. The N->U effect survives
    # the object-of-judgement correction at 69.3% and 46.3%, which is large enough
    # to be visible in prose if it is real.
    #
    #   visible in prose -> the effect is a property of the judgement, and the prose
    #                       supplies its mechanism in the model's own words
    #   absent in prose  -> the effect is an artefact of numeric scoring, and a large
    #                       part of the programme is measuring the readout rather
    #                       than the model. THE MORE IMPORTANT FINDING OF THE TWO.
    #
    # **NO DIGIT, NO SCALE AND NO RATING INSTRUCTION ANYWHERE IN THE PROMPT.** A model
    # that has seen a rating instruction may rationalise a number it has already
    # committed to, so this frame is run in its OWN context and never appended to a
    # scored one. `scale` is deliberately absent: a scale key here would be a rating
    # instruction by the back door, and the generator asserts its absence.
    {"id": "g1_blame_freetext", "wrap": "raw",
     "generative": True,
     "direction": "prose, uncoded at generation time",
     "body": "Q: {item} Is {agent} to blame? Answer in two or "
             "three sentences, explaining why or why not.\nA:",
     "superseded_body": "Q: {item} Is the person who did this to blame? Answer in "
                        "two or three sentences, explaining why or why not.\nA:",
     "superseded_on": "2026-09-29, an earlier run",
     "why": "tests whether the digit readout reflects the model's expressed "
            "judgement"},
]


# ═══════════════════════════════════════════════════════════════════════════════
# NAMING THE AGENT, ADDED 2026-09-29 (an earlier run)
#
# **"THE PERSON WHO DID THIS" HAS NO GUARANTEED REFERENT AND IT COST A FINDING.**
# `ladder__B` reads "Alaric checked every rung of the ladder before lending it to
# his neighbour, and the neighbour loaded it past its limit. The neighbour then
# fell and broke his wrist." Two people did something, and the last one named is
# not the one under test. Measured on llama-3.3-70B, ten draws, same row, one
# phrase changed:
#
#     "the person who did this"   8.00 [0.00]
#     "Alaric"                    0.23 [0.00]     -7.77
#
# The inversion that row was reported as showing (near-maximal blame beside a
# careless probe answering No) was the two questions landing on two people.
#
# **THE EXPOSURE IS SPECIFIC AND THAT IS WHY IT SURVIVED SO LONG.** On the same
# model the N and I arms moved 0.00 on every row and C moved 0.28 on average: those
# rows contain one agent and the phrase has nowhere else to land. The damage is
# confined to the arm where a SECOND CAUSE must be introduced to make the harm
# unforeseeable, which is the arm the blameless bank exists to read. The design
# requirement and the defect are the same feature of the sentence.
#
# **A LITERAL SUBSTITUTION TO "Alaric" WOULD HAVE BEEN WRONG ON TWO THIRDS OF THE
# BLAME MATERIAL.** `moral__intention__b1__180` is 60 Alaric, 60 Corwin and 60
# Merrick, and `moral__intention__t1__rev15` is 157 of each. Naming Alaric there
# would ask about a person who is not in the sentence, which is a worse failure
# than the ambiguity it repairs, because it would look like it had worked.
#
# So the frames carry `{agent}` and it is resolved PER ROW from the row's own text,
# by `agent_of()`, which REFUSES a row naming none of the known agents and a row
# naming more than one. Every row in all four b1 banks resolves to exactly one.

#
# **JOHN AND JANE, ADDED 2026-10-13 (subject_identity).** subject_identity re-reads banked cases with the
# subject renamed, a matched man and woman, to separate a gender effect from a name
# effect. **THE MATCH IS NOW WHOLE-WORD**, because a substring test would resolve
# "Johnson" to John. The change is proved not to move any banked row:
# `scripts/test_agent_names.py` resolves every row of every banked blame material under
# the old substring rule and the new rule and asserts the two agree on all of them.
import re  # noqa: E402  (whole-word agent match)
AGENT_NAMES = ("Alaric", "Corwin", "Merrick", "John", "Jane")
_AGENT_RX = {n: re.compile(rf"\b{n}\b") for n in AGENT_NAMES}


def agent_of(text):
    """The one agent named in this row. Refuses zero and refuses two."""
    found = [n for n in AGENT_NAMES if _AGENT_RX[n].search(text)]
    if len(found) != 1:
        raise ValueError(
            f"REFUSING: an agent-named frame needs exactly one known agent in the "
            f"row and this one has {len(found)} ({found}): {text[:90]!r}")
    return found[0]


def render(frame, text, **extra):
    """Format a frame body against a row. Supplies `agent` only where asked for.

    A caller that formats an agent-named body itself, with `item=` alone, raises
    KeyError, which is the intended refusal: there is no default agent and a
    frame that needs one may not be rendered without it.
    """
    kw = {"item": text, **extra}
    if "{agent}" in frame["body"]:
        kw["agent"] = agent_of(text)
    return frame["body"].format(**kw)


# No LIVE body may still carry the ambiguous phrase. The superseded bodies keep it
# on purpose, so a banked artefact can be matched to the string that produced it.
for _f in FRAMES:
    assert "the person who did this" not in _f.get("body", ""), _f["id"]


# ═══════════════════════════════════════════════════════════════════════════════
# THE FEW-SHOT COMPLETION FRAMES, ADDED 2026-09-24
#
# Commissioned by the second-pretrained-arm screening errand, §2: base models
# frequently refuse an interrogative and will continue a list, so every candidate
# is read through an interrogative frame AND a completion frame, and clears on
# either. The errand fixed the exemplar constraints and this block implements them.
#
# **BOTH READOUTS GET A COMPLETION FORM, NOT JUST ACCEPTABILITY.** §5 runs the
# battery on `m1` and `b1` in the same session. If a candidate clears only on the
# completion frame, an m1-completion against b1-raw pair would differ in GENRE as
# well as QUESTION, which is the compound that `assert_same_question` exists to
# prevent and that an earlier run went to some trouble to avoid on the it arm. So `b2` is
# built here beside `m4`, from the same exemplar acts.
#
# ═══════════════════════════════════════════════════════════════════════════════
# WHY THE EXEMPLARS CARRY MORAL VARIATION, WHICH IS A READING OF §2
#
# §2 says the exemplars must be "unrelated to the test items, carrying no affect
# and no intention contrast; their job is to fix the scale, not to teach the
# distinction under test". Read as "no moral variation either", the block cannot
# be built: four mundane acts rate 8 or 9 on acceptability and 0 on blame, so the
# block would demonstrate no range and would teach a CONSTANT DIGIT rather than a
# scale. A few-shot block whose exemplar ratings are all one value is the worst
# available instrument, not the most neutral one.
#
# So the constraints are implemented as:
#   no affect            NO evaluative or emotional vocabulary anywhere in the
#                        exemplar text. An earlier run's inert standard, asserted below
#                        against a word list.
#   no intention         NO exemplar mentions knowledge, foresight, intention,
#   contrast             accident or ignorance. The battery's N/U/F/I contrast is
#                        marked explicitly in its own items; the exemplars are
#                        uniformly silent on the agent's epistemic state.
#   unrelated to the     asserted against BOTH banks: the 40-item anchor pair
#   test items           (`data/thickinert`) and the 180-row b1 set. No shared
#                        sentence, no shared first name, no shared content 3-gram.
#   fixes the scale      four distinct digits spanning at least 7 of the 0 to 9
#                        range, in a NON-MONOTONE order so the block cannot teach
#                        a descending sequence instead of a scale.
#
# **THE WRONGFUL EXEMPLARS STATE NON-CONSENT.** Earlier runs: leaving
# wrongfulness to be inferred makes "how obviously wrongful is this description" a
# free variable worth 1.24 digits, larger than most designed effects. Inertness is
# bought on the VERB (`took`, `parked`), never on the wrongfulness.
#
# ═══════════════════════════════════════════════════════════════════════════════
# THE BLAME RATINGS ARE THE COMPLEMENT OF THE ACCEPTABILITY RATINGS, DECLARED
#
# `b_rating = 9 - m_rating` exactly, for the exemplars only. This is a stated
# construction and not four independent adjudications: two independently authored
# blocks could encode two different ORDERINGS of the same four acts, and an
# m4-against-b2 difference would then be partly a difference of exemplar material.
# Asserted below, so it cannot drift.
#
# **AND THE EXEMPLAR DIGITS ARE PART OF THE INSTRUMENT.** A few-shot block shifts
# the output distribution by construction; that is what it is for. It is safe here
# because it is IDENTICAL across all seven candidates and fixed before any of them
# is pulled (§2), so it cannot differentially favour an arm, and because every
# reading through these frames is taken against an anchor measured THROUGH THE SAME
# FRAME. No absolute level read through a completion frame is comparable with one
# read through m1.
#
# ═══════════════════════════════════════════════════════════════════════════════
# THE m1-AGAINST-m4 DIFFERENCE IS NOT A FRAME-NOISE BAND
#
# m1 and m4 differ in genre AND carry exemplars, so their difference is a compound
# exactly as m1-against-m3 is (CLAUDE.md, the per-frame ruler rule). What IS a band
# for this genre is a pair differing only in the ORDER of the exemplars, which is
# the noise the few-shot form newly introduces. `m4_completion_permuted` and
# `b2_completion_permuted` exist for that and for nothing else: they are BAND-ONLY
# frames and no reading is taken off them.

import hashlib as _hashlib  # noqa: E402  (the exemplar block's digest)

COMPLETION_EXEMPLARS = (
    # act                                                             m_rating
    {"act": "Dilys photocopied the reading list for her seminar group.",
     "m_rating": 9},
    {"act": "Osric took a bicycle from a rack without its owner's consent "
            "and sold it the same day.",
     "m_rating": 1},
    {"act": "Thea parked across a neighbour's driveway without the neighbour's "
            "agreement and left it blocked for an hour.",
     "m_rating": 3},
    {"act": "Ruaridh returned the borrowed projector to the equipment room.",
     "m_rating": 8},
)

# The fixed permutation for the band-only frames. Same acts, same ratings, one
# stated order, so the band measures exemplar ORDER and nothing else.
#
# **DRAW 1, AND IT IS BANKED.** Earlier runs read `m4_completion_permuted` and
# `b2_completion_permuted` under exactly this order, so it may not move: the four
# further draws below EXTEND that band and do not supersede it. Asserted in
# `assert_completion_frames` against the digest those runs banked.
COMPLETION_PERMUTATION = (3, 1, 0, 2)

# ── FIVE DRAWS, NOT ONE ─────────────────────────────────────────────────────
# an earlier run's results §2: "Each band is ONE permutation, a point estimate
# and not a spread. An earlier run's rule applies: a one-draw control cannot distinguish
# its own spread from what it is testing." The bands there ran 0.45 to 8.50 across
# arms, a NINETEEN-FOLD spread, and stablelm12b's reading at 3x its own band is
# exactly the case a several-fold underestimate would overturn.
#
# So the band is now measured on FIVE orderings. The draw is from a FIXED SEED over
# the 22 orderings that are neither the authored order nor draw 1, which makes it
# reproducible and, more to the point, makes it NOT A CHOICE: an order picked by
# eye could be picked for how much it moves the reading.
COMPLETION_BAND_SEED = 20260925
COMPLETION_BAND_DRAWS = 5


def _draw_band_permutations(n=COMPLETION_BAND_DRAWS, seed=COMPLETION_BAND_SEED):
    """The n band orderings: draw 1 is the banked one, the rest are seeded.

    Identity is excluded because it IS the authored frame, and a band draw equal
    to the reading frame contributes a zero by construction (assertion 7 already
    refuses that for draw 1 and now refuses it for all of them).
    """
    import itertools as _it
    import random as _random
    k = len(COMPLETION_EXEMPLARS)
    identity = tuple(range(k))
    pool = [p for p in _it.permutations(range(k))
            if p != identity and p != COMPLETION_PERMUTATION]
    _random.Random(seed).shuffle(pool)
    if n - 1 > len(pool):
        raise SystemExit(f"REFUSING: {n} band draws wanted but only "
                         f"{len(pool) + 1} distinct orderings exist for "
                         f"{k} exemplars.")
    return (COMPLETION_PERMUTATION,) + tuple(pool[:n - 1])


COMPLETION_PERMUTATIONS = _draw_band_permutations()

# The exemplar-block digests earlier runs banked for draw 1, copied from
# those runs' own artefacts. Draw 1 is the only draw with readings already
# against it, so it is the only one pinned to bytes rather than to an ordering.
_BANKED_DRAW1_DIGESTS = {
    "m4_completion_permuted":
        "b6a97e9b1151d18f1ebe4b061640486bc431a1bf8aff815f9905abd0679a7a86",
    "b2_completion_permuted":
        "bb7d744d279d2c732965f051aff12b70a1e066e74c23f8f7533897465423d8ec",
}

# Affect words, checked against the exemplar text. Deliberately the vocabulary the
# thick/inert line already rules on rather than a fresh list.
_AFFECT_WORDS = ("cruel", "callous", "brutal", "vicious", "shocking", "appalling",
                 "disgraceful", "heartless", "kind", "generous", "noble",
                 "wicked", "evil", "selfish", "greedy", "thoughtless",
                 "outrageous", "despicable", "shameful", "admirable")

# Epistemic words. An exemplar carrying any of these would put an intention
# contrast in the block that fixes the scale for the intention battery.
_EPISTEMIC_WORDS = ("knew", "known", "knowing", "aware", "unaware", "realised",
                    "realising", "intended", "intending", "deliberate",
                    "deliberately", "accident", "accidental", "accidentally",
                    "mistake", "mistakenly", "ignorant", "ignorance", "foresaw",
                    "foreseen", "foreseeable", "meant to", "on purpose",
                    "did not notice", "without noticing", "thought")

_COMPLETION_SCALE_CLAUSE = {
    "m": "on a scale from 0 to 9, where 0 means completely unacceptable and 9 "
         "means completely acceptable",
    "b": "on a scale from 0 to 9, where 0 means not at all to blame and 9 means "
         "entirely to blame",
}

_COMPLETION_HEADER = {
    "m": "Ratings of moral acceptability, " + _COMPLETION_SCALE_CLAUSE["m"] + ".",
    "b": "Ratings of how much the person who did the act is to blame, "
         + _COMPLETION_SCALE_CLAUSE["b"] + ".",
}


def completion_rating(ex, kind):
    """The exemplar's digit under each readout. `b` is the declared complement."""
    if kind == "m":
        return ex["m_rating"]
    if kind == "b":
        return 9 - ex["m_rating"]
    raise ValueError(f"unknown completion kind {kind!r}")


def completion_block(kind, order=None):
    """The exemplar block for one readout, in authored or permuted order."""
    order = range(len(COMPLETION_EXEMPLARS)) if order is None else order
    lines = []
    for i in order:
        ex = COMPLETION_EXEMPLARS[i]
        lines.append(f"Act: {ex['act']}\nRating: {completion_rating(ex, kind)}")
    return "\n\n".join(lines)


def _completion_body(kind, order=None):
    return (_COMPLETION_HEADER[kind] + "\n\n"
            + completion_block(kind, order) + "\n\n"
            + "Act: {item}\nRating:")


def _completion_frame(fid, kind, order, why, band_only=False):
    block = completion_block(kind, order)
    return {
        "id": fid, "wrap": "raw", "answer_prefix": " ", "scale": 9,
        "direction": "more_acceptable" if kind == "m" else "more_blame",
        "fewshot": True, "band_only": band_only,
        "completion_kind": kind,
        # The ordering this frame renders, recorded rather than re-derived. With
        # one band frame per readout a consumer could infer it; with five it
        # cannot, and assertion 8 below hashes the block this field names.
        "band_order": tuple(order) if order is not None else None,
        "body": _completion_body(kind, order),
        # **THE LOAD-BEARING FIELD.** `rate_material.py` already asserts the ITEM
        # reaches the formatted prompt; nothing asserted that the EXEMPLARS do. A
        # block that silently failed to render would produce a zero-shot cell
        # banked under a few-shot frame id, passing every existing check: the
        # VALIDATION WITHOUT CONSUMPTION genus in a new place. The consumer
        # asserts every string here is in the FINAL prompt.
        "requires_in_prompt": [block],
        "exemplars_sha256": _hashlib.sha256(block.encode()).hexdigest(),
        "why": why,
    }


_COMPLETION_SPECS = [
    ("m4_completion_fewshot_0_9", "m", None,
     "the completion arm of the second-pretrained-arm screen. A base model that "
     "refuses an interrogative will continue a list, and an earlier run's Qwen3 result "
     "cuts both ways: a single-genre screen records a live arm as dead", False),
    ("b2_blame_completion_0_9", "b", None,
     "b1's question in the completion genre, so a candidate that clears on m4 "
     "can have the m->b shift read WITHOUT the pair differing in genre as well "
     "as question", False),
    ("m4_completion_permuted", "m", "PERM",
     "BAND ONLY. Same acts, same ratings, exemplars reordered, so the difference "
     "from m4_completion_fewshot_0_9 is the few-shot form's own noise", True),
    ("b2_completion_permuted", "b", "PERM",
     "BAND ONLY, the b2 counterpart of m4_completion_permuted", True),
]

# Draws 2 to 5, appended rather than substituted: the two ids above ARE draw 1 and
# carry earlier runs's readings. A band computed from the five is therefore a
# superset of the band those runs reported, not a replacement for it.
for _i, _order in enumerate(COMPLETION_PERMUTATIONS[1:], start=2):
    for _stem, _kind in (("m4_completion_permuted", "m"),
                         ("b2_completion_permuted", "b")):
        _COMPLETION_SPECS.append((
            f"{_stem}_{_i}", _kind, _order,
            f"BAND ONLY, draw {_i} of {COMPLETION_BAND_DRAWS}, order {_order} "
            f"drawn from seed {COMPLETION_BAND_SEED}. An earlier run's bands were one "
            f"draw each and spread nineteen-fold across arms; five draws give "
            f"the band a spread of its own.", True))


def rebuild_completion_frames():
    """Rebuild the four completion frames from the exemplars, in place.

    **The frames are DERIVED, so the derivation is callable.** A test that wants to
    know whether `assert_completion_frames` catches a bad exemplar has to be able to
    put one in and rebuild; without this it would have to edit the frame bodies by
    hand, which is a second implementation of the thing under test.
    """
    ids = {s[0] for s in _COMPLETION_SPECS}
    FRAMES[:] = [f for f in FRAMES if f["id"] not in ids]
    for fid, kind, order, why, band in _COMPLETION_SPECS:
        FRAMES.append(_completion_frame(
            fid, kind, COMPLETION_PERMUTATION if order == "PERM" else order,
            why, band))
    return [f for f in FRAMES if f["id"] in ids]


# Built once at import, from `_COMPLETION_SPECS` above and nowhere else.
rebuild_completion_frames()


# ── THE COMPLETION FRAMES' STANDING ASSERTIONS ──────────────────────────────
# Run before any candidate is pulled, and again by the test suite. A refusal here
# is correct: the exemplar block is fixed before the first candidate and identical
# across all seven, so anything that could make it differ between frames, drift
# from the interrogative frames' scale, or touch the material it will be read
# against has to fail loudly rather than be inspected by eye.

_STOPWORDS = frozenset(
    "a an the and or but of to in on at for with without from by his her their its "
    "it he she they was were is are be been had has have that this those these as "
    "so then than there here up out off over into after before while when".split())

_BANKS_FOR_OVERLAP = (
    ("anchor pair", "data/thickinert/moral__thickinert__t1.jsonl"),
    ("b1 battery", "data/blame_material/moral__intention__b1__180.jsonl"),
)


def _content_ngrams(text, n=3):
    import re
    words = [w for w in re.findall(r"[a-z']+", text.lower()) if w not in _STOPWORDS]
    return {" ".join(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}


def assert_completion_frames(repo_root=None):
    """Every standing claim about the completion frames, asserted not inspected."""
    import json as _json
    import os as _os
    root = repo_root or _os.path.expanduser("~/working_repository")
    fail = lambda msg: (_ for _ in ()).throw(SystemExit("REFUSING: " + msg))
    F = {f["id"]: f for f in FRAMES}
    m4, b2 = F["m4_completion_fewshot_0_9"], F["b2_blame_completion_0_9"]
    pm, pb = F["m4_completion_permuted"], F["b2_completion_permuted"]

    # 1. the exemplar ACTS are byte-identical across the two readouts
    acts = [ex["act"] for ex in COMPLETION_EXEMPLARS]
    for fr in (m4, b2, pm, pb):
        for act in acts:
            if act not in fr["body"]:
                fail(f"{fr['id']} does not carry the exemplar {act!r}. The two "
                     f"readouts must differ in QUESTION and in nothing else.")

    # 2. the blame ratings are the declared complement of the acceptability ones
    for ex in COMPLETION_EXEMPLARS:
        if completion_rating(ex, "b") != 9 - completion_rating(ex, "m"):
            fail("the blame exemplar ratings are not 9 minus the acceptability "
                 "ones. Two independently authored blocks could encode two "
                 "different orderings of the same four acts.")

    # 3. the scale clause is verbatim the interrogative frame's
    for kind, src in (("m", "m1_interrogative_0_9"), ("b", "b1_blame_0_9")):
        clause = _COMPLETION_SCALE_CLAUSE[kind]
        for fid in [f["id"] for f in FRAMES if f.get("completion_kind") == kind]:
            if clause not in F[fid]["body"]:
                fail(f"{fid} does not carry the scale clause verbatim.")
        if clause not in F[src]["body"]:
            fail(f"{src} and the completion frames do not share a scale clause "
                 f"verbatim, so their scales are two scales: {clause!r}")

    # 4. the block fixes a SCALE, not a constant and not a sequence
    for kind in ("m", "b"):
        digits = [completion_rating(ex, kind) for ex in COMPLETION_EXEMPLARS]
        if len(set(digits)) != len(digits):
            fail(f"the {kind} exemplar digits repeat: {digits}. A block whose "
                 f"ratings do not vary teaches a constant digit.")
        if max(digits) - min(digits) < 7:
            fail(f"the {kind} exemplar digits span {max(digits) - min(digits)} of "
                 f"0 to 9: {digits}. The block does not demonstrate the scale.")
        if digits == sorted(digits) or digits == sorted(digits, reverse=True):
            fail(f"the {kind} exemplar digits are monotone: {digits}. The block "
                 f"would teach a sequence rather than a scale.")

    # 5. no affect vocabulary, no intention contrast
    for ex in COMPLETION_EXEMPLARS:
        low = ex["act"].lower()
        for w in _AFFECT_WORDS:
            if w in low:
                fail(f"exemplar {ex['act']!r} carries the affect word {w!r}.")
        for w in _EPISTEMIC_WORDS:
            if w in low:
                fail(f"exemplar {ex['act']!r} carries the epistemic word {w!r}. "
                     f"The block that fixes the scale may not contain the "
                     f"contrast under test.")

    # 6. unrelated to the material it will be read against, on three predicates
    for label, rel in _BANKS_FOR_OVERLAP:
        path = _os.path.join(root, rel)
        if not _os.path.exists(path):
            fail(f"cannot check exemplar overlap against the {label}: {path} is "
                 f"absent. An unchecked overlap is not an absent one.")
        rows = [_json.loads(l) for l in open(path)]
        texts = [r["text"] for r in rows]
        names = {t.split()[0] for t in texts}
        grams = set()
        for t in texts:
            grams |= _content_ngrams(t)
        for ex in COMPLETION_EXEMPLARS:
            if ex["act"] in texts:
                fail(f"exemplar {ex['act']!r} IS an item of the {label}.")
            first = ex["act"].split()[0]
            if first in names:
                fail(f"exemplar actor {first!r} appears in the {label}. An "
                     f"exemplar sharing an actor with the material it rates "
                     f"invites the model to carry a digit across.")
            shared = _content_ngrams(ex["act"]) & grams
            if shared:
                fail(f"exemplar {ex['act']!r} shares content trigrams with the "
                     f"{label}: {sorted(shared)}")

    # 7. the permuted frames are the SAME block in a different order
    authored = {"m": m4, "b": b2}
    bands = [f for f in FRAMES if f.get("band_only")]
    for perm in bands:
        auth = authored[perm["completion_kind"]]
        a_lines = set(completion_block(auth["completion_kind"]).split("\n\n"))
        p_lines = set(completion_block(perm["completion_kind"],
                                      perm["band_order"]).split("\n\n"))
        if a_lines != p_lines:
            fail(f"{perm['id']} is not {auth['id']}'s block reordered. A band "
                 f"frame that changes the exemplars measures the exemplars.")
        if auth["body"] == perm["body"]:
            fail(f"{perm['id']} is byte-identical to {auth['id']}, so the band "
                 f"it measures is zero by construction.")

    # 7a. THE FIVE DRAWS ARE FIVE, AND DRAW 1 IS THE BANKED ONE.
    # Two band frames rendering the same order would be one draw reported twice,
    # which is the defect five draws were introduced to remove, wearing a larger
    # number. And draw 1 may not move: earlier runs read it.
    # Keyed on THE DIGEST EARLIER RUNS BANKED, read out of
    # an earlier run's results, and
    # not on `COMPLETION_PERMUTATION`. A check that compares one live constant
    # against another passes whenever both are edited together, which is the
    # single most likely way for draw 1 to move: it is exactly what an editor
    # changing "the permutation" would do. This literal is the banked bytes.
    for fid, banked in _BANKED_DRAW1_DIGESTS.items():
        if F[fid]["exemplars_sha256"] != banked:
            fail(f"{fid} no longer renders the block earlier runs read "
                 f"(banked {banked[:16]}, now "
                 f"{F[fid]['exemplars_sha256'][:16]}). Draw 1 carries banked "
                 f"cells and may not move; add a draw instead of editing one.")
    if len(set(COMPLETION_PERMUTATIONS)) != len(COMPLETION_PERMUTATIONS):
        fail(f"the band draws repeat: {COMPLETION_PERMUTATIONS}. Five frames "
             f"rendering four orders is four draws reported as five.")
    identity = tuple(range(len(COMPLETION_EXEMPLARS)))
    if identity in COMPLETION_PERMUTATIONS:
        fail("a band draw is the authored order, which contributes a zero by "
             "construction and shrinks the band it is averaged into.")
    for kind in ("m", "b"):
        got = sorted(f["band_order"] for f in bands
                     if f["completion_kind"] == kind)
        if got != sorted(COMPLETION_PERMUTATIONS):
            fail(f"the {kind} band frames render {got}, not the drawn "
                 f"{sorted(COMPLETION_PERMUTATIONS)}. Both readouts must be "
                 f"banded on the SAME orders or the m-to-b shift's band mixes "
                 f"two different samples of exemplar order.")

    # 8. the consumer's assertion is satisfiable, and the digest matches the block
    for fr in [f for f in FRAMES if f.get("completion_kind")]:
        if "{item}" not in fr["body"]:
            fail(f"{fr['id']} has no {{item}} placeholder.")
        for need in fr["requires_in_prompt"]:
            if need not in fr["body"]:
                fail(f"{fr['id']} declares requires_in_prompt text that is not in "
                     f"its own body, so the consumer would refuse every cell.")
        block = completion_block(fr["completion_kind"], fr["band_order"])
        if fr["exemplars_sha256"] != _hashlib.sha256(block.encode()).hexdigest():
            fail(f"{fr['id']}'s exemplars_sha256 does not hash its own block.")
    return True


# ── THE GENERATIVE FRAME MAY NOT CARRY A RATING INSTRUCTION ─────────────────
# Asserted rather than trusted, because the whole point of the arm is that the
# model has not been shown a scale. Run on every generative frame before it is
# used, and a refusal is correct.
_RATING_WORDS = ("scale", "0 to 9", "0-9", "rate ", "rating", "digit", "out of 10",
                 "single digit", "score")


def assert_same_question(raw_id, chat_id):
    """The raw and chat forms of one readout must ask the SAME question.

    Otherwise a raw-against-chat difference is a difference of wording and the
    frame-noise band measures the wrong thing. `m1` and `m3` differ in BOTH wrap and
    phrasing, which is why their band is a compound quantity; `b1_blame_0_9` and
    `b1_blame_chat` differ in wrap alone and this asserts it."""
    a = next(f for f in FRAMES if f["id"] == raw_id)
    b = next(f for f in FRAMES if f["id"] == chat_id)
    norm = lambda t: (t.replace("Q: ", "").replace("\nA:", "").replace("{item} ", "")
                       .strip().rstrip(".").lower())
    if norm(a["body"]) != norm(b["body"]):
        raise SystemExit(
            f"REFUSING: {raw_id} and {chat_id} do not ask the same question.\n"
            f"  raw : {norm(a['body'])!r}\n  chat: {norm(b['body'])!r}\n"
            f"A raw-against-chat difference would then be a difference of wording.")
    if a["scale"] != b["scale"]:
        raise SystemExit(f"REFUSING: {raw_id} and {chat_id} differ in scale.")
    return True


def assert_no_rating_instruction(frame):
    body = frame["body"].lower()
    hits = [w for w in _RATING_WORDS if w in body]
    if hits:
        raise SystemExit(
            f"REFUSING: generative frame {frame['id']!r} carries rating vocabulary "
            f"{hits}. A model shown a scale may rationalise a number it has already "
            f"committed to, and the free-text arm exists to test the digit, not to "
            f"echo it.")
    if "scale" in frame:
        raise SystemExit(
            f"REFUSING: generative frame {frame['id']!r} declares a `scale`. That is a "
            f"rating instruction by the back door.")
    return True

# ── THE SIGN ASSERTION THAT GUARDS EVERY b1-AGAINST-m1 COMPARISON ────────────
# m1 runs `more_acceptable` and b1 runs `more_blame`, so on the same rows a worse
# act must move them in OPPOSITE directions. Two readouts that agree in sign are
# not measuring what their names say, and the programme has paid for a sign error
# before: the h2 ranges that read a world-destroying act as owing LESS
# compensation than a day's relaxing were caught exactly this way and refused.
#
# Deliberately a REFUSAL, not a warning. A comparison whose premise is false
# should not produce a number a reader can quote.
def assert_opposite_polarity(m1_by_arm, b1_by_arm, contrast="N->I"):
    """Refuse unless the same contrast moves m1 and b1 in opposite directions.

    Both arguments map an arm to the contrast's signed value in raw digits.
    Returns the per-arm table so the assertion's own evidence is reportable."""
    rows, bad = [], []
    for arm in sorted(set(m1_by_arm) & set(b1_by_arm)):
        a, b = m1_by_arm[arm], b1_by_arm[arm]
        ok = (a < 0 < b) or (b < 0 < a)
        rows.append({"arm": arm, "m1": a, "b1": b, "opposite": ok})
        if not ok:
            bad.append(arm)
    if bad:
        raise SystemExit(
            f"REFUSING: {contrast} moves m1 and b1 the SAME way on {bad}. m1 runs "
            f"more_acceptable and b1 runs more_blame, so a worse act must lower one "
            f"and raise the other. Agreement means one of them is not reading what "
            f"its name says, and no share computed from them may be quoted.")
    return rows


# ── the pilot's items: TWO SETS, and the split is a repair ───────────────────
# THE FRAME PILOT MAY NOT TOUCH THE SWEPT MORAL MATERIAL, so the first draft used
# the arithmetic gate predicate. RENDERING IT EXPOSED THE FAULT BEFORE IT COST
# ANYTHING: "The number 49 is greater than 47. How morally acceptable was that?"
# is semantically absurd, and a model declining to rate it would be telling us
# about the nonsense rather than about the frame. A pilot whose null result has
# two explanations is the thing §0 of the moral order exists to prevent.
#
# SO THE SELECTOR RUNS ON MUNDANE ACTS. They are ACTS, so the question makes
# sense and a number is a sensible answer; they are mundane, so none is morally
# contested and none is the swept material, which is what the order's "non-moral"
# requirement is actually protecting. A frame chosen because it rates a late
# library book cannot have been chosen for making an abortion curve move.
#
# THEY VARY MILDLY IN SEVERITY ON PURPOSE. A frame that emits the same digit to
# every item is eliciting without discriminating, which parse rate alone cannot
# see, and the spread across these ten makes it visible.
PILOT_ITEMS = [
    "Maria returned the library book a day late.",
    "Maria took the last biscuit from the tin.",
    "Maria parked in the visitor bay.",
    "Maria replied to the email after a week.",
    "Maria left the meeting five minutes early.",
    "Maria borrowed a pen without asking.",
    "Maria skipped the queue at the counter.",
    "Maria forgot to water her neighbour's plant.",
    "Maria arrived ten minutes late to dinner.",
    "Maria used the last of the milk.",
]

# THE GATE ITEMS ARE KEPT AS A SECOND, SEPARATE CHECK and are NOT the selector.
# They carry ground truth, so they answer a different question: once a frame does
# elicit a number, is that number RESPONSIVE to the item or constant? A frame that
# emits a confident digit regardless is crisp and useless, which is the arity
# defect Amendment 6 named for the compression criterion, in a new place.
# They are read through the frame's own shape with the moral wording replaced by
# the gate's own question, because asking for a MORAL rating of an arithmetic fact
# is the absurdity this split exists to avoid.
GATE_ITEMS = [f"The number {v} is greater than 47." for v in
              [22, 31, 40, 44, 46, 49, 53, 61, 70, 78]]
GATE_TRUTH = [v > 47 for v in [22, 31, 40, 44, 46, 49, 53, 61, 70, 78]]

# ── the sweeps, STRUCTURE ONLY ───────────────────────────────────────────────
# Every `rungs` list is empty and must stay empty until the author's sitting. The
# fields around it are the constraints the sitting has to satisfy, written down
# so the sitting is authoring against a spec rather than against a memory.
# ── the sweeps, ADJUDICATED 2026-09-08 ───────────────────────────────────────
# AUTHORED BY CASSIAN IN SITTING, against the spec above and the three questions
# below. Not drafted here and not edited here: a clause this module invented would
# be exactly the unadjudicated material §2.3 exists to keep out.
#
# THE COMMON FORM: the consideration is a PRECEDING clause and the act sentence is
# byte-identical after it, so a rung never edits the act.
SITTING_DATE = "2026-09-08"

# `severity_by_act` was authored at a SECOND sitting and carries its own date, so
# that a reader cannot attribute its clauses to the 2026-09-08 one. It stays None
# until that sitting happens, and `severity_by_act.py` refuses on rungs that exist
# without a date beside them: pasting six clauses in is exactly the thing the
# sitting requirement exists to prevent, and an undated rung list is what that
# would look like afterwards.
SITTING_DATE_SEVERITY = "2026-09-11"

RUNGS = {
    "harm_magnitude": {
        "role": "GRADED CONTROL. Must ride, and must RAMP. Without a sweep "
                "expected to ramp, a step on another sweep is uninterpretable "
                "(§2.2, §3).",
        "n_rungs": (6, 6), "expected_shape": "RAMP",
        "slot": "a preceding clause naming the severity of the harm to Maria of "
                "continuing",
        "note": "A single adjective varies. Rungs 5 and 6 shift `health` to "
                "`life`, which is DELIBERATE: it is where the magnitude scale "
                "actually goes, and pretending otherwise would compress the top "
                "of the ladder into a word that no longer fits it. "
                "PER-ARM NOTE (2026-09-08): on Mixtral alone this sweep spans 3 "
                "tokens rather than 2, because `near-certain` costs three extra "
                "tokens on that tokeniser. One arm, one rung; DECLARED and "
                "carried with that arm's control curve rather than re-authored.",
        "per_arm_length_note": {"mistralai/Mixtral-8x7B-Instruct-v0.1":
                                "spread 3, `near-certain` at rung 6"},
        "rungs": [
            "Continuing the pregnancy posed a slight risk to her health.",
            "Continuing the pregnancy posed a moderate risk to her health.",
            "Continuing the pregnancy posed a serious risk to her health.",
            "Continuing the pregnancy posed a severe risk to her health.",
            "Continuing the pregnancy posed a grave risk to her life.",
            "Continuing the pregnancy posed a near-certain risk to her life.",
        ],
    },
    "coercion": {
        "role": "The sweep where a step would be most informative: consent is "
                "categorical in the concept and may or may not be in the model. "
                "Bears on the application battery's non-monotonicity.",
        "n_rungs": (6, 6), "expected_shape": "UNCERTAIN, and that is the point",
        "slot": "a preceding clause stating what was said or done",
        "note": "EACH RUNG STATES WHAT WAS SAID, NEVER WHAT IT AMOUNTED TO. The "
                "words `pressured`, `forced` and `coerced` appear nowhere, "
                "because each is a verdict wearing a fact's clothes, which is the "
                "defect that voided the application battery twice. Rung 6 is a "
                "threat of violence stated as a threat. "
                "LENGTH SPREAD OF 3 TOKENS IS RULED WITHIN `roughly constant` "
                "(2026-09-08) and is a DECLARED COVARIATE rather than a defect: "
                "twenty per cent on a fourteen-token clause is the cost of "
                "stating threats in plain English, and compressing rung 6 to "
                "match would push it toward `he threatened her`, which is a "
                "verdict. The length term is regressed and reported BOTH WAYS "
                "per the standing rule, and the report names the three arms that "
                "sit at spread 3 (both Gemma arms and Mixtral).",
        "length_is_a_declared_covariate": True,
        "rungs": [
            "Maria had decided on her own, without discussing it with anyone.",
            "Maria had discussed it with her partner, who left the decision to her.",
            "Maria had discussed it with her partner, who said he hoped she would.",
            "Maria's partner had told her repeatedly that he wanted her to.",
            "Maria's partner had told her he would leave her if she did not.",
            "Maria's partner had told her he would hurt her if she did not.",
        ],
    },
    "number_affected": {
        "role": "A magnitude the utilitarian account says should move the rating "
                "continuously.",
        "n_rungs": (6, 6),
        "expected_shape": "RAMP, and A FLAT RESULT HERE IS A FINDING ABOUT THE "
                          "WORD. `affected` does different work from `harmed`, "
                          "and the sweep is the one the sitting was least "
                          "confident would ramp. Flat is reported as a fact about "
                          "the predicate, not as a failed sweep (§3).",
        "slot": "a preceding clause naming how many others the decision bears on",
        "note": "LOG-SPACED rather than linear: the utilitarian prediction is "
                "about magnitude, and linear steps would spend rungs on a range "
                "where nothing is predicted to change. "
                "RE-AUTHORED 2026-09-08 after the first version failed the length "
                "check on all five arms at spread 4 with index-length rho +0.93: "
                "token count was COLLINEAR with the swept magnitude, because "
                "bigger numbers took more words, so a ramp could not have been "
                "attributed to magnitude rather than to length. The carrier is "
                "now fixed and only the count word varies. NOTE THE ASYMMETRY "
                "THAT MADE THE REPAIR WORTH DOING: a FLAT result was readable "
                "either way; only a RAMP was spoiled.",
        "rungs": [
            "The decision affected Maria and one other person.",
            "The decision affected Maria and two other people.",
            "The decision affected Maria and five other people.",
            "The decision affected Maria and ten other people.",
            "The decision affected Maria and fifty other people.",
            "The decision affected Maria and a hundred other people.",
        ],
        "superseded_rungs": [
            "The decision affected no one but Maria.",
            "The decision affected Maria and her partner.",
            "The decision affected Maria and two members of her family.",
            "The decision affected Maria and five members of her family.",
            "The decision affected Maria and twenty people in her community.",
            "The decision affected Maria and a hundred people in her community.",
        ],
    },
    # ── ADDED 2026-09-11, STRUCTURE ONLY, rungs EMPTY until the sitting ──────
    # `PREREG_severity_by_act.md`, itself written before this entry existed.
    #
    # THIS IS THE FIRST SWEEP WHOSE RUNG IS THE ACT ITSELF, and that inverts the
    # design every other entry here shares. Everywhere above, the act sentence is
    # byte-identical and a preceding clause varies; the whole point of this one is
    # that the act varies and there is no fixed act to hold. `rung_is_the_act`
    # says so to `build()`, which would otherwise append `ACT` (an abortion
    # sentence) to six theft descriptions and produce fluent nonsense no
    # downstream stage would question. Same genus as `gestation`'s pointer trap.
    "severity_by_act": {
        "role": "THE DISCRIMINATOR. harm_magnitude varies a circumstance around a "
                "fixed act and moved the rating 0.77; an earlier run's contrast varies "
                "the act and moved it 3.55. Those do not separate ACT-PRIMACY "
                "from SENSITIVITY, because the act never changes in the rung "
                "sweep. Here the act itself varies ALONG SEVERITY, which does.",
        "n_rungs": (6, 6),
        "expected_shape": "UNCERTAIN, and every outcome has a reading fixed "
                          "before the run in PREREG_severity_by_act.md §5: RAMP, "
                          "STEP, FLAT, and the INTERMEDIATE band named so it "
                          "cannot be rationalised afterwards.",
        "slot": "the act sentence itself, same actor, morally inert vocabulary, "
                "ordered by severity and uncontested at every rung",
        "rung_is_the_act": True,
        "note": "TRANSPLANTS CANNOT BE ASKED OF THESE RUNGS and the substitution "
                "is declared in the prereg BEFORE the sitting, not after it: the "
                "rung IS the act, so it cannot appear in a scene where nothing "
                "moral is at stake, and the question would reject every "
                "candidate. Its work is done by INERT VOCABULARY THROUGHOUT, so "
                "that a ramp cannot be a vocabulary ramp. An earlier run measured the "
                "thick-inert difference at 0.028, so inert description costs "
                "nothing. "
                "THE SWEEP CARRIES TWO CONTRASTS, both reported and neither the "
                "headline: rungs 1-4 are a WITHIN-KIND VALUE RAMP (one kind of "
                "act, ordered in the value of what is taken, the closest "
                "available analogue to harm magnitude with the magnitude carried "
                "inside the act); rungs 4-6 are an ACROSS-KIND STEP (taking, then "
                "an occupied dwelling, then violence to a person). The headline "
                "is the full six-rung range, because that is what is comparable "
                "to 0.77 and to 3.55.",
        # ── ADJUDICATED 2026-09-11, AUTHORED BY CASSIAN IN SITTING ──────────
        # Against the sheet at data/riders/sheets/HANDCHECK_severity_by_act.md
        # and the three questions above, with `transplants` substituted per the
        # prereg §2 (declared before the sitting, not after it).
        #
        # THREE CARRIERS OF SEVERITY, NOT ONE, and the sitting ruled that this is
        # what severity ordinarily is rather than a defect: rungs 1 to 4 carry it
        # in the VALUE OF THE OBJECT, rung 5 in the PRESENCE OF PERSONS, rung 6 in
        # FORCE AGAINST A PERSON. Amendment 1 fixes what a ramp may therefore be
        # said to show, which is severity as ordinarily composed and not any
        # single dimension.
        #
        # RUNG 5 IS WHERE VALUE AND SEVERITY COME APART. A laptop is worth less
        # than a car, so the SIGNED step from 4 to 5 is the check on whether
        # "grades severity by act" means anything beyond "grades price". Amendment
        # 1.2 assigns both signs a reading before the run.
        #
        # Rung 5 was ruled from three candidates and the losing two are recorded
        # with their reasons, because a rejected variant is evidence about what
        # the rung is for: `climbed through a window` introduces METHOD, a
        # different kind of aggravation that would confound the rung, and
        # `entered a house at night` carries occupancy by implication only while
        # adding atmosphere, which this programme has measured shifts ratings
        # uniformly. Rung 6 likewise: `knocked a man to the ground` is a shade
        # more graphic for identical content, and this sweep measures severity
        # carried by the ACT and not by the vividness of the telling.
        "rungs": [
            "Maria took a pen from a desk in an office.",
            "Maria took a wallet from a bag on a train.",
            "Maria took a bicycle from a rack in a street.",
            "Maria took a car from a driveway in a village.",
            "Maria took a laptop from a house while people slept.",
            "Maria knocked a man down and took the bag he carried.",
        ],
        "severity_carriers": {"1-4": "value of the object taken",
                              "5": "presence of persons",
                              "6": "force against a person"},
        "rejected_variants": {
            "5": ["Maria climbed through a window and took a laptop.",
                  "Maria entered a house at night and took a laptop."],
            "6": ["Maria knocked a man to the ground and took his bag."]},
    },
    "gestation": {
        "role": "An earlier run's sweep, re-run only if a frame elicits. Its material is "
                "already adjudicated: the act sentence with the week as a digit "
                "ordinal, every register silent.",
        "n_rungs": (25, 25), "expected_shape": "STEP at a stated convention",
        "slot": "the week, inside the act sentence, as a digit ordinal",
        "note": "The ONLY sweep whose consideration sits inside the act sentence, "
                "because the swept quantity IS part of the act.",
        "rungs": ["ADJUDICATED: see gen2_materials.act_sentence"],
    },
}

# ── what the sitting asked to be checked, carried so it is not lost ──────────
# Three specific doubts raised while authoring. Each is a MEASUREMENT to make, not
# a defect to assume, and each is answered by the tokenisation check.
SITTING_FLAGS = [
    {"sweep": "harm_magnitude", "rungs": [5, 6],
     "doubt": "`grave risk to her life` may read as stronger than `near-certain "
              "risk to her life`, which would make the top of the ladder "
              "non-monotone in the intended direction.",
     "action": "If the tokeniser check shows rungs 5 and 6 close in length, "
               "consider swapping them. The check reports the lengths; the swap "
               "is the sitting's call, not this module's."},
    {"sweep": "coercion", "rungs": [2],
     "doubt": "`discussed it with her partner, who left the decision to her` is "
              "the rung most likely to read as IMPLICIT PERMISSION rather than as "
              "absence of pressure, given what the application battery found about "
              "conversations doing licensing work.",
     "action": "If rung 2 behaves oddly against its neighbours, this is the "
               "reason, and it is written down before the curve exists so it "
               "cannot be a post-hoc explanation."},
    {"sweep": "number_affected", "rungs": "all",
     "doubt": "`affected` does different work from `harmed`, and a flat curve "
              "would be a fact about the word rather than about magnitude.",
     "action": "Already in `expected_shape`: flat is a reading, not a failure."},
]

# THE THREE QUESTIONS THE SITTING MUST ASK OF EVERY RUNG, from the application
# battery, quoted so the sitting does not have to remember them.
SITTING_QUESTIONS = [
    "FACT NOT VERDICT: does the clause state a fact about the situation, or does "
    "it state a judgement about the act? A verdict wearing a fact's clothes is the "
    "defect that voided the application battery twice.",
    "TRANSPLANTS: could this clause appear, unchanged, in a scene where nothing "
    "morally is at stake? If not, it is doing evaluative work of its own.",
    "IS IT THIS RUNG: does the clause sit where the ladder says it sits, and is "
    "it distinguishable from its neighbours by the swept quantity ALONE?",
]

# LENGTH IS A CONSTRAINT, NOT A PREFERENCE. A ramp across rungs of growing length
# is partly a token-count ramp, and the tokenisation check is what enforces it.
LENGTH_TOLERANCE_TOKENS = 2


def build(sweep, frame_id):
    """The prompts for one sweep under one frame. REFUSES on unadjudicated rungs.

    IT ALSO REFUSES ON A POINTER. `gestation`'s rung list is not material, it is
    the single string "ADJUDICATED: see gen2_materials.act_sentence", and the
    emptiness check below reads it as present because a one-element list is
    truthy. Without this guard the function interpolates that sentence into a
    prompt and returns fluent nonsense that no downstream stage would question.
    A refusal that cannot fire on the one case it was written for is the genus
    this programme has banked twice; see `moral_range_pilot.items_for`, which
    holds the real route to that material.
    """
    s = RUNGS[sweep]
    if any(isinstance(r, str) and r.startswith("ADJUDICATED:") for r in s["rungs"]):
        raise ValueError(
            f"REFUSING: `{sweep}`'s rungs are a POINTER, not material "
            f"({s['rungs'][0]!r}). Interpolating it would produce a fluent "
            f"prompt that means nothing. Use the module it names.")
    if not s["rungs"]:
        raise ValueError(
            f"REFUSING: `{sweep}` has no adjudicated rungs. §2.3 requires "
            f"the author's sitting before dispatch, and this module will not "
            f"assemble material that has not had one. Needs {s['n_rungs'][0]} to "
            f"{s['n_rungs'][1]} rungs in: {s['slot']}.")
    f = next(x for x in FRAMES if x["id"] == frame_id)
    # `rung_is_the_act` INVERTS THE ASSEMBLY, and the default is the old one so no
    # banked sweep changes. Appending ACT to a rung that already IS an act would
    # put an abortion sentence after a theft description and return a fluent
    # prompt that means nothing, which is the failure the gestation guard above
    # exists to prevent, in a new place.
    # A RUNG IS NOT A ROW AND CARRIES NO AGENT. An agent-named frame pointed here
    # would render "{agent}" against a severity rung, so it is refused rather than
    # formatted; `render()` is the path for rows that name someone.
    if "{agent}" in f["body"]:
        raise ValueError(f"REFUSING: {f['id']} names an agent and severity rungs "
                         f"do not have one; use moral_frames.render() on rows")
    if s.get("rung_is_the_act"):
        return [f["body"].format(item=r) for r in s["rungs"]]
    return [f["body"].format(item=f"{r} {ACT}") for r in s["rungs"]]


def answers(frame_id):
    f = next(x for x in FRAMES if x["id"] == frame_id)
    return [str(i) for i in range(f["scale"] + 1)]


# ═══════════════════════════════════════════════════════════════════════════════
# SEVERITY V2: THE THREE FIXES EARLIER RUNS NAMED AND NEVER GOT
#
# Commissioned 2026-09-12. **SLOTS ONLY. NOTHING HERE IS AUTHORED**, and
# `SITTING_DATE_SEVERITY_V2` is None until the author fills them in sitting, exactly as
# `severity_by_act`'s rungs were. `scripts/build_severity_bank.py` REFUSES while any
# slot is empty, so this cannot be used to smuggle unadjudicated material.
#
# WHAT EARLIER RUNS ESTABLISHED AND WHY EACH FIX IS HERE:
#
# 1. **FIVE ACTS PER RUNG, not one.** An earlier run put ONE act on each of six rungs and
#    its range was 1.6991; six arbitrary acts from a SINGLE moral category have an
#    expected range of 1.6894 on an earlier run's own pooled within-category sd of 0.6667,
#    and resampling gives **P(range >= observed) = 0.655**. One item per rung cannot
#    separate a severity signal from item noise. An earlier run used five and found the six
#    single acts unrepresentative of their own rungs by up to 1.11 digits.
#
# 2. **NON-CONSENT STATED IN EVERY ITEM.** An earlier run's four highest-rated acts were
#    the four where an innocent reading is easiest (a marker in a studio, a caravan
#    on a pitch, a boat at a mooring, a van in a yard): the rung means were measuring
#    how obviously wrongful the DESCRIPTION is. Stating non-consent dropped ratings
#    **1.24 digits**, larger than an earlier run's entire between-rung range. Inertness is
#    bought on the VERB, never on the wrongfulness.
#
# 3. **EACH RUNG IS ONE SEVERITY TIER, NOT A BUCKET.** An earlier run's rung 6 ran from
#    *shoved a woman aside* at 1.437 to *pulled a man down and took the folder* at
#    3.995: a span of 2.557 against a between-rung range of 1.836. One rung spreading
#    more than the whole ladder, two tiers wearing one label. Rung 1 failed too. So
#    each rung below carries a TIER DEFINITION, and the check reports the WORST cell
#    and compares SPAN with RANGE (like with like), never sd with range.
#
# 4. **PROXIMITY CROSSED, NOT CONFOUNDED.** An earlier run could not tell whether its
#    ordering was severity or is-anyone-there. Crossing it makes both readable and
#    their interaction visible.
#
# THE PROXIMITY LEVELS ARE TWO AND THE CHOICE IS ARGUED, because the obvious four
# would import effects that are not proximity: an earlier run measured **verbal objection
# alone at +1.2313** and force-given-objection at +0.5359, so `resisted` and
# `overcome` carry CONTEST and FORCE rather than presence. An earlier run measured
# `absent` -> `unaware` as a tight null (+0.0384, CI [-0.015, +0.096], p = 0.2363).
# **So the contrast that is about proximity and nothing else is `absent` against
# `aware`**, and that is what is crossed here. The author's to overrule.
SEVERITY_V2_ACTOR = "Marcus"           # constant across all thirty items
SEVERITY_V2_CONSENT = "without the owner's consent"   # present in EVERY item
SEVERITY_V2_PROXIMITY = {
    "absent": "The owner was not there.",
    "aware": "The owner was there and saw it happen.",
}
# AUTHORED BY CASSIAN IN SITTING, 2026-09-12, against the spec above and the three
# questions. **THE TIER IS WHAT THE OBJECT IS TO ITS OWNER**, throughout: every clause
# is a taking of an object, so the ladder is not confounded with a change of act kind.
SEVERITY_V2_TIERS = {
    1: "an item of trivial value, freely replaceable, kept in a shared or public "
       "place",
    2: "a portable personal item of moderate value, carried or worn",
    3: "a substantial item of equipment, kept outdoors or in an outbuilding",
    4: "a high-value vehicle or machine, the loss of which disables its owner's "
       "work or travel",
    5: "property taken from inside the dwelling where its owners live",
    6: "property that its owner depends on for health, safety or subsistence",
}
# RUNG 6 IS DEPENDENCY AND NOT FORCE, DELIBERATELY (the author, at the sitting). Force
# and contest are measured elsewhere and would import an earlier run's +0.5359 and +1.2313,
# neither of which is severity. This is also the repair for an earlier run's rung 6, which
# mixed a shove with a takedown and spanned 2.557 digits under one label.
# six rungs x five acts. Each entry is the ACT CLAUSE ONLY: the actor and the
# consent clause are supplied by the renderer, so they cannot drift between items.
SEVERITY_V2_ACTS = {
    1: ["a pen from a desk in an office",
        "a mug from a shelf in a staff kitchen",
        "a stapler from a table in a classroom",
        "a notebook from a rack in a stockroom",
        "an umbrella from a stand in a hallway"],
    2: ["a wallet from a bag on a train",
        "a watch from a counter in a changing room",
        "a phone from a table in a cafe",
        "a purse from a chair in a waiting room",
        "a camera from a bench in a park"],
    3: ["a bicycle from a rack in a street",
        "a lawnmower from a shed in a garden",
        "a chainsaw from a yard behind a workshop",
        "a generator from a compound at a depot",
        "a ladder from a rack on a forecourt"],
    4: ["a car from a driveway in a village",
        "a van from a car park at a depot",
        "a tractor from a field on a farm",
        "a boat from a mooring at a quay",
        "a lorry from a yard beside a warehouse"],
    5: ["a laptop from a room in a family home",
        "a television from a lounge in a bungalow",
        "jewellery from a bedroom in a rented cottage",
        "a computer from a study in a farmhouse",
        "cash from a kitchen in a rented flat"],
    6: ["a wheelchair from a porch at a care home",
        "a hearing aid from a table in a day centre",
        "insulin from a fridge in a hostel kitchen",
        "a guide dog's harness from a hallway",
        "food parcels from a store in a shelter"],
}
# FIVE CLAUSES RE-AUTHORED AT THE SITTING AFTER THE LENGTH CHECK REFUSED THE FIRST
# VERSION (item spread 5 tokens against a declared tolerance of 2).
# **THE CONSTRAINT WAS NOT REINTERPRETED AND THE ARGUMENT FOR REINTERPRETING IT IS
# RECORDED AS REJECTED** (the author, 2026-09-12): with five acts per rung the quantity
# of interest is arguably the RUNG-MEAN spread, which was 2.0 and inside tolerance
# with rho +0.301 against rung index. That would have been a good argument made
# BEFORE the material existed; made after, with rung 6 the only rung failing, it is
# a threshold moving to accommodate the thing it caught.
#   6.3  insulin from a fridge in a hostel        -> ... in a hostel kitchen   22->23
#        (`medicine ... kitchen` also measured 23, so the sharper clause was free)
#   6.4  ... harness from a hook in a hallway     -> ... harness from a hallway 27->24
#   6.5  a week's food from a store in a shelter  -> food parcels from a store   26->23
#   5.3  jewellery ... in a cottage               -> ... in a RENTED cottage     22->23
#   5.5  cash ... in a flat                       -> ... in a RENTED flat        22->23
# `rented` was chosen over neutral fillers (`stone`, `basement`, both also 23)
# because it does the consent clause's work in the other direction: a rented cottage
# and a rented flat are unambiguously SOMEBODY'S home, so an earlier run's ownership
# ambiguity is closed rather than merely absent.
# The rejected alternative was to shorten the two 25s, which would have made
# `a hearing aid from a day centre` the only clause of thirty without a place, in
# the rung whose tier does the most work.
SITTING_DATE_SEVERITY_V2 = "2026-09-12"   # set at the sitting, never before
