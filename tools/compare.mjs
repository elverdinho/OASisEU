import {chromium} from 'playwright';
import fs from 'fs';
const slugs=JSON.parse(fs.readFileSync('_mirror/_pages.json','utf8')).map(s=>s==='/'?'':s.replace(/^\//,''));
slugs.push('faq','georgia-call');
const b=await chromium.launch();
async function heights(url,sel){
  const ctx=await b.newContext({viewport:{width:1440,height:1000}});
  const p=await ctx.newPage();
  try{ await p.goto(url,{waitUntil:'networkidle',timeout:60000}); }catch(e){ await ctx.close(); return null; }
  await p.waitForTimeout(2200);
  const r=await p.evaluate(s=>[...document.querySelectorAll(s)].map(e=>Math.round(e.getBoundingClientRect().height)).filter(h=>h>2),sel);
  await ctx.close(); return r;
}
const rows=[];
for(const s of [...new Set(slugs)]){
  const live=await heights('https://theoasisproject.eu/'+s,'main.page .block');
  const mine=await heights('http://127.0.0.1:4173/'+s,'main > section.block, footer section.block');
  if(!live||!mine){rows.push([s||'home','FETCH-ERR']);continue;}
  const dl=live.reduce((a,c)=>a+c,0), dm=mine.reduce((a,c)=>a+c,0);
  const diffs=live.map((h,i)=>Math.abs(h-(mine[i]??0)));
  const worst=Math.max(...diffs,0);
  rows.push([s||'home',`blocks ${live.length}/${mine.length}`,`total ${dl}/${dm}`,`Δmax ${worst}`, worst>20||live.length!==mine.length?'CHECK':'ok']);
}
rows.forEach(r=>console.log(r.join('  |  ')));
await b.close();
