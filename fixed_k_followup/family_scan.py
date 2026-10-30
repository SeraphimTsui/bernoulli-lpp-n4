from itertools import combinations
from pathlib import Path
import json
from scan import points,comparable,chain3
out=[]
for n in range(4,12):
 a='RUUR'+'U'*(n-2)+'R'*(n-2);b='UURR'+'U'*(n-2)+'R'*(n-2)
 A,B=points(a),points(b);sites=[(x,y) for x in range(n+1) for y in range(n+1) if (x,y) not in ((0,0),(n,n))];c=[0,0]
 for triple in combinations(sites,3):
  x,y,z=triple;best=3 if chain3(x,y,z) else (2 if comparable(x,y) or comparable(x,z) or comparable(y,z) else 1)
  c[0]+=sum(v in A for v in triple)==best;c[1]+=sum(v in B for v in triple)==best
 candidate=-(5*n*n-27*n+32)//2
 assert c[1]-c[0]==candidate
 out.append(dict(n=n,source=a,target=b,counts=c,delta=c[1]-c[0],candidate_formula=candidate))
(Path(__file__).parent/'family_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
