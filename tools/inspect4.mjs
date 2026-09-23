import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:1000}});
const p=await ctx.newPage();
await p.goto('https://theoasisproject.eu/about-us-oasis',{waitUntil:'networkidle',timeout:60000});
await p.waitForTimeout(3000);
console.log(JSON.stringify(await p.evaluate(()=>{
  const f=document.querySelector('iframe');
  const bb=f.getBoundingClientRect();const s=getComputedStyle(f);
  const par=f.parentElement.getBoundingClientRect();const ps=getComputedStyle(f.parentElement);
  return {iframe:{w:Math.round(bb.width),h:Math.round(bb.height),top:Math.round(bb.top+scrollY)},
          css:{w:s.width,h:s.height,ar:s.aspectRatio},
          parent:{cls:(f.parentElement.className+'').slice(0,40),w:Math.round(par.width),h:Math.round(par.height),top:Math.round(par.top+scrollY),of:ps.overflow,pos:ps.position}};
}),null,1));
await b.close();
