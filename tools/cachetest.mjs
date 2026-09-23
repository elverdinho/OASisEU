import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext();           // one context = one persistent cache
const p=await ctx.newPage();
await p.goto('http://127.0.0.1:4173/',{waitUntil:'networkidle'});
const first=await p.evaluate(()=>document.body.innerText.includes('Cultivamos Cultura'));
// now reload the way a user hits F5
await p.reload({waitUntil:'networkidle'});
const second=await p.evaluate(()=>document.body.innerText.includes('Cultivamos Cultura'));
const hdrs=await p.evaluate(async()=>{
  const r=await fetch(location.href,{cache:'no-store'});
  return {cc:r.headers.get('cache-control'),etag:r.headers.get('etag'),lm:r.headers.get('last-modified')};
});
console.log(JSON.stringify({firstLoadHasNewCall:first,afterReload:second,headers:hdrs},null,1));
await b.close();
