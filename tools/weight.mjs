import {chromium} from 'playwright';
const b=await chromium.launch();
async function w(scroll){
  const ctx=await b.newContext({viewport:{width:1440,height:1000}});
  const p=await ctx.newPage();
  let bytes=0; const seen=new Set();
  p.on('response',async r=>{try{const h=r.headers()['content-length'];
    if(h&&!seen.has(r.url())){seen.add(r.url());bytes+=parseInt(h,10);} }catch(e){}});
  await p.goto('http://127.0.0.1:4173/',{waitUntil:'networkidle',timeout:60000});
  if(scroll){await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,90));}});
             await p.waitForTimeout(3000);}
  await ctx.close();
  return (bytes/1048576).toFixed(1);
}
console.log('home, senza scorrere :', await w(false), 'MB');
console.log('home, tutta scorsa   :', await w(true), 'MB');
await b.close();
