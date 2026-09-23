import {chromium} from 'playwright';
const b=await chromium.launch();
for(const [tag,url] of [['local','http://127.0.0.1:4173/'],['live','https://theoasisproject.eu/']]){
  const ctx=await b.newContext({viewport:{width:1440,height:1000}});
  const p=await ctx.newPage();
  await p.goto(url,{waitUntil:'networkidle',timeout:60000});
  const y=await p.evaluate(async()=>{
    for(let v=0;v<5000;v+=300){scrollTo(0,v);await new Promise(r=>setTimeout(r,60));}
    const el=[...document.querySelectorAll('h1,h2,h3,p,span')].find(e=>/OASis Gallery/i.test(e.textContent));
    return el.getBoundingClientRect().top+scrollY-40;});
  await p.evaluate(y=>scrollTo(0,y),y);await p.waitForTimeout(1600);
  await p.screenshot({path:`_shots/gal-${tag}.png`,clip:{x:0,y:0,width:1440,height:800}});
  await ctx.close();
}
await b.close();console.log('ok');
