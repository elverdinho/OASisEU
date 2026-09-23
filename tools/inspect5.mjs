import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:1000}});
const p=await ctx.newPage();
await p.goto('https://theoasisproject.eu/about-us-oasis',{waitUntil:'networkidle',timeout:60000});
await p.waitForTimeout(3000);
console.log(JSON.stringify(await p.evaluate(()=>{
  const blocks=[...document.querySelectorAll('.block')];
  const blk=blocks.find(b=>b.querySelector('iframe'));
  const s=getComputedStyle(blk);const bb=blk.getBoundingClientRect();
  const kids=[...blk.children].map(c=>{const cb=c.getBoundingClientRect();const cs=getComputedStyle(c);
    return {cls:(c.className+'').slice(0,40),top:Math.round(cb.top+scrollY),h:Math.round(cb.height),pad:cs.padding,mh:cs.minHeight,pos:cs.position,disp:cs.display,gtr:cs.gridTemplateRows?.slice(0,60)};});
  return {block:{top:Math.round(bb.top+scrollY),h:Math.round(bb.height),pad:s.padding,mh:s.minHeight,disp:s.display},kids};
}),null,1));
await b.close();
