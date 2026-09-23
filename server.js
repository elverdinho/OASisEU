#!/usr/bin/env node
/**
 * OASis - zero-dependency server.
 *   node server.js            -> http://localhost:4173
 * Serves site/ and accepts form submissions at POST /api/forms.
 * Submissions are appended to data/submissions.jsonl and, when RESEND_API_KEY
 * is set, forwarded by email to FORM_TO (default info@theoasisproject.eu).
 */
const http = require('http');
const fs   = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, 'site');
const DATA = path.join(__dirname, 'data');
const PORT = process.env.PORT || 4173;
const TO   = process.env.FORM_TO || 'info@theoasisproject.eu';
const FROM = process.env.FORM_FROM || 'OASis website <onboarding@resend.dev>';

const TYPES = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8',
  '.js':'text/javascript; charset=utf-8','.json':'application/json','.svg':'image/svg+xml',
  '.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp',
  '.gif':'image/gif','.ico':'image/x-icon','.mp4':'video/mp4','.woff2':'font/woff2',
  '.woff':'font/woff','.ttf':'font/ttf','.xml':'application/xml','.txt':'text/plain; charset=utf-8',
  '.PNG':'image/png','.JPG':'image/jpeg'};

fs.mkdirSync(DATA, {recursive:true});

async function sendMail(entry){
  if(!process.env.RESEND_API_KEY) return {skipped:'no RESEND_API_KEY'};
  const rows = Object.entries(entry.fields)
    .map(([k,v])=>`<tr><td style="padding:6px 12px;font-weight:600">${k}</td><td style="padding:6px 12px">${String(v).replace(/</g,'&lt;')}</td></tr>`).join('');
  const r = await fetch('https://api.resend.com/emails',{
    method:'POST',
    headers:{'Authorization':`Bearer ${process.env.RESEND_API_KEY}`,'Content-Type':'application/json'},
    body:JSON.stringify({from:FROM,to:[TO],subject:`OASis website - ${entry.form}`,
      html:`<h2>${entry.form}</h2><table>${rows}</table><p style="color:#888">${entry.at} - ${entry.page||''}</p>`})
  });
  return r.ok ? {sent:true} : {error:await r.text()};
}

const server = http.createServer(async (req,res)=>{
  if(req.method==='POST'){   // Netlify receives form posts on the page path itself
    let body='';
    req.on('data',c=>{body+=c; if(body.length>1e6) req.destroy();});
    req.on('end',async ()=>{
      let payload={};
      const ct=(req.headers['content-type']||'');
      try{
        if(ct.includes('application/json')) payload=JSON.parse(body||'{}');
        else payload=Object.fromEntries(new URLSearchParams(body));
      }catch(e){
        res.writeHead(400,{'Content-Type':'application/json'});
        return res.end(JSON.stringify({error:'bad payload'}));
      }
      const {_form, _page, 'form-name':formName, 'bot-field':bot, ...fields}=payload;
      if(bot){ res.writeHead(200,{'Content-Type':'application/json'}); return res.end('{"ok":true}'); }
      if(!Object.keys(fields).length){
        res.writeHead(400,{'Content-Type':'application/json'});
        return res.end(JSON.stringify({error:'empty submission'}));
      }
      const entry={at:new Date().toISOString(), form:formName||_form||'unknown', page:_page||req.url||'',
                   ip:req.socket.remoteAddress, fields};
      fs.appendFileSync(path.join(DATA,'submissions.jsonl'), JSON.stringify(entry)+'\n');
      let mail={};
      try{ mail=await sendMail(entry); }catch(e){ mail={error:String(e)}; }
      console.log('[form]', entry.form, Object.keys(fields).join(','), JSON.stringify(mail));
      res.writeHead(200,{'Content-Type':'application/json'});
      res.end(JSON.stringify({ok:true}));
    });
    return;
  }

  let p = decodeURIComponent((req.url||'/').split('?')[0]);
  if(p==='/') p='/index.html';
  if(!path.extname(p)) p += '.html';                 // /news -> /news.html
  const file = path.join(ROOT, path.normalize(p).replace(/^(\.\.[/\\])+/,''));
  if(!file.startsWith(ROOT)){ res.writeHead(403); return res.end('forbidden'); }
  fs.readFile(file,(err,buf)=>{
    if(err){
      res.writeHead(404,{'Content-Type':'text/html; charset=utf-8'});
      return res.end('<h1>404</h1><p><a href="/">Back to the OASis home page</a></p>');
    }
    const st = fs.statSync(file);
    const isAsset = /\.(png|jpg|jpeg|webp|svg|mp4|woff2?)$/i.test(file);
    res.writeHead(200,{'Content-Type':TYPES[path.extname(file)]||'application/octet-stream',
                       'Content-Length': st.size,
                       'Last-Modified': st.mtime.toUTCString(),
                       'ETag': '"'+st.size.toString(16)+'-'+st.mtimeMs.toString(36)+'"',
                       // pages and styles must never be served from a stale cache while editing
                       'Cache-Control': isAsset
                         ? 'public, max-age=31536000, immutable'
                         : 'no-store, no-cache, must-revalidate, max-age=0'});
    res.end(buf);
  });
});

server.listen(PORT, ()=>console.log(`OASis running on http://localhost:${PORT}`));
