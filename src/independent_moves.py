"""Independent word/corner implementation of genuine McKeown--Nakajima moves.

Only standard Python is needed. No signed-run replacement formula is used.
Run from any directory; output is review/independent_moves.json.
"""
from itertools import combinations
from math import comb
from pathlib import Path
import json


def words(n):
    for ups in combinations(range(2 * n), n):
        ups = set(ups)
        yield ''.join('U' if i in ups else 'R' for i in range(2 * n))


def vertices(w):
    x = y = 0
    ans = [(x, y)]
    for c in w:
        x += c == 'R'
        y += c == 'U'
        ans.append((x, y))
    return ans


def corners(w):
    return [0] + [t for t in range(1, len(w)) if w[t-1] != w[t]] + [len(w)]


def mixed_two_dot_count(w):
    """Direct count of incomparable off-path sites per on-path vertex.

    This verifies Lemma 9 independently of the area-integral proof.
    Comparable sites on the same directed path cannot be incomparable.
    """
    n = w.count('U')
    p = vertices(w)
    on = set(p)
    return sum(1 for x, y in p for u in range(n+1) for v in range(n+1)
               if (u,v) not in on and ((u < x and v > y) or (u > x and v < y)))


def moves(w):
    p = vertices(w)
    ts = corners(w)
    heights = [p[t][1] - p[t][0] for t in ts]
    r = len(ts) - 1

    # Each concavity is indexed by its middle corner.  Reverse its two
    # adjacent constant-letter blocks, requiring the outer runs on both sides.
    for c in range(2, r-1):
        t = ts[c]
        above = w[t-1:t+1] == 'RU' and heights[c] >= 0
        below = w[t-1:t+1] == 'UR' and heights[c] <= 0
        if above or below:
            lo, hi = ts[c-1], ts[c+1]
            v = w[:lo] + w[lo:hi][::-1] + w[hi:]
            yield {'source':w, 'target':v, 'kind':'bump', 'k':c,
                   'side':'above' if above else 'below',
                   'start_step':lo, 'end_step':hi}

    # The origin may serve as the left endpoint, but the final vertex cannot
    # serve as the right endpoint because its diagonal height is zero.
    for left in range(r-1):
        for right in range(left+2, r):
            for side in (1, -1):
                left_ok = left == 0 or side*heights[left] > 0
                right_ok = side*heights[right] > 0
                crossing = all(side*heights[j] < 0 for j in range(left+1, right))
                if left_ok and right_ok and crossing:
                    lo, hi = ts[left], ts[right]
                    v = w[:lo] + w[lo:hi][::-1] + w[hi:]
                    yield {'source':w, 'target':v, 'kind':'unwind',
                           'l':left, 'k':right,
                           'side':'above' if side == 1 else 'below',
                           'start_step':lo, 'end_step':hi}


def small_counts(n):
    """n<=2 exhaustive check, deliberately using coordinate sets and DP."""
    assert n <= 2
    ps = sorted(words(n))
    sites = [(x,y) for y in range(n+1) for x in range(n+1)
             if (x,y) not in ((0,0),(n,n))]
    counts = {p:[0]*(len(sites)+1) for p in ps}
    layers = [0]*(len(sites)+1)
    for mask in range(1 << len(sites)):
        occupied = {site for i,site in enumerate(sites) if mask & (1 << i)}
        k = len(occupied)
        layers[k] += 1
        dp = {}
        for y in range(n+1):
            for x in range(n+1):
                predecessors = [dp[q] for q in ((x-1,y),(x,y-1)) if q in dp]
                dp[x,y] = max(predecessors, default=0) + ((x,y) in occupied)
        for p in ps:
            if sum(q in occupied for q in vertices(p)) == dp[n,n]:
                counts[p][k] += 1
    assert layers == [comb(len(sites),k) for k in range(len(sites)+1)]
    return counts


def build():
    output = {'schema':1, 'implementation':'step-word reversal at geometric corners',
              'source':'https://arxiv.org/html/2608.11378v2',
              'access_date':'2026-10-29', 'sizes':{}}
    for n in range(1,5):
        ps = sorted(words(n))
        assert len(ps) == comb(2*n,n)
        es = []
        for p in ps:
            for e in moves(p):
                q = e['target']
                assert q in ps and p != q
                decrease = len(corners(p))-len(corners(q))
                expected = 1 if e['kind']=='unwind' and e['l']==0 else 2
                assert decrease == expected
                delta = mixed_two_dot_count(q) - mixed_two_dot_count(p)
                assert delta > 0
                e['corner_decrease'] = decrease
                e['mixed_two_dot_gain'] = delta
                es.append(e)
        pairs = sorted({(e['source'],e['target']) for e in es})
        all_targets = {e['source'] for e in es}
        sinks = sorted(set(ps)-all_targets)
        assert sinks == ['R'*n+'U'*n, 'U'*n+'R'*n]
        # Every path reaches at least one corner path; strict corner decrease
        # already certifies acyclicity.
        adj = {p:set() for p in ps}
        for a,b in pairs: adj[a].add(b)
        reach = {}
        for p in sorted(ps, key=lambda q:len(corners(q))):
            reach[p] = set(adj[p])
            for q in adj[p]: reach[p].update(reach[q])
            if p not in sinks: assert set(sinks)&reach[p]
        d = {'path_count':len(ps), 'witness_count':len(es),
             'distinct_edge_count':len(pairs),
             'bump_witnesses':sum(e['kind']=='bump' for e in es),
             'unwind_witnesses':sum(e['kind']=='unwind' for e in es),
             'boundary_unwind_witnesses':sum(e['kind']=='unwind' and e['l']==0 for e in es),
             'strict_transitive_pairs':sum(map(len,reach.values())),
             'sinks':sinks, 'edges':es, 'distinct_pairs':pairs,
             'mixed_two_dot_counts':{p:mixed_two_dot_count(p) for p in ps}}
        if n <= 2: d['small_counts'] = small_counts(n)
        output['sizes'][str(n)] = d
    target = Path(__file__).resolve().parents[1]/'review'/'independent_moves.json'
    target.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({n:{k:v for k,v in d.items() if k not in ('edges','distinct_pairs','mixed_two_dot_counts','small_counts')}
                      for n,d in output['sizes'].items()},indent=2))


if __name__ == '__main__':
    build()
