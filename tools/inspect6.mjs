import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:1000}});
const p=await ctx.newPage();
await p.goto('https://theoasisproject.eu/about-us-oasis',{waitUntil:'networkidle',timeout:60000});
await p.waitForTimeout(3000);
console.log(JSON.stringify(await p.evaluate(()=>{
  const f=document.querySelector('form');
  const btn=f.querySelector('button,input[type=submit]');
  const inp=f.querySelector('input');
  const lab=f.querySelector('label');
  const cs=e=>{const s=getComputedStyle(e);return {bg:s.backgroundColor,color:s.color,border:s.border,radius:s.borderRadius,pad:s.padding,fs:s.fontSize,ff:s.fontFamily.slice(0,25),h:Math.round(e.getBoundingClientRect().height),w:Math.round(e.getBoundingClientRect().width)};};
  const ph=getComputedStyle(inp,'::placeholder');
  return {form:cs(f),button:{...cs(btn),text:btn.textContent.trim()},input:cs(inp),placeholder:{color:ph.color},label:{...cs(lab),text:lab.textContent.trim()},
          action:f.getAttribute('action'),method:f.method, fields:[...f.querySelectorAll('label')].map(l=>l.textContent.trim())};
}),null,1));
await b.close();
