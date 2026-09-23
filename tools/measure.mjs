import {chromium} from 'playwright';
const b=await chromium.launch();
async function m(url,sel){
  const ctx=await b.newContext({viewport:{width:1440,height:1000}});
  const p=await ctx.newPage();
  await p.goto(url,{waitUntil:'networkidle',timeout:60000});
  await p.waitForTimeout(2500);
  const r=await p.evaluate((sel)=>{
    const out=[];
    document.querySelectorAll(sel).forEach(e=>{const bb=e.getBoundingClientRect();
      if(bb.height>2) out.push([Math.round(bb.top+scrollY),Math.round(bb.height)]);});
    return out;},sel);
  await ctx.close();return r;
}
for(const [name,lu,loc] of [['home','https://theoasisproject.eu/','http://127.0.0.1:4173/index.html'],
                            ['about','https://theoasisproject.eu/about-us-oasis','http://127.0.0.1:4173/about-us-oasis.html']]){
  const live=await m(lu,'main.page > div > .block, main.page .block');
  const mine=await m(loc,'header.site-header, main > section.block, footer section.block');
  console.log(name,'\n live:',JSON.stringify(live.slice(0,10)),'\n mine:',JSON.stringify(mine.slice(0,10)));
}
await b.close();
