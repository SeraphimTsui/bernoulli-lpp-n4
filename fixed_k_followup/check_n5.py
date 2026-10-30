"""Independent fixed-k replay: longest-chain optimum, path scores by masks."""
from pathlib import Path
from itertools import combinations
import json,sys,collections
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from moves import generate
from scan import comparable,chain3
n=5;sites=[(x,y) for y in range(n+1) for x in range(n+1) if (x,y) not in ((0,0),(n,n))];idx={v:i for i,v in enumerate(sites)}
result=json.loads((Path(__file__).parent/'all_edges_n5_k3.json').read_text());paths=sorted(result['path_counts']);masks=[]
for w in paths:
 x=y=0;mask=0
 for c in w:
  x+=c=='R';y+=c=='U'
  if (x,y) in idx:mask|=1<<idx[x,y]
 masks.append(mask)
counts=[0]*len(paths);layers=0
for ids in combinations(range(len(sites)),3):
 a,b,c=(sites[i] for i in ids);best=3 if chain3(a,b,c) else (2 if comparable(a,b) or comparable(a,c) or comparable(b,c) else 1);mask=sum(1<<i for i in ids);layers+=1
 for i,p in enumerate(masks):counts[i]+=(mask&p).bit_count()==best
rows=dict(zip(paths,counts));assert rows==result['path_counts'];assert layers==result['configurations']==5984
geometric={(e['source'],e['target'],e['kind'],e.get('l'),e['k']) for e in result['edges']}
signed={(w['source'],w['target'],w['kind'],w['l'],w['k']) for e in generate(n)['edges'] for w in e['witnesses']};assert signed==geometric
neg=[e for e in result['edges'] if rows[e['target']]-rows[e['source']]<0]
summary={'n':5,'k':3,'configurations':layers,'paths':len(paths),'rows_all_match':True,'all_operation_witnesses_match':True,'move_witnesses':len(geometric),'negative_witnesses':len(neg),'negative_by_kind':dict(collections.Counter(e['kind'] for e in neg)),'minimum_delta':min(e['delta'] for e in neg),'scope':'Complete three-ones layer; not all 2^34 configurations, not all-p proof.'}
(Path(__file__).parent/'n5_independent_check.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
