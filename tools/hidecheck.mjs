import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:1000}});
const p=await ctx.newPage();
await p.goto('http://127.0.0.1:4173/garage-modern-open-call',{waitUntil:'networkidle',timeout:60000});
await p.addStyleTag({content:'.el-text,.el-text *,.nav a,.nav a *,.el-btn a,.el-btn a *{color:transparent!important;text-shadow:none!important;-webkit-text-fill-color:transparent!important;text-decoration-color:transparent!important}'});
await p.waitForTimeout(500);
console.log(JSON.stringify(await p.evaluate(()=>{
  const a=[...document.querySelectorAll('.nav a')].find(x=>x.textContent.trim()==='Home');
  const cs=getComputedStyle(a);
  return {color:cs.color,fill:cs.webkitTextFillColor,shadow:cs.textShadow,
          parentColor:getComputedStyle(a.parentElement).color};
}),null,1));
await b.close();
