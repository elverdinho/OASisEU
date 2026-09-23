import {chromium} from 'playwright';
const b=await chromium.launch();
for(const [tag,url] of [['local','http://127.0.0.1:4173/index.html'],['live','https://theoasisproject.eu/']]){
  const ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,
   userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'});
  const p=await ctx.newPage();
  await p.goto(url,{waitUntil:'networkidle',timeout:60000});
  await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,70));}});
  await p.waitForTimeout(1000);await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(600);
  await p.screenshot({path:`_shots/m-home-${tag}.png`,fullPage:true});
  await ctx.close();
}
await b.close();console.log('done');
