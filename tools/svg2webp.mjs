import {chromium} from 'playwright';
import fs from 'fs';
import path from 'path';
const dir='site/assets';
const big=fs.readdirSync(dir).filter(f=>f.endsWith('.svg'))
  .map(f=>({f,size:fs.statSync(path.join(dir,f)).size}))
  .filter(x=>x.size>400*1024);
const b=await chromium.launch();
for(const {f,size} of big){
  const ctx=await b.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1});
  const p=await ctx.newPage();
  await p.goto('file://'+path.resolve(dir,f),{waitUntil:'networkidle'});
  await p.waitForTimeout(400);
  const out=path.join(dir,f.replace(/\.svg$/,'.png'));
  await p.screenshot({path:out,clip:{x:0,y:0,width:1920,height:1080},omitBackground:true});
  console.log(f.slice(0,42),(size/1048576).toFixed(2)+'MB ->',(fs.statSync(out).size/1048576).toFixed(2)+'MB png');
  await ctx.close();
}
await b.close();
