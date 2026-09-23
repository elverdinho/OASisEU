import {chromium} from 'playwright';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:1000}});
const p=await ctx.newPage();
await p.goto('http://127.0.0.1:4173/calls-for-artists-oasis',{waitUntil:'networkidle',timeout:60000});
await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}scrollTo(0,0);});
await p.waitForTimeout(800);
console.log('order:',JSON.stringify(await p.evaluate(()=>[...document.querySelectorAll('.call-card')].map(c=>{
  const t=c.textContent.replace(/\s+/g,' ').trim();const m=t.match(/(\d{2}\/\d{2}\/\d{4})/);
  return (m?m[1]:'??')+' '+c.dataset.country;}))));
// exercise the filter
await p.click('.chip[data-country="Portugal"]');
await p.waitForTimeout(400);
console.log('after Portugal filter:',await p.evaluate(()=>{
  const all=[...document.querySelectorAll('.call-card')];
  return {visible:all.filter(c=>!c.hidden).length,countries:[...new Set(all.filter(c=>!c.hidden).map(c=>c.dataset.country))],url:location.search};}));
const y=await p.evaluate(()=>document.querySelector('.call-filter').getBoundingClientRect().top+scrollY-40);
await p.click('.chip[data-country=""]');await p.waitForTimeout(500);
await p.evaluate(y=>scrollTo(0,y),y);await p.waitForTimeout(700);
await p.screenshot({path:'_shots/grid.png',clip:{x:0,y:0,width:1440,height:940}});
await b.close();
