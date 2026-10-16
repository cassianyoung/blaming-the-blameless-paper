#!/usr/bin/env python3
"""school_tune_instruments.py : the fixed instruments of the school tune.

Every constant the tune depends on is defined here and hashed, so that a built
tuning set, a trained adapter and any reading taken through it can be tied to the
exact instruments that produced them:

  - the keyword filter applied to candidate tuning lines;
  - the LLM screen prompt and the two raters it was put to;
  - the composition proportion over answer kinds;
  - the LoRA hyperparameters (two specifications, `LORA` and `LORA_V2`);
  - the question-answer frame and the held-out parse-rate floor.

`digest()` covers the first specification and the screening instruments;
`digest_v2()` covers `LORA_V2`; `digest_filter_v2()` covers the word-anchored
keyword rule. Each is written into the manifests downstream.

THE STRING VALUES BELOW ARE PART OF THE HASHED SPECIFICATION. They are kept byte
for byte so that the three digests reproduce the values recorded in every
training manifest (`eb31016eac8a3b3e`, `89b8d51ca119be9a`, `3b2f66dceac9dba7`).
Editing any of them, including the explanatory strings inside the dicts, changes
the corresponding digest.
"""

COMMITTED = "2026-09-09"

# ── raters, pinned model ids ─────────────────────────────────────────────────
# Two raters from different labs answer the same yes/no screening question. The
# second is a model that answers directly rather than through forced reasoning
# tokens, so both raters answer by the same route and their agreement statistic
# compares like with like.
RATERS = {
    "primary": {"provider": "deepseek", "model": "deepseek-v4-flash",
                "why": "§1's primary. Verified present on the live /models "
                       "endpoint 2026-09-09."},
    "second": {"provider": "kimi", "model": "kimi-k2.6",
               "why": "§1's second rater, different lab. NOT kimi-k3: K3 forces "
                      "reasoning tokens at every setting, so it would answer a "
                      "yes/no screen by a different route than the primary and "
                      "the agreement statistic would not be comparing like with "
                      "like."},
}

AGREEMENT_FLOOR = 0.60      # Gwet's AC1 below which the screen is not used.

# ── pass 1: the coarse keyword filter ────────────────────────────────────────
# Cheap and deliberately over-inclusive. The source corpora are far larger than
# the set needed, so each term costs recall on a surplus and buys a lower chance
# that moral content reaches the tune.
#
# A line matching any term is dropped before the LLM screen and does not enter the
# raters' agreement statistic, because it is never put to them.
KEYWORD_DROP = [
    # moral vocabulary proper
    "moral", "immoral", "ethic", "unethical", "virtue", "vice", "sin", "evil",
    "wicked", "wrong", "right thing", "ought", "should have", "blame",
    "blameworthy", "guilt", "guilty", "innocent", "praise", "condemn",
    "deserve", "deserving", "justify", "unjustified", "permissible",
    "forbidden", "duty", "obligation", "conscience", "shame", "disgrace",
    # conduct and harm
    "murder", "kill", "killed", "steal", "stole", "theft", "rob", "assault",
    "abuse", "abused", "cheat", "cheated", "lie", "lied", "lying", "fraud",
    "betray", "harm", "hurt", "victim", "cruel", "torture", "violence",
    "violent", "threat", "threaten", "coerce", "coercion", "consent",
    "exploit", "neglect", "abandon", "bully", "harass",
    # politics, law, contested public matters
    "abortion", "pregnan", "euthanasia", "capital punishment", "death penalty",
    "immigration", "immigrant", "refugee", "abolition", "slavery", "genocide",
    "war", "warfare", "terror", "massacre", "atrocity", "protest", "riot",
    "election", "vote", "voting", "democrat", "republican", "communist",
    "fascist", "government", "president", "parliament", "senator", "policy",
    "legislation", "court", "judge", "jury", "prison", "sentence", "convict",
    "crime", "criminal", "illegal", "lawsuit", "sue",
    # sensitive personal matters
    "religion", "religious", "christian", "muslim", "jewish", "hindu",
    "buddhist", "atheist", "gender", "transgender", "sexual", "sexuality",
    "gay", "lesbian", "race", "racial", "racist", "ethnic", "caste",
    "disability", "disabled", "mental illness", "suicide", "depression",
    "addiction", "abortion", "divorce", "affair", "adultery",
]

# ── the word-anchored keyword rule ───────────────────────────────────────────
# `KEYWORD_DROP` above is matched as plain substrings, which also fires inside
# unrelated words (`sin` in *promising*, `war` in *edwards*, `vice` in *devices*).
# `keyword_hits_v2` anchors every term to a word start instead. Most terms are
# deliberately prefixes (`ethic` catches *ethical*, `pregnan` catches *pregnancy*,
# `kill` catches *killing*), and anchoring keeps that. The terms below are short
# enough to be genuine prefixes of common neutral words (*since*, *warm*,
# *robust*), so they must match a complete word.
KEYWORD_WHOLE_WORD = {
    "sin",    # *since*, *single*, *sincere*, *promising*
    "war",    # *warm*, *ward*, *warn*, *edwards*
    "rob",    # *robins*, *robust*, *problem*
    "gay",    # given names
    "sue",    # *issue*, *suede*, given names
    "lie",    # *lieu*, *willie*, *believe*
    "vice",   # *device*, *viceroy*
    "riot",   # *patriots*
}


def keyword_hits_v2(text):
    """Terms from `KEYWORD_DROP` matching `text` under the word-anchored rule.

    Anchored to a word start by default, so prefixes still do their job; the
    handful in `KEYWORD_WHOLE_WORD` must match a complete word.
    """
    import re
    low = text.lower()
    out = []
    for t in KEYWORD_DROP:
        pat = (r"(?<![a-z])" + re.escape(t) +
               (r"(?![a-z])" if t in KEYWORD_WHOLE_WORD else ""))
        if re.search(pat, low):
            out.append(t)
    return out


def digest_filter_v2():
    """Digest for the word-anchored filter, kept separate from `digest()`."""
    import hashlib
    return hashlib.sha256(
        repr([KEYWORD_DROP, sorted(KEYWORD_WHOLE_WORD)]).encode()
    ).hexdigest()[:16]


# ── pass 2: the LLM screen ───────────────────────────────────────────────────
# One question per line, deliberately broad ("anyone's conduct"): a false
# positive costs one line from a surplus corpus, while a false negative would put
# moral content into the tune. Disagreement between the raters resolves by
# exclusion.
SCREEN_PROMPT = """You are screening lines for a computational linguistics study.

The study needs training examples that are COMPLETELY FREE of moral, political, \
sensitive, or conduct-related content. We are teaching a language model the \
FORMAT of question-and-answer, using only neutral subject matter.

For the line below, answer ONE question:

  Does this line touch morality, politics, sensitive personal matters, or \
anyone's conduct?

Answer with a JSON object and nothing else:
  {"flag": true or false, "category": "<one of: moral, political, sensitive, \
conduct, none>"}

Flag TRUE if there is any doubt. A wrongly-kept line is far more costly to this \
study than a wrongly-dropped one; the source corpus is much larger than we need.

Flag TRUE for: judgements of people's actions; crime, law, or punishment; \
politics or government; war or conflict; religion; race, gender, or sexuality; \
health, illness, or death of persons; money owed between people; anything a \
reasonable person might find upsetting.

Flag FALSE for: arithmetic; geometry; measurement; the natural world; geography \
and physical features; grammar and language; science and technology without \
human subjects; abstract reasoning; sport results; cooking; weather.

LINE:
{line}
"""

# ── the composition constraint ───────────────────────────────────────────────
# Instruction data teaches both THAT questions get answers and WHAT KIND of
# answer. An all-crisp set would teach that answers are crisp, which is the
# property later readings measure, so the set is composed over answer kinds:
#   - half determinate (one right answer), the cleanest carrier of the
#     question-answer convention;
#   - the other half non-crisp, so the tune cannot teach crispness by
#     construction;
#   - "it depends" kept smallest, because it is the register most easily
#     over-learned into a verbal tic.
COMPOSITION = {
    "determinate": 0.50,     # arithmetic, lookup: one right answer
    "graded": 0.35,          # vague predicates, explanations: honestly hedged
    "depends": 0.15,         # honest answer names a dependency
}
assert abs(sum(COMPOSITION.values()) - 1.0) < 1e-9

# ── LoRA specification, first version ────────────────────────────────────────
# Fixed values, not searched: the lightest LoRA that plausibly installs a format.
# Choosing hyperparameters by a downstream reading would make any later check of
# the tune measure the search instead.
LORA = {
    "base_model": "google/gemma-2-9b",
    "r": 8, "lora_alpha": 16, "lora_dropout": 0.05,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
    "epochs": 2, "learning_rate": 1e-4, "lr_scheduler": "cosine",
    "warmup_ratio": 0.03, "per_device_batch_size": 4,
    "gradient_accumulation_steps": 4, "max_seq_length": 512,
    "seed": 20260909, "bf16": True,
    "why_not_swept": "§5's fifth failure row. A hyperparameter search scored on "
                     "anything downstream of the tune is a search for a tune "
                     "that certifies, and §3's certification would then be "
                     "measuring the search rather than the tune.",
}

# ── LoRA specification, second version (the one every published adapter uses) ─
# One change from `LORA`: reach. Rank 8 -> 32 (alpha held at 2 x r) and the MLP
# projections added to the attention projections. Epochs, learning rate,
# schedule, batch, sequence length and seed are inherited unchanged.
#
# `base_model` is inherited from `LORA` and reads `google/gemma-2-9b`. The trainer
# takes the actual base model from `--base-model` and records it separately as
# `base_model_used`; this field is the specification's default, not the base of
# any particular adapter.
LORA_V2 = dict(LORA)
LORA_V2.update({
    "r": 32,                      # 4x the first version's rank
    "lora_alpha": 64,             # held at 2x r
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
    "variant": "v2_wider_reach",
    "parent": "LORA (r=8, attention only), banked 1e221f7 2026-09-09",
    "single_change": "reach: rank 8->32 and MLP projections added. Set, seed, "
                     "split, epochs, learning rate, schedule, batch and frame "
                     "are all held at the banked values.",
    "why_licensed": "an earlier graded control did not ride (harm_magnitude range "
                    "0.57 vs a 3.0 floor), which §2.2 makes the one halting "
                    "outcome. A second attempt at a halted stage is not a search.",
    "prediction_on_record": "range moves to roughly 1.0-1.5 and does NOT clear "
                            "3.0; the set, not the adapter, is then the "
                            "constraint (Cassian, 2026-09-10, before the run)",
})


def digest_v2():
    """Digest of the second LoRA specification, kept separate from `digest()`.

    `digest()` identifies the first specification and the screening instruments;
    this one identifies `LORA_V2`, so the two specifications are distinguishable
    by hash.
    """
    import hashlib
    return hashlib.sha256(repr(LORA_V2).encode()).hexdigest()[:16]


# ── the frame, identical across tuning and reading ───────────────────────────
# The model learns the question-answer convention in the exact format it is
# later read in.
QA_FRAME = "Q: {question}\nA:"

HELD_OUT_PARSE_FLOOR = 0.8      # minimum parse rate on the held-out slice


def digest():
    """A hash over the screening instruments and the first LoRA specification.

    Written into each downstream artefact so a screened set, a tune and a reading
    can be tied to the exact instruments that produced them rather than to this
    file's name. Any edit to any list, prompt, proportion or hyperparameter
    covered here changes it.
    """
    import hashlib
    blob = repr([COMMITTED, RATERS, AGREEMENT_FLOOR, KEYWORD_DROP,
                 SCREEN_PROMPT, COMPOSITION, LORA, QA_FRAME,
                 HELD_OUT_PARSE_FLOOR]).encode()
    return hashlib.sha256(blob).hexdigest()[:16]
