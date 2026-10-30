# Fixed-three-site infinite counterexample family

For each integer n >= 4, choose uniformly exactly three nonendpoint vertices
of the (n+1) by (n+1) grid and give them weight one. All maximizing ties count.
The legal boundary unwind

`R U^2 R U^(n-2) R^(n-2)` -> `U^2 R^2 U^(n-2) R^(n-2)`

changes the optimal-configuration count by `-(5*n^2 - 27*n + 32)/2 < 0`.
The probability difference divides this by `binom((n+1)^2-2, 3)`.

[Paper PDF](manuscript/build/main.pdf) · [LaTeX](manuscript/main.tex) ·
[中文摘要](证明结果与中文摘要.txt) · [Second derivation](poset_second_derivation.txt)

This is an analytic result for a dependent, fixed-cardinality ensemble.
**It is not a counterexample to the independent Bernoulli(p) conjecture.**
The n=4 instance appeared in the earlier finite companion; this follow-up
extends the displayed family to every n >= 4. Priority and independent
research significance remain unestablished after the bounded literature review.

## Reproduction

Use Python 3, without `-O`. From this directory run:

```sh
python verify_sparse_dp.py
python audit_geometry.py
python check_poset_identity.py
python all_edges.py
python check_n5.py
```

Only the Python standard library is required. `all_edges.py` and `check_n5.py`
use `../src/independent_moves.py` and `../src/moves.py` from the same repository.
The first program fully replays the three-site layer for n=4,...,11; geometry
checks cover n=4,...,30. The n=5 checks compare all 252 paths and 560 move
witnesses over 5,984 three-site configurations. These are exact finite checks,
not full n=5 enumeration and not a substitute for the all-n analytic proof.

The original verification outputs are supplied; timing fields change on rerun.
`scan.py` / `results.json` record an earlier, different extension of the path
and are exploratory evidence, not the displayed theorem family.

## Review status

Unsigned, AI-assisted research draft. Independent computational implementations
agree, but no human peer review or completed proof-assistant verification is
claimed. The second analytic derivation was organized by the same AI.
Lean verification is a separate ongoing task. No journal or arXiv submission
has been made. No reuse license has been selected.

This public edition only updates publication wording relative to the local
30 October 2026 manuscript; the mathematics and verification code are unchanged.
See `SHA256SUMS.txt` for hashes of this edition before rerunning computations.
