import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:400}});
const p=await ctx.newPage();
await p.goto('https://theoasisproject.eu/about-us-oasis',{waitUntil:'networkidle',timeout:60000});
await p.waitForTimeout(2500);
await p.screenshot({path:'_shots/about-top-live.png',clip:{x:0,y:0,width:1440,height:300}});
const info=await p.evaluate(()=>{
  const out=[];
  document.querySelectorAll('*').forEach(e=>{
    const s=getComputedStyle(e);
    if(s.backgroundImage&&s.backgroundImage!=='none'){
      const bb=e.getBoundingClientRect();
      if(bb.top<300&&bb.height>3) out.push({cls:(e.className+'').slice(0,45),tag:e.tagName,top:Math.round(bb.top),h:Math.round(bb.height),img:s.backgroundImage.slice(0,75),pos:s.position,z:s.zIndex});
    }});
  return out;});
console.log(JSON.stringify(info,null,1).slice(0,1800));
await b.close();
