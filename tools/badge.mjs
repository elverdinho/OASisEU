import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:900}});
const p=await ctx.newPage();
const injected=[];
p.on('response',r=>{const u=r.url();
  if(!u.includes('oasis-project-eu.netlify.app')&&!u.startsWith('data:')) injected.push(u.slice(0,90));});
await p.goto('https://oasis-project-eu.netlify.app/',{waitUntil:'networkidle',timeout:60000});
await p.waitForTimeout(2500);
const found=await p.evaluate(()=>{
  const out=[];
  document.querySelectorAll('body *').forEach(e=>{
    const s=getComputedStyle(e);
    if(s.position!=='fixed') return;
    const r=e.getBoundingClientRect();
    if(r.height<1) return;
    out.push({tag:e.tagName,id:e.id||null,cls:(e.className+'').slice(0,40),
              bottom:Math.round(innerHeight-r.bottom),right:Math.round(innerWidth-r.right),
              text:(e.textContent||'').trim().slice(0,46)});
  });
  return {fixed:out,
          netlifyMentions:(document.documentElement.outerHTML.match(/netlify/gi)||[]).length,
          badgeText:/powered by netlify/i.test(document.body.innerText)};
});
console.log(JSON.stringify(found,null,1));
console.log('richieste a terze parti:',injected.length?injected:'nessuna');
await b.close();
