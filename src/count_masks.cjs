'use strict';
// Independent implementation A: direct comparison of every path-mask score.
// No lattice optimum recursion is used here.
const fs = require('fs');
const path = require('path');
const [nArg, output, limitArg] = process.argv.slice(2);
const n = Number(nArg);
if (!Number.isInteger(n) || n < 1 || n > 4 || !output) throw Error('usage: node count_masks.cjs n output.json [limit] (1<=n<=4)');
const sites = [];
for (let y=0;y<=n;y++) for(let x=0;x<=n;x++)
  if (!(x===0&&y===0) && !(x===n&&y===n)) sites.push([x,y]);
const index = new Map(sites.map((v,i)=>[v.join(','),i]));
const words=[];
function paths(s,r,u){
  if(r===n&&u===n){words.push(s);return;}
  if(r<n) paths(s+'R',r+1,u);
  if(u<n) paths(s+'U',r,u+1);
}
paths('',0,0);
const masks = words.map(w=>{
  let x=0,y=0,mask=0;
  for(const c of w){if(c==='R')x++;else y++; const i=index.get(x+','+y);if(i!==undefined)mask|=1<<i;}
  return mask;
});
function popcount(v){v=v-((v>>>1)&0x55555555);v=(v&0x33333333)+((v>>>2)&0x33333333);return (((v+(v>>>4))&0x0f0f0f0f)*0x01010101)>>>24;}
const m=sites.length, total=2**m, limit=limitArg?Math.min(Number(limitArg),total):total;
const counts=words.map(()=>new Uint32Array(m+1)), layers=new Uint32Array(m+1), scores=new Uint8Array(words.length);
const started=Date.now(), cpu0=process.cpuUsage();
for(let config=0;config<limit;config++){
  const k=popcount(config); layers[k]++;
  let best=-1;
  for(let j=0;j<masks.length;j++){const score=popcount(config&masks[j]);scores[j]=score;if(score>best)best=score;}
  for(let j=0;j<masks.length;j++)if(scores[j]===best)counts[j][k]++;
}
const cpu=process.cpuUsage(cpu0);
const result={implementation:'A: direct path masks and SWAR population counts',n,m,sites,path_order:'R before U lexicographic',configurations:limit,complete:limit===total,layer_totals:[...layers],counts:Object.fromEntries(words.map((w,j)=>[w,[...counts[j]]])),path_masks:Object.fromEntries(words.map((w,j)=>[w,masks[j]])),runtime:{wall_seconds:(Date.now()-started)/1000,cpu_seconds:(cpu.user+cpu.system)/1e6,node:process.version,platform:process.platform,arch:process.arch}};
fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({n,configurations:limit,complete:result.complete,...result.runtime}));
