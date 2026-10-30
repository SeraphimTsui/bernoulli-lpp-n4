"""Independent full k=3 replay via sparse longest-chain DP and bitmask scoring.

Also verifies the four summands in the combinatorial proof against individual
configurations; this uses no case formulas to decide path optimality.
"""
from itertools import combinations
from pathlib import Path
import hashlib,json,time

def vertex_mask(word,index):
    x=y=0;m=0
    for c in word:
        if c=='R':x+=1
        else:y+=1
        if (x,y) in index:m |= 1 << index[x,y]
    return m

def run(n):
    sites=[(x,y) for x in range(n+1) for y in range(n+1) if (x,y) not in ((0,0),(n,n))]
    index={v:i for i,v in enumerate(sites)}
    a='RUUR'+'U'*(n-2)+'R'*(n-2)
    b='UURR'+'U'*(n-2)+'R'*(n-2)
    ma,mb=vertex_mask(a,index),vertex_mask(b,index)
    local={(1,0),(1,1),(0,1),(0,2)}
    common=ma & mb; parts={'one_local_one_common':0,'one_local_no_common':0,
                           'one_local_two_common':0,'two_local':0,'three_local':0,'zero_local':0}
    scores=[0,0];configurations=0
    for ids in combinations(range(len(sites)),3):
        # ids are sorted by x,y; each predecessor precedes its successor.
        rank=[]
        for i in ids:
            x,y=sites[i]
            rank.append(1+max((rank[j] for j,h in enumerate(ids[:len(rank)])
                               if sites[h][0]<=x and sites[h][1]<=y),default=0))
        best=max(rank);mask=sum(1<<i for i in ids)
        hit_a=(mask&ma).bit_count()==best;hit_b=(mask&mb).bit_count()==best
        scores[0]+=hit_a;scores[1]+=hit_b;configurations+=1
        j=sum(sites[i] in local for i in ids)
        if j==1:
            c=(mask&common).bit_count()
            key=['one_local_no_common','one_local_one_common','one_local_two_common'][c]
        else:key=['zero_local',None,'two_local','three_local'][j]
        parts[key]+=int(hit_b)-int(hit_a)
    expected={'one_local_one_common':2-2*(n-3)**2,
              'one_local_no_common':-(n-1)*(n-2)//2,
              'one_local_two_common':0,'two_local':1,'three_local':0,'zero_local':0}
    assert parts==expected,(n,parts,expected)
    delta=scores[1]-scores[0]
    assert delta==-(5*n*n-27*n+32)//2
    return {'n':n,'configurations':configurations,'counts':scores,'delta':delta,'decomposition':parts,'all_terms_match_derived_formulas':True}

if __name__=='__main__':
    start=time.process_time();results=[run(n) for n in range(4,12)]
    out={'method':'independently written sparse rank-DP on three sites and direct path masks',
         'scope':'Every k=3 configuration for n=4,...,11; no all-p or full 2^m enumeration',
         'results':results,'cpu_seconds':time.process_time()-start,
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (Path(__file__).parent/'verify_sparse_dp.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
    print(json.dumps(out,indent=2))
