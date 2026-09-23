import {chromium} from 'playwright';
const b=await chromium.launch();
async function go(url,tag){
  const ctx=await b.newContext({viewport:{width:1440,height:1000}});
  const p=await ctx.newPage();
  await p.goto(url,{waitUntil:'networkidle',timeout:60000});
  const y=await p.evaluate(()=>{const el=[...document.querySelectorAll('h1,h2,h3')].find(e=>/OASis Mission/i.test(e.textContent));
    return el?el.getBoundingClientRect().top+scrollY-120:null;});
  if(y===null){console.log(tag,'not found');await ctx.close();return;}
  await p.evaluate(async(y)=>{for(let v=0;v<y;v+=300){scrollTo(0,v);await new Promise(r=>setTimeout(r,70));}scrollTo(0,y);},y);
  await p.waitForTimeout(2500);
  await p.screenshot({path:`_shots/mission-${tag}.png`,clip:{x:0,y:0,width:1440,height:620}});
  console.log(tag,'captured at',Math.round(y));
  await ctx.close();
}
await go('https://theoasisproject.eu/','live');
await go('http://127.0.0.1:4173/','mine');
await b.close();
