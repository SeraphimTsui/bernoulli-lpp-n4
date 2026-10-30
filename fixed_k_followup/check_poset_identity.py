"""Second counting route: count two-path-site chain obstructions and antichains.

This code does not classify configurations by the four local vertices.
It works for an arbitrary monotone path and enumerates off-path coordinates.
"""
from itertools import combinations
from pathlib import Path
from math import comb
import json,time,hashlib

def comparable(a,b):
    return ((a[0]<=b[0] and a[1]<=b[1]) or (b[0]<=a[0] and b[1]<=a[1]))
def path_vertices(word):
    x=y=0;out=[]
    for c in word:
        if c=='R':x+=1
        else:y+=1
        out.append((x,y))
    return out[:-1]
def count(n,word):
    P=path_vertices(word);T=len(P)
    D={(x,y) for x in range(n+1) for y in range(n+1)}-set(P)-{(0,0),(n,n)}
    # X counts all three-chains with two vertices on P and one off P.
    X=sum(comb(sum(comparable(v,z) for v in P),2) for z in D)
    # Y counts all three-antichains with exactly one vertex on P.
    Y=0
    for v in P:
        inc=[z for z in D if not comparable(v,z)]
        Y+=sum(not comparable(z,t) for z,t in combinations(inc,2))
    return {'X':X,'Y':Y,'C3':comb(T,3)+comb(T,2)*len(D)-X+Y}
if __name__=='__main__':
    start=time.process_time();rows=[]
    for n in range(4,12):
        a=count(n,'RUUR'+'U'*(n-2)+'R'*(n-2))
        b=count(n,'UURR'+'U'*(n-2)+'R'*(n-2))
        assert a['X']-b['X']==3-2*(n-3)**2
        assert b['Y']-a['Y']==-comb(n-1,2)
        assert b['C3']-a['C3']==-(5*n*n-27*n+32)//2
        rows.append({'n':n,'gamma':a,'pi':b,'X_gamma_minus_X_pi':a['X']-b['X'],'Y_pi_minus_Y_gamma':b['Y']-a['Y'],'delta':b['C3']-a['C3']})
    out={'method':'generic path identity C3=choose(T,3)+choose(T,2)*(m-T)-X+Y',
         'scope':'Independent finite evaluation n=4,...,11; analytic explanation in poset_second_derivation.txt',
         'results':rows,'cpu_seconds':time.process_time()-start,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (Path(__file__).parent/'check_poset_identity.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
    print(json.dumps(out,indent=2))
