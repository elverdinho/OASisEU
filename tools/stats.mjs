import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:1000}});
const p=await ctx.newPage();
await p.goto('http://127.0.0.1:4173/',{waitUntil:'networkidle',timeout:60000});
const y=await p.evaluate(async()=>{
  for(let v=0;v<3000;v+=300){scrollTo(0,v);await new Promise(r=>setTimeout(r,70));}
  const el=[...document.querySelectorAll('.el-text')].find(e=>/ARTISTS INVOLVED/i.test(e.textContent));
  const s=el.closest('section.block');return s.getBoundingClientRect().top+scrollY;});
await p.evaluate(y=>scrollTo(0,y),y);await p.waitForTimeout(900);
await p.screenshot({path:'_shots/stats.png',clip:{x:0,y:0,width:1440,height:720}});
console.log(JSON.stringify(await p.evaluate(()=>[...document.querySelectorAll('.on-photo')].map(e=>e.textContent.trim().slice(0,22)))));
await b.close();
