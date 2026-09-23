import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:1000}});
const p=await ctx.newPage();
await p.goto('https://theoasisproject.eu/',{waitUntil:'networkidle',timeout:60000});
await p.waitForTimeout(2500);
console.log(JSON.stringify(await p.evaluate(()=>{
  const blk=document.querySelectorAll('.block')[0];
  const bb=blk.getBoundingClientRect();
  const kids=[...blk.querySelectorAll('img,a')].map(e=>{const r=e.getBoundingClientRect();
    return {tag:e.tagName,top:Math.round(r.top-bb.top),h:Math.round(r.height),w:Math.round(r.width)};}).filter(k=>k.h>20);
  return {blockTop:Math.round(bb.top+scrollY),blockH:Math.round(bb.height),kids};
}),null,1));
await b.close();
