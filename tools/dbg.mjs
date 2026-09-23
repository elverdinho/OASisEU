import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:1000}});
const p=await ctx.newPage();
await p.goto('http://127.0.0.1:4173/',{waitUntil:'networkidle',timeout:60000});
await p.evaluate(()=>scrollTo(0,document.body.scrollHeight));await p.waitForTimeout(1500);
console.log(JSON.stringify(await p.evaluate(()=>{
  const f=document.querySelector('footer .block');
  const fb=f.getBoundingClientRect();
  const cv=f.querySelector('.canvas').getBoundingClientRect();
  const cs=getComputedStyle(f);
  return {blockH:Math.round(fb.height),pad:cs.padding,
    canvasOffsetTop:Math.round(cv.top-fb.top),
    els:[...f.querySelectorAll('.el')].map(e=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);
      return {t:(e.textContent||'').trim().slice(0,26)||e.className,cssTop:s.top,rendTop:Math.round(r.top-fb.top),h:Math.round(r.height),mh:s.minHeight,jc:s.justifyContent};})};
}),null,1));
await b.close();
