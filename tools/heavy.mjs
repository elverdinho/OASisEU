import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:1000}});
const p=await ctx.newPage();
const rows=[];
p.on('response',r=>{const h=r.headers()['content-length'];
  if(h)rows.push([parseInt(h,10),r.url().split('/').pop()]);});
await p.goto('http://127.0.0.1:4173/',{waitUntil:'networkidle',timeout:60000});
await p.waitForTimeout(1500);
rows.sort((a,c)=>c[0]-a[0]);
console.log('--- top risorse in home (senza scroll) ---');
rows.slice(0,10).forEach(([s,n])=>console.log((s/1048576).toFixed(2).padStart(7),'MB ',n.slice(0,64)));
// what size are they actually displayed at?
console.log('--- resa a schermo ---');
console.log(JSON.stringify(await p.evaluate(()=>[...document.querySelectorAll('img')]
  .map(i=>({f:i.currentSrc.split('/').pop().slice(0,40),nat:i.naturalWidth,shown:Math.round(i.getBoundingClientRect().width)}))
  .filter(x=>x.nat>x.shown*2.2).slice(0,8)),null,1));
await b.close();
