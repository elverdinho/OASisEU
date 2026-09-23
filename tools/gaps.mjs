import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:1200},deviceScaleFactor:1});
const p=await ctx.newPage();
await p.goto('http://127.0.0.1:4173/cc-second-call',{waitUntil:'networkidle'});
await p.evaluate(async()=>{for(let y=0;y<2500;y+=300){scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}scrollTo(0,0);});
await p.waitForTimeout(800);
console.log('DOM boxes:',JSON.stringify(await p.evaluate(()=>{
  const blk=[...document.querySelectorAll('section.block')][1];
  const bb=blk.getBoundingClientRect();
  return [...blk.querySelectorAll('.el-img')].map(e=>{const r=e.getBoundingClientRect();
    const img=e.querySelector('img');const ir=img.getBoundingClientRect();
    return {src:img.getAttribute('src').split('/').pop().slice(0,26),
            elTop:Math.round(r.top-bb.top),elBot:Math.round(r.bottom-bb.top),
            imgTop:Math.round(ir.top-bb.top),imgBot:Math.round(ir.bottom-bb.top),
            imgLeft:Math.round(ir.left),imgRight:Math.round(ir.right),
            radius:getComputedStyle(img).borderRadius};});
})));
await p.screenshot({path:'_shots/gapcol.png',fullPage:true});
await b.close();
