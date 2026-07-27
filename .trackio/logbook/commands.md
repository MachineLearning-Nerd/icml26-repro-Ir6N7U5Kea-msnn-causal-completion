# Captured runs (clean relative commands; run from paper dir with .venv active)
source .venv/bin/activate
trackio logbook run --page "Tables 1-3 + theorems" -- python repro/src/verify.py
trackio logbook run --page "Negative controls" -- python repro/tests/test_controls.py
