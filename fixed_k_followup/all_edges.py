"""Complete k=3 n=5 layer. Independent lattice-DP optimum and direct path sums."""
from pathlib import Path
from itertools import combinations
import sys,json,collections,time
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'src'))
from independent_moves import words,moves,vertices
n=5;sites=[(x,y) for y in range(n+1) for x in range(n+1) if (x,y) not in ((0,0),(n,n))];ps=sorted(words(n));pathsets=[set(vertices(w)) for w in ps];counts=[0]*len(ps);layers=0;t=time.time()
for triple in combinations(sites,3):
 S=set(triple);dp={}
 for y in range(n+1):
  for x in range(n+1):dp[x,y]=((x,y) in S)+max(dp.get((x-1,y),0),dp.get((x,y-1),0))
 best=dp[n,n];layers+=1
 for j,p in enumerate(pathsets):counts[j]+=(sum(q in p for q in triple)==best)
rows=dict(zip(ps,counts));edges=[]
for w in ps:
 for e in moves(w):
  e['delta']=rows[e['target']]-rows[w];edges.append(e)
assert layers==5984
data={'n':n,'k':3,'configurations':layers,'path_count':len(ps),'path_counts':rows,'edges':edges,'negative_edges':[e for e in edges if e['delta']<0],'distribution':dict(sorted(collections.Counter(e['delta'] for e in edges).items())),'wall_seconds':time.time()-t,'method':'DP optimum + direct path sums for every 3-subset; no full 2^34 enumeration'}
(Path(__file__).parent/'all_edges_n5_k3.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in data.items() if k not in ('edges','path_counts','negative_edges')},indent=2));print('negative edges:',len(data['negative_edges']));print(json.dumps(data['negative_edges'][:12],indent=2))
