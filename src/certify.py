"""Exact lightweight certificate checks, no floating-point sign tests."""
import csv, hashlib, json, math
from pathlib import Path
from moves import generate, runs, paths
ROOT=Path(__file__).resolve().parents[1]

def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def vertices(w):
    out=[(0,0)];x=y=0
    for c in w:
        x+=c=='R';y+=c=='U';out.append((x,y))
    return out
def c11(w,n):
    p=set(vertices(w));other={(x,y) for x in range(n+1) for y in range(n+1)}-p
    return sum((x-a)*(y-b)<0 for x,y in p for a,b in other)

independent_moves=read('review/independent_moves.json')['sizes']
summaries=[]
for n in range(1,5):
    a=read(f'results/counts_n{n}.json');b=read(f'results/replay_n{n}.json');m=(n+1)**2-2
    assert a['complete'] and b['checks']['complete']
    assert a['configurations']==b['full_configuration_count']==2**m
    assert a['counts']==b['counts'], f'Independent mismatch n={n}'
    assert a['layer_totals']==b['layers']==[math.comb(m,k) for k in range(m+1)]
    rows=a['counts'];assert sorted(rows)==paths(n)
    for w,c in rows.items():
        assert len(c)==m+1 and all(type(v) is int for v in c)
        assert c[0]==c[m]==1 and c[1]==2*n-1
        assert all(0<=v<=math.comb(m,k) for k,v in enumerate(c))
        assert rows[w.translate(str.maketrans('RU','UR'))]==c==rows[w[::-1]]
        assert c[2]==math.comb(2*n-1,2)+c11(w,n)
    moves=generate(n);assert moves==read(f'results/moves_n{n}.json')
    geom=independent_moves[str(n)]
    assert sorted([e['source'],e['target']] for e in moves['edges'])==geom['distinct_pairs']
    def witness_id(e): return (e['source'],e['target'],e['kind'],e.get('l'),e['k'])
    assert {witness_id(w) for e in moves['edges'] for w in e['witnesses']}=={witness_id(e) for e in geom['edges']}
    if n<=2: assert rows==geom['small_counts']
    for w in rows: assert c11(w,n)==geom['mixed_two_dot_counts'][w]
    certs=[]
    for e in moves['edges']:
        x,y=e['source'],e['target'];d=[v-u for u,v in zip(rows[x],rows[y])]
        assert d[0]==d[-1]==d[1]==0
        assert d[2]==c11(y,n)-c11(x,n)>0, e
        elevated=[(d[k] if k<=m else 0)+(d[k-1] if k>=1 else 0) for k in range(m+2)]
        assert all(v>=0 for v in elevated) and elevated[2]>=2
        # Multiplication by p+(1-p)=1 gives a degree-(m+1) representation.
        # At least its k=2 basis term is strictly positive for every 0<p<1.
        certs.append(dict(**e,delta=d,elevated_delta=elevated,certificate_degree=m+1,strict_on_open_unit_interval=True,coefficientwise_nonnegative=all(v>=0 for v in d),positive_indices=[k for k,v in enumerate(d) if v>0],negative_indices=[k for k,v in enumerate(d) if v<0]))
    # Transitive reachability and the exact set of maximal paths.
    reach={w:set() for w in rows}
    for e in moves['edges']:reach[e['source']].add(e['target'])
    for w in sorted(rows,key=lambda w:len(runs(w))):
        for v in list(reach[w]):reach[w].update(reach[v])
    maxima=[w for w in rows if not reach[w]]
    assert maxima==['R'*n+'U'*n,'U'*n+'R'*n]
    assert all(w in maxima or reach[w].intersection(maxima) for w in rows)
    info=dict(n=n,free_sites=m,configurations=2**m,paths=len(rows),move_witnesses=moves['witness_count'],edges=len(certs),strict_comparable_pairs=sum(map(len,reach.values())),coefficientwise_certified_edges=sum(c['coefficientwise_nonnegative'] for c in certs),minimum_delta2=min((c['delta'][2] for c in certs),default=None),negative_coefficient_edges=[(c['source'],c['target']) for c in certs if c['negative_indices']],all_counts_independently_matched=True,all_layers_matched=True,maximal_paths=maxima,main_cpu_seconds=a['runtime']['cpu_seconds'],replay_cpu_seconds=b['cpu_seconds'])
    info['all_edges_certified_after_one_elevation']=True
    info['all_move_witnesses_independently_matched']=True
    info['bump_edges']=geom['bump_witnesses']
    info['unwind_edges']=geom['unwind_witnesses']
    info['boundary_unwind_edges']=geom['boundary_unwind_witnesses']
    assert info['strict_comparable_pairs']==geom['strict_transitive_pairs']
    (ROOT/f'results/certificates_n{n}.json').write_text(json.dumps(dict(summary=info,edges=certs,reachability={w:sorted(v) for w,v in reach.items()}),indent=2)+'\n',encoding='utf8')
    with (ROOT/f'results/counts_n{n}.csv').open('w',newline='',encoding='utf8') as f:
        wr=csv.writer(f);wr.writerow(['path']+[f'k={k}' for k in range(m+1)]);wr.writerows([w]+c for w,c in rows.items())
    summaries.append(info)
(ROOT/'results/certificate_summary.json').write_text(json.dumps(summaries,indent=2)+'\n',encoding='utf8')
print(json.dumps(summaries,indent=2))
