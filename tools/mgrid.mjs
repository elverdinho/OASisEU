import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,
 userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'});
const p=await ctx.newPage();
await p.goto('http://127.0.0.1:4173/calls-for-artists-oasis',{waitUntil:'networkidle',timeout:60000});
await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}});
const y=await p.evaluate(()=>document.querySelector('.call-filter').getBoundingClientRect().top+scrollY-30);
await p.evaluate(y=>scrollTo(0,y),y);await p.waitForTimeout(900);
console.log('overflow width:',await p.evaluate(()=>document.documentElement.scrollWidth));
await p.screenshot({path:'_shots/mgrid.png',clip:{x:0,y:0,width:390,height:820}});
await b.close();
