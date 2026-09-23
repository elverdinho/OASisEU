import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:1000}});
const p=await ctx.newPage();
await p.goto('http://127.0.0.1:4173/',{waitUntil:'networkidle',timeout:60000});
await p.evaluate(async()=>{for(let y=0;y<1400;y+=250){scrollTo(0,y);await new Promise(r=>setTimeout(r,70));}});
await p.evaluate(()=>scrollTo(0,900));await p.waitForTimeout(900);
await p.screenshot({path:'_shots/homecard.png',clip:{x:60,y:0,width:700,height:480}});
await b.close();
