"""Run-formula move generator. Coordinates: U positive, R negative.
Boundary convention is explicit and independently audited in review/.
"""
import itertools, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def paths(n):
    return sorted(''.join('U' if i in us else 'R' for i in range(2*n))
                  for us in itertools.combinations(range(2*n),n))

def runs(w):
    return [len(list(g))*(1 if c=='U' else -1) for c,g in itertools.groupby(w)]

def word(a):
    assert all(v!=0 for v in a)
    assert all(a[i]*a[i+1]<0 for i in range(len(a)-1))
    return ''.join(('U' if v>0 else 'R')*abs(v) for v in a)

def generate(n):
    witnesses=[]
    for w in paths(n):
        aa=runs(w); r=len(aa); a=[0]+aa; s=list(itertools.accumulate(a))
        for k in range(2,r-1):
            if (s[k]>=0 and a[k]<0) or (s[k]<=0 and a[k]>0):
                b=a[1:k-1]+[a[k-1]+a[k+1],a[k]+a[k+2]]+a[k+3:]
                witnesses.append(dict(source=w,target=word(b),kind='bump',k=k,l=None))
        for l in range(r):
            for k in range(l+2,r):
                for sign in (-1,1):
                    if (l==0 or sign*s[l]>0) and sign*s[k]>0 and all(sign*s[i]<0 for i in range(l+1,k)):
                        b=a[1:l]+[a[l]+a[k]]+list(reversed(a[l+2:k]))+[a[k+1]+a[l+1]]+a[k+2:]
                        witnesses.append(dict(source=w,target=word(b),kind='unwind',l=l,k=k))
    universe=set(paths(n))
    for e in witnesses:
        assert e['target'] in universe
        assert len(runs(e['target']))<len(runs(e['source']))
    unique=sorted(set((e['source'],e['target']) for e in witnesses))
    edges=[dict(source=x,target=y,witnesses=[e for e in witnesses if e['source']==x and e['target']==y]) for x,y in unique]
    return dict(n=n,paths=[dict(word=w,runs=runs(w)) for w in paths(n)],witness_count=len(witnesses),edge_count=len(edges),edges=edges)

if __name__=='__main__':
    for n in range(1,5):
        result=generate(n)
        (ROOT/'results'/f'moves_n{n}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(n,result['witness_count'],result['edge_count'])
