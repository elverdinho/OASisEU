import {chromium} from 'playwright';
const b=await chromium.launch();
async function grab(url,tag){
  const ctx=await b.newContext({viewport:{width:1440,height:1000}});
  const p=await ctx.newPage();
  await p.goto(url,{waitUntil:'networkidle',timeout:60000});
  await p.evaluate(()=>scrollTo(0,document.body.scrollHeight));
  await p.waitForTimeout(2000);
  const r=await p.evaluate(()=>{
    const f=document.querySelector('footer')||[...document.querySelectorAll('.block')].pop();
    const bb=f.getBoundingClientRect();
    const kids=[...f.querySelectorAll('*')].filter(e=>getComputedStyle(e).backgroundImage!=='none'||getComputedStyle(e).backgroundColor!=='rgba(0, 0, 0, 0)')
      .slice(0,5).map(e=>{const s=getComputedStyle(e);return{cls:(e.className+'').slice(0,40),bg:s.backgroundColor,img:s.backgroundImage.slice(0,55),op:s.opacity,bl:s.mixBlendMode};});
    return {h:Math.round(bb.height),kids};
  });
  await p.screenshot({path:`_shots/footer-${tag}.png`,clip:{x:0,y:1000-Math.min(r.h,340),width:1440,height:Math.min(r.h,340)}});
  console.log(tag,JSON.stringify(r,null,1).slice(0,900));
  await ctx.close();
}
await grab('https://theoasisproject.eu/','live');
await grab('http://127.0.0.1:4173/','mine');
await b.close();
