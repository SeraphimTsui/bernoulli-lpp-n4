"""Exact k=3 layers only, using longest chains of occupied points."""
from itertools import combinations
from math import comb
import json,time
from pathlib import Path
def points(word):
 x=y=0; out={(0,0)}
 for c in word:
  x+=c=='R';y+=c=='U';out.add((x,y))
 return out
def comparable(a,b):return (a[0]<=b[0] and a[1]<=b[1]) or (b[0]<=a[0] and b[1]<=a[1])
def chain3(a,b,c):
 return comparable(a,b) and comparable(a,c) and comparable(b,c)
def compute(n):
 sites=[(x,y) for y in range(n+1) for x in range(n+1) if (x,y) not in ((0,0),(n,n))]
 a='RUURUU'+'R'*(n-2)+'U'*(n-4)
 b='UURRUU'+'R'*(n-2)+'U'*(n-4)
 pa,pb=points(a),points(b); counts=[0,0];both=0;plus=[];minus=[]
 for x,y,z in combinations(sites,3):
  if chain3(x,y,z):best=3
  elif comparable(x,y) or comparable(x,z) or comparable(y,z):best=2
  else:best=1
  ga=sum(v in pa for v in (x,y,z))==best
  gb=sum(v in pb for v in (x,y,z))==best
  counts[0]+=ga;counts[1]+=gb;both+=ga and gb
  if ga and not gb and len(minus)<3:minus.append([x,y,z])
  if gb and not ga and len(plus)<3:plus.append([x,y,z])
 return dict(n=n,free_sites=len(sites),k=3,total=comb(len(sites),3),source=a,target=b,counts=counts,both=both,source_only=counts[0]-both,target_only=counts[1]-both,delta=counts[1]-counts[0],source_only_examples=minus,target_only_examples=plus)
if __name__=='__main__':
 start=time.time();data=[compute(n) for n in range(4,11)];p=Path(__file__).parent/'results.json';p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8');print(json.dumps(data,indent=2));print('wall_seconds',time.time()-start)
