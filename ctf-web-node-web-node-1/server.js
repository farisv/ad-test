'use strict';
const http = require('http');
const fs = require('fs');
const crypto = require('crypto');
const { exec } = require('child_process');
const DB = '/data/mergedesk.json';
let data = { users: [], items: [], nextId: 1 };
try { data = JSON.parse(fs.readFileSync(DB, 'utf8')); } catch (_) {}
const save = () => fs.writeFileSync(DB, JSON.stringify(data));
const json = (res, code, obj) => { res.writeHead(code, {'content-type':'application/json'}); res.end(JSON.stringify(obj)); };
const read = req => new Promise((resolve, reject) => { let s=''; req.on('data',d=>{s+=d;if(s.length>8192)req.destroy()}); req.on('end',()=>{try{resolve(s?JSON.parse(s):{})}catch(e){reject(e)}}); });
const hash = p => crypto.createHash('sha256').update(String(p)).digest('hex');
const current = req => { const token=(req.headers.authorization||'').replace(/^Bearer /,''); return data.users.find(u=>u.token===token&&token); };
const clean = s => String(s||'').replace(/[^A-Za-z0-9_]/g,'').slice(0,48);

// Intentionally vulnerable recursive merge: special object keys are not rejected.
function merge(target, source) { for (const key in source) { if (source[key] && typeof source[key]==='object') { if (!target[key]) target[key]={}; merge(target[key],source[key]); } else target[key]=source[key]; } return target; }
// Intentionally vulnerable document matcher: user input may supply query operators.
function matches(value, query) { if (query && typeof query==='object') { if ('$ne' in query) return value!==query.$ne; if ('$regex' in query) return new RegExp(query.$regex).test(value); } return value===query; }

async function route(req,res) {
  const url=new URL(req.url,'http://service');
  if(req.method==='GET'&&url.pathname==='/health') return json(res,200,{status:'ok'});
  if(req.method==='GET'&&url.pathname==='/') { res.writeHead(200,{'content-type':'text/plain'});return res.end('Merge Desk API\nregister, login, /api/items, /api/profile, /api/render\n'); }
  let b={}; if(req.method==='POST'||req.method==='PATCH') try{b=await read(req)}catch(_){return json(res,400,{error:'bad json'})}
  if(req.method==='POST'&&url.pathname==='/api/register') {
    const username=clean(b.username), password=String(b.password||''); if(username.length<3||password.length<6)return json(res,400,{error:'invalid registration'});
    if(data.users.some(u=>u.username===username))return json(res,409,{error:'exists'}); data.users.push({username,password:hash(password),token:'',profile:{theme:'light'}});save();return json(res,201,{status:'registered'});
  }
  if(req.method==='POST'&&url.pathname==='/api/login') {
    const user=data.users.find(u=>matches(u.username,b.username)&&matches(u.password,typeof b.password==='string'?hash(b.password):b.password));
    if(!user)return json(res,403,{error:'bad credentials'});user.token=crypto.randomBytes(24).toString('hex');save();return json(res,200,{token:user.token});
  }
  const user=current(req); if(!user)return json(res,401,{error:'authentication required'});
  if(req.method==='PATCH'&&url.pathname==='/api/profile') { merge(user.profile,b);save();return json(res,200,{profile:user.profile}); }
  if(req.method==='POST'&&url.pathname==='/api/items') { const title=String(b.title||'').slice(0,120),content=String(b.content||'');if(!title||content.length>4096)return json(res,400,{error:'invalid item'});const item={id:data.nextId++,owner:user.username,title,content};data.items.push(item);save();return json(res,201,{id:item.id}); }
  const m=url.pathname.match(/^\/api\/items\/(\d+)$/); if(req.method==='GET'&&m){const item=data.items.find(x=>x.id===+m[1]);if(!item)return json(res,404,{error:'not found'});if(item.owner!==user.username)return json(res,403,{error:'forbidden'});return json(res,200,item);}
  if(req.method==='GET'&&url.pathname==='/api/admin/items'){if(!user.profile.isAdmin)return json(res,403,{error:'admin only'});return json(res,200,data.items);}
  if(req.method==='POST'&&url.pathname==='/api/render') {
    // Intentionally vulnerable: an ostensibly cosmetic template is passed to a shell.
    const template=String(b.template||'');if(template.length>256)return json(res,400,{error:'too long'});
    exec("printf '"+template+"'",{timeout:1500,maxBuffer:4096},(err,stdout)=>json(res,err?400:200,{output:stdout,error:err?err.message:undefined}));return;
  }
  return json(res,404,{error:'not found'});
}
http.createServer((req,res)=>route(req,res).catch(e=>json(res,500,{error:e.message}))).listen(8083,'0.0.0.0');
