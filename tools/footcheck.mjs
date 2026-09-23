import {chromium} from 'playwright';
const b=await chromium.launch();
for(const [tag,url] of [['mine','http://127.0.0.1:4173/'],['live','https://theoasisproject.eu/']]){
  const ctx=await b.newContext({viewport:{width:1440,height:1000}});
  const p=await ctx.newPage();
  await p.goto(url,{waitUntil:'networkidle',timeout:60000});
  await p.evaluate(()=>scrollTo(0,document.body.scrollHeight));await p.waitForTimeout(2000);
  console.log(tag,JSON.stringify(await p.evaluate(()=>{
    const blocks=[...document.querySelectorAll('.block')];
    const f=blocks[blocks.length-1];
    const fb=f.getBoundingClientRect();
    const items=[...f.querySelectorAll('.el-text, [class*=layout-element]')].map(e=>{
      const bb=e.getBoundingClientRect();
      return {t:(e.textContent||'').trim().slice(0,34),top:Math.round(bb.top-fb.top),bot:Math.round(bb.bottom-fb.top)};
    }).filter(x=>x.t);
    return {blockH:Math.round(fb.height),docH:Math.round(document.body.scrollHeight),
            blockBottom:Math.round(fb.bottom+scrollY),items};
  }),null,1));
  await ctx.close();
}
await b.close();
