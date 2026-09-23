import {chromium} from 'playwright';
const b=await chromium.launch();
for(const u of ['https://theoasisproject.eu/','https://theoasisproject.eu/about-us-oasis']){
  const ctx=await b.newContext({viewport:{width:1440,height:1000}});
  const p=await ctx.newPage();
  await p.goto(u,{waitUntil:'networkidle',timeout:60000});
  await p.waitForTimeout(2000);
  const r=await p.evaluate(()=>{
    const out=[];
    const hdr=document.querySelector('header')||document.querySelector('[class*="header"]');
    if(hdr){const s=getComputedStyle(hdr);const bb=hdr.getBoundingClientRect();
      out.push({tag:'HEADER',cls:hdr.className.slice(0,60),pos:s.position,top:bb.top,h:bb.height,bg:s.backgroundColor,z:s.zIndex});}
    document.querySelectorAll('section,[class*="block"]').forEach((el,i)=>{
      if(i>6)return;const bb=el.getBoundingClientRect();const s=getComputedStyle(el);
      if(bb.height<5)return;
      out.push({tag:el.tagName,cls:(el.className+'').slice(0,50),top:Math.round(bb.top+scrollY),h:Math.round(bb.height),pt:s.paddingTop,bg:s.backgroundColor.slice(0,30),img:(s.backgroundImage||'').slice(0,50)});
    });
    return out;
  });
  console.log('###',u);console.log(JSON.stringify(r,null,1).slice(0,2200));
  await ctx.close();
}
await b.close();
