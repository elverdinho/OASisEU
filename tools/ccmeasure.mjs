import {chromium} from 'playwright';
const b=await chromium.launch();
const out={};
for(const [tag,w,h] of [['d',1440,1000],['m',390,844]]){
  const ctx=await b.newContext({viewport:{width:w,height:h},isMobile:tag==='m',hasTouch:tag==='m'});
  const p=await ctx.newPage();
  await p.goto('http://127.0.0.1:4173/cc-second-call',{waitUntil:'networkidle',timeout:60000});
  await p.addStyleTag({content:'.el-text{min-height:0!important;height:auto!important}'});
  await p.waitForTimeout(600);
  out[tag]=await p.evaluate(()=>{
    const el=[...document.querySelectorAll('.el-text')].find(e=>/For 2027/.test(e.textContent));
    return Math.ceil(el.getBoundingClientRect().height);
  });
  await ctx.close();
}
console.log(JSON.stringify(out));
await b.close();
