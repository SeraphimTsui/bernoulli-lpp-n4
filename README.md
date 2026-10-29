# Bernoulli last passage percolation for n = 4

An unsigned, AI-assisted research manuscript and complete integer certificates
for a finite specialization of the McKeown–Nakajima bump/unwind conjecture.

**Result:** all 120 genuine nonidentity moves on the 5 × 5 vertex grid strictly
increase geodesic-membership probability for every 0 < p < 1, including all ties.
The 188 strict transitive comparisons follow. Equality holds at p = 0 and 1.
Two independent full enumerations agree on all 8,388,608 environments.

[Read the paper PDF](manuscript/build/main.pdf) · [LaTeX source](manuscript/main.tex) ·
[中文摘要](中文摘要.txt) · [Publication-stage novelty review](literature/novelty_check_20261029.txt)

## Scope and priority

This is a modest finite computer-assisted verification, not a proof for general n.
118 edges have nonnegative degree-23 raw coefficients; all 120 have nonnegative
degree-24 coefficients after one elevation. A stronger fixed-cardinality claim
fails: one legal unwind has conditional difference −2/1771 when exactly three
free vertices are occupied.

The model, move definitions and motivating conjecture come from
[McKeown and Nakajima, arXiv:2608.11378v2](https://arxiv.org/html/2608.11378v2).
Their Theorem 3 proves a small-p comparison. A bounded review on 29 October2026
did not locate this same finite certificate; **priority and standalone research
significance remain unestablished**. Citation-index coverage was incomplete.
Enumeration, dynamic programming and degree elevation are standard methods.

## Reproduce

Install Node.js and Python3. Only their standard libraries are used.
From this directory run:

```sh
python reproduce.py
```

This fully recomputes both tables and checks all moves and signs for n=1..4.
To check saved certificates without enumerating configurations again:

```sh
python src/certify.py
```

Run without Python's `-O` flag because assertions are executable checks.
Counters are exact integers. The original two n4 runs used5.890 CPU seconds
combined; runtime depends on hardware. No n5 computation is included.
Timing receipts change on rerun; mathematical arrays must agree exactly.

Compile the manuscript with TeX Live:

```sh
cd manuscript
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
```

## Files and review

- `results/counts_n4.csv`: all70 probability coefficient rows.
- `results/certificates_n4.json`: all edge differences, elevated coefficients and closure.
- `review/`: independent AI implementation, definition and manuscript reviews.
- `literature/`: source/version records and bounded novelty search logs.
- `SHA256SUMS.txt`: integrity of this public package before rerunning computations.

Historical reviews refer to the initial local draft. The public edition changes
publication wording and reproduction instructions; the mathematical theorem and
certificate arrays are unchanged. The work was generated and checked with AI
assistance. It has **not** received human peer review or proof-assistant verification.
No person or institution is claimed as manuscript author.

No journal or arXiv submission is represented by this GitHub deposit.
No reuse license has been selected; public visibility alone is not a license grant.
