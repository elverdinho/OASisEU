import {chromium} from 'playwright';
const pages=process.argv[2].split(',');
const b=await chromium.launch();
for(const p of pages){
  for(const [tag,base] of [['local','http://127.0.0.1:4173'],['live','https://theoasisproject.eu']]){
    const ctx=await b.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1});
    const pg=await ctx.newPage();
    const url= tag==='local' ? `${base}/${p==='home'?'index.html':p+'.html'}` : `${base}/${p==='home'?'':p}`;
    try{
      await pg.goto(url,{waitUntil:'networkidle',timeout:60000});
      await pg.waitForTimeout(2500);
      await pg.evaluate(async()=>{const step=400;for(let y=0;y<document.body.scrollHeight;y+=step){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,90));}});
      await pg.waitForTimeout(1200);
      await pg.evaluate(()=>window.scrollTo(0,0));
      await pg.waitForTimeout(800);
      const h=await pg.evaluate(()=>document.body.scrollHeight);
      await pg.screenshot({path:`_shots/${p}-${tag}.png`,fullPage:true});
      console.log(p,tag,'h='+h);
    }catch(e){console.log(p,tag,'ERR',e.message.slice(0,80));}
    await ctx.close();
  }
}
await b.close();
