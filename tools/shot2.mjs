import {chromium} from 'playwright';
const b=await chromium.launch();
for(const [p,url] of [['partners','http://127.0.0.1:4173/oasis-partners'],['calls','http://127.0.0.1:4173/calls-for-artists-oasis']]){
  const ctx=await b.newContext({viewport:{width:1440,height:1000}});
  const pg=await ctx.newPage();
  await pg.goto(url,{waitUntil:'networkidle',timeout:60000});
  await pg.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=350){scrollTo(0,y);await new Promise(r=>setTimeout(r,70));}});
  await pg.waitForTimeout(900);await pg.evaluate(()=>scrollTo(0,0));await pg.waitForTimeout(500);
  await pg.screenshot({path:`_shots/${p}-local.png`,fullPage:true});
  await ctx.close();
}
await b.close();console.log('ok');
