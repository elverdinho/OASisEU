import {chromium} from 'playwright';
const b=await chromium.launch();
for(const [tag,w,h] of [['d',1440,1000],['m',390,844]]){
  const ctx=await b.newContext({viewport:{width:w,height:h},isMobile:tag==='m',hasTouch:tag==='m'});
  const p=await ctx.newPage();
  await p.goto('http://127.0.0.1:4173/cc-second-call',{waitUntil:'networkidle',timeout:60000});
  await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=350){scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}scrollTo(0,0);});
  await p.waitForTimeout(900);
  console.log(tag,JSON.stringify(await p.evaluate(()=>{
    const blk=[...document.querySelectorAll('section.block')][1];
    const bb=blk.getBoundingClientRect();
    const items=[...blk.querySelectorAll('.el')].map(e=>{const r=e.getBoundingClientRect();
      const t=(e.textContent||'').trim().slice(0,18);
      return {t:t||e.className.replace('el el-','').split(' ')[0],top:Math.round(r.top-bb.top),bot:Math.round(r.bottom-bb.top)};});
    return {blockH:Math.round(bb.height),overflowX:document.documentElement.scrollWidth,items};
  })));
  await p.screenshot({path:`_shots/cc-${tag}.png`,fullPage:true});
  await ctx.close();
}
await b.close();
