import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:400}});
const p=await ctx.newPage();
await p.goto('http://127.0.0.1:4173/about-us-oasis',{waitUntil:'networkidle',timeout:60000});
await p.waitForTimeout(1500);
await p.screenshot({path:'_shots/hdr-about.png',clip:{x:0,y:0,width:1440,height:200}});
await b.close();
