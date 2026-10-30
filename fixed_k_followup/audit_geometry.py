"""Independent finite audit of each geometric subclaim in the analytic proof.

Construct all sets from path step words, not from the manuscript's displayed C.
Compute antichain, chain, rectangle, and pair counts directly from coordinates.
This is a finite audit through n=30, not a proof by finite testing.
"""
from itertools import combinations
from pathlib import Path
from math import comb
import hashlib,json,time

def trace(w):
    x=y=0;p={(0,0)}
    for ch in w:
        if ch=='R':x+=1
        else:y+=1
        p.add((x,y))
    return p
def le(a,b):return a[0]<=b[0] and a[1]<=b[1]
def compatible(a,b):return le(a,b) or le(b,a)
def chain(triple):return all(compatible(a,b) for a,b in combinations(triple,2))

def audit(n):
    V={(x,y) for x in range(n+1) for y in range(n+1)};ends={(0,0),(n,n)};W=V-ends
    A=trace('RUUR'+'U'*(n-2)+'R'*(n-2)) & W
    B=trace('UURR'+'U'*(n-2)+'R'*(n-2)) & W
    a,b,c,d=(1,0),(1,1),(0,1),(0,2)
    assert A-B=={a,b} and B-A=={c,d}
    L=(A-B)|(B-A);C=A&B;D=W-L-C
    assert C==({(1,2)}|{(2,y) for y in range(2,n+1)}|{(x,n) for x in range(3,n)})
    ant={}
    for x in (a,b,c,d):
        pool=[z for z in D if not compatible(x,z)]
        ant[str(x)]=sum(not compatible(u,v) for u,v in combinations(pool,2))
    assert [ant[str(z)] for z in (a,b,c,d)]==[0,(n-2)*(n-1),0,comb(n-1,2)]
    rectangles=0
    for h in C:
        assert all(le(x,h) for x in L)
        assert all(not le(z,x) for z in D for x in L)
        q=sum(int(le(a,z) and le(z,h))+int(le(b,z) and le(z,h))-
              int(le(c,z) and le(z,h))-int(le(d,z) and le(z,h)) for z in D)
        by_chain=sum(int(chain((a,h,z)))+int(chain((b,h,z)))-
                     int(chain((c,h,z)))-int(chain((d,h,z))) for z in D)
        assert q==by_chain==2*(h[0]-h[1]+1)
        rectangles+=q
    assert rectangles==2-2*(n-3)**2
    pair_a=sum(chain((a,b,z)) for z in D);pair_b=sum(chain((c,d,z)) for z in D)
    assert pair_a-pair_b==1
    values=[]
    for triple in combinations((a,b,c,d),3):
        longest=3 if chain(triple) else 2 if any(compatible(u,v) for u,v in combinations(triple,2)) else 1
        values.append(int(sum(x in B for x in triple)==longest)-int(sum(x in A for x in triple)==longest))
    assert values==[-1,-1,1,1]
    return {'n':n,'local_vertices':len(L),'common_vertices':len(C),'off_path_vertices':len(D),'antichain_counts':[ant[str(z)] for z in (a,b,c,d)],'one_local_one_common_signed_chain_count':rectangles,'two_local_signed_chain_count':pair_a-pair_b,'three_local_values':values}
if __name__=='__main__':
    start=time.process_time();rows=[audit(n) for n in range(4,31)]
    out={'description':'coordinate set, local antichain and chain subclaim audit',
         'scope':'all n=4,...,30; finite subclaim check, not a universal proof',
         'results':rows,'cpu_seconds':time.process_time()-start,
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (Path(__file__).parent/'audit_geometry.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'n_min':4,'n_max':30,'all_assertions_passed':True,'cpu_seconds':out['cpu_seconds']},indent=2))
