# Medical AI Demo Rules

RULE 1: NEVER define data classes inside agent files.
  Always import from models/schemas.py.
RULE 2: NEVER mutate CaseState in place.
  Always use state.model_copy(update={...}).
RULE 3: NEVER call Claude API before Day 5.
  Use stub rationale strings until then.
RULE 4: NEVER use time.time() in simulator.
  All times are synthetic floats (elapsed_min). Seed np.random(42).
RULE 5: ALWAYS run pytest after changes to pk/ or agents/.
RULE 6: NEVER put ANTHROPIC_API_KEY in docker-compose.yml.
  Use env_file: .env only.
RULE 7: When unsure about clinical values, add comment:
  # CLINICAL_REVIEW: verify with domain expert

RULE 8: Never give sugammadex a ceiling effect.
  It should always reach full reversal (1.0).
RULE 9: Never make sugammadex time-to-reversal depth-dependent in the MVP.
  Always evaluate to a constant fixed time to 0.9.

These rules exist because this is a medical AI demo.
Clinical correctness > development speed.
