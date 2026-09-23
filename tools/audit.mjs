// For every page: hide the text, screenshot the background, and record where each
// piece of text sits and what colour it is. tools/audit.py then measures the real
// contrast of each text box against the pixels actually behind it.
import {chromium} from 'playwright';
import fs from 'fs';
const slugs=JSON.parse(fs.readFileSync('site-data.json','utf8'));
const pages=Object.values(slugs.pages).filter(p=>p.blocks&&p.blocks.length).map(p=>p.slug==='home'?'':p.slug);
const b=await chromium.launch();
const out={};
for(const s of pages){
  const ctx=await b.newContext({viewport:{width:1440,height:1000}});
  const p=await ctx.newPage();
  await p.goto('http://127.0.0.1:4173/'+s,{waitUntil:'networkidle',timeout:60000});
  await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}scrollTo(0,0);});
  await p.waitForTimeout(1200);
  const boxes=await p.evaluate(()=>{
    const res=[];
    document.querySelectorAll('.el-text, .nav a, .site-header .nav a').forEach(el=>{
      const t=(el.textContent||'').trim(); if(!t) return;
      // colour + size of the first real text node holder
      const probe=el.matches('a')?el:(el.querySelector('h1,h2,h3,h4,h5,h6,p,span,li')||el);
      const cs=getComputedStyle(probe);
      const bb=el.getBoundingClientRect();
      res.push({t:t.slice(0,44),color:cs.color,size:parseFloat(cs.fontSize),weight:cs.fontWeight,
                x:Math.round(bb.left+scrollX),y:Math.round(bb.top+scrollY),
                w:Math.round(bb.width),h:Math.round(bb.height),
                plate:el.classList.contains('on-photo'),
                el:el.dataset.el||null,
                block:(el.closest('section.block')||{}).dataset?.block||null,
                bgkind:(el.closest('section.block')||{}).dataset?.bgkind||null});
    });
    return res;});
  await p.addStyleTag({content:'.el-text,.el-text *,.nav a,.nav a *,.el-btn a,.el-btn a *{color:transparent!important;text-shadow:none!important;-webkit-text-fill-color:transparent!important;text-decoration-color:transparent!important}'});
  await p.waitForTimeout(400);
  await p.screenshot({path:`_shots/bg-${s||'home'}.png`,fullPage:true});
  out[s||'home']=boxes;
  await ctx.close();
  console.log('captured',s||'home',boxes.length);
}
fs.writeFileSync('_shots/audit.json',JSON.stringify(out));
await b.close();
