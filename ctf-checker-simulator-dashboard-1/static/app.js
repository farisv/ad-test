'use strict';
const cards=document.querySelector('#cards'),history=document.querySelector('#history'),run=document.querySelector('#run');
const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let last={};
function badge(ok,a,b){return `<span class="state ${ok?a:b}">${ok?a.toUpperCase():b.toUpperCase()}</span>`}
function render(data){
 document.querySelector('#target').textContent=`Target ${data.target}`;
 document.querySelector('#clock').textContent=`Every ${data.interval}s · next in ${data.runtime.next_run_in??'…'}s`;
 const rt=document.querySelector('#runtime');rt.className='pill '+(data.runtime.running?'running':'');rt.innerHTML=`<span class="dot"></span>${data.runtime.running?'Tick running':'Scheduler active'}`;run.disabled=data.runtime.running;
 const newest=data.ticks[0]?.results||[];last=Object.fromEntries(newest.map(x=>[x.service,x]));cards.innerHTML='';
 for(const [id,meta] of Object.entries(data.services)){const r=last[id];const el=document.createElement('article');el.className='card';el.innerHTML=`<h2>${safe(meta.name)}</h2><div class="kind">${safe(id)} · :${meta.port} · ${safe(meta.attack)}</div><div class="states">${r?badge(r.sla_ok,'up','down'):badge(false,'up','unknown')}${r?badge(!r.steal_ok,'blocked','stolen'):badge(false,'blocked','unknown')}</div>`;cards.append(el)}
 if(!data.ticks.length)return;history.innerHTML='';
 for(const tick of data.ticks){const results=tick.results||[],up=results.filter(r=>r.sla_ok).length,stolen=results.filter(r=>r.steal_ok).length,errors=results.filter(r=>r.sla_error||r.steal_error).map(r=>`${r.service}: ${r.sla_error||''}${r.sla_error&&r.steal_error?' | ':''}${r.steal_error||''}`).join('\n');const tr=document.createElement('tr');tr.innerHTML=`<td>#${tick.id}</td><td>${safe(tick.started_at)}</td><td>${tick.duration_ms==null?'running':tick.duration_ms+' ms'}</td><td>${up}/${Object.keys(data.services).length} UP</td><td>${stolen}/${Object.keys(data.services).length}</td><td>${results.reduce((n,r)=>n+(r.stolen_flags||[]).length,0)} flags</td>`;history.append(tr);const groups=results.map(r=>`<div class="flaggroup"><strong>${safe(data.services[r.service]?.name||r.service)} · ${r.stolen_count} stolen</strong><div class="flags">${(r.stolen_flags||[]).length?(r.stolen_flags||[]).map(f=>`<code>${safe(f)}</code>`).join(''):'<span>None</span>'}</div></div>`).join('');const d=document.createElement('tr');d.className='details';d.innerHTML=`<td colspan="6">${groups}${errors?`<div class="error">${safe(errors)}</div>`:''}</td>`;history.append(d)}
}
async function refresh(){try{const r=await fetch('/api/status',{cache:'no-store'});render(await r.json())}catch(e){document.querySelector('#runtime').textContent='Dashboard API unavailable'}}
run.onclick=async()=>{run.disabled=true;await fetch('/api/run',{method:'POST'});setTimeout(refresh,300)};
refresh();setInterval(refresh,3000);
