import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:1000}});
const p=await ctx.newPage();
await p.goto('https://theoasisproject.eu/about-us-oasis',{waitUntil:'networkidle',timeout:60000});
await p.waitForTimeout(2500);
const r=await p.evaluate(()=>{
  const out=[];
  const bs=getComputedStyle(document.body);
  out.push({t:'BODY',bg:bs.backgroundColor,img:bs.backgroundImage.slice(0,60)});
  // what is painted at y=40 x=700 ?
  const el=document.elementFromPoint(700,40);
  let n=el,chain=[];
  while(n&&chain.length<8){const s=getComputedStyle(n);chain.push({tag:n.tagName,cls:(n.className+'').slice(0,45),h:Math.round(n.getBoundingClientRect().height),top:Math.round(n.getBoundingClientRect().top),bg:s.backgroundColor.slice(0,25),img:s.backgroundImage.slice(0,70),pos:s.position,z:s.zIndex});n=n.parentElement;}
  out.push({t:'CHAIN@700,40',chain});
  document.querySelectorAll('.block').forEach((e,i)=>{if(i>3)return;const bb=e.getBoundingClientRect();const s=getComputedStyle(e);
    out.push({t:'BLOCK'+i,cls:(e.className+'').slice(0,40),top:Math.round(bb.top+scrollY),h:Math.round(bb.height),pt:s.paddingTop,mt:s.marginTop,bg:s.backgroundColor.slice(0,24),img:s.backgroundImage.slice(0,60)});});
  return out;
});
console.log(JSON.stringify(r,null,1));
await b.close();
