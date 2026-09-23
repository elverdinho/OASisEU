import {chromium} from 'playwright';
const b=await chromium.launch();
const slugs=['','about-us-oasis','oasis-partners','calls-for-artists-oasis','news'];
async function h(url){
  const ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,
    userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'});
  const p=await ctx.newPage();
  try{await p.goto(url,{waitUntil:'networkidle',timeout:60000});}catch(e){await ctx.close();return null;}
  await p.waitForTimeout(2000);
  const r=await p.evaluate(()=>({blocks:[...document.querySelectorAll('main.page .block, main > section.block, footer section.block')].map(e=>Math.round(e.getBoundingClientRect().height)).filter(x=>x>2),
    overflow: document.documentElement.scrollWidth}));
  await ctx.close();return r;
}
for(const s of slugs){
  const live=await h('https://theoasisproject.eu/'+s);
  const mine=await h('http://127.0.0.1:4173/'+(s===''?'index':s)+'.html');
  const dl=live.blocks.reduce((a,c)=>a+c,0), dm=mine.blocks.reduce((a,c)=>a+c,0);
  console.log((s||'home').padEnd(24), 'live',live.blocks.length,dl,'w'+live.overflow,'| mine',mine.blocks.length,dm,'w'+mine.overflow);
}
await b.close();
