// main.js — fetch chain-snatching data, render table, map and chart
const API = location.origin.replace(/\/templates.*|\/templates|\/templates\/.*/,'') || 'http://localhost:8000';
const token = () => localStorage.getItem('token');

async function fetchData(){
  const area = document.getElementById('filterArea').value || undefined;
  const sd = document.getElementById('startDate').value || undefined;
  const ed = document.getElementById('endDate').value || undefined;
  const q = new URLSearchParams(); if(area) q.set('area',area); if(sd) q.set('start_date',sd); if(ed) q.set('end_date',ed);
  const url = API + '/chain-snatching?' + q.toString();
  const res = await fetch(url, {headers:{'Authorization':'Bearer '+token()}});
  if(res.status===401){alert('Unauthorized — please login');location.href='/templates/login.html';return null}
  if(!res.ok){console.error('Fetch failed',res.status);return null}
  return await res.json();
}

function renderTable(results){
  const tbody = document.querySelector('#dataTable tbody'); tbody.innerHTML='';
  results.forEach(r=>{const tr=document.createElement('tr'); tr.innerHTML=`<td>${r.area}</td><td>${r.count}</td>`; tbody.appendChild(tr);});
}

function renderChart(results){
  const top = results.slice(0,5); const labels = top.map(r=>r.area); const data = top.map(r=>r.count);
  const ctx = document.getElementById('barChart').getContext('2d');
  if(window._bar) window._bar.destroy();
  window._bar = new Chart(ctx, {type:'bar',data:{labels, datasets:[{label:'Cases',data,backgroundColor:'#00d1b2'}]}, options:{plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#cfe8ea'}},y:{ticks:{color:'#cfe8ea'}}}});
}

let map, markers=[];
function initMap(){
  map = L.map('map').setView([12.97,77.59],12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:''}).addTo(map);
}

function renderMap(results){
  markers.forEach(m=>map.removeLayer(m)); markers=[];
  results.forEach(r=>{ if(!r.lat && !r.lng) return; const m=L.marker([r.lat,r.lng]).addTo(map).bindPopup(`<strong>${r.area}</strong><br/>Cases: ${r.count}`); markers.push(m);});
}

async function loadAndRender(){
  const data = await fetchData(); if(!data) return; renderTable(data.results); renderChart(data.results); renderMap(data.results);
}

const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) logoutBtn.addEventListener('click',()=>{localStorage.removeItem('token');location.href='/templates/login.html'});

document.addEventListener('DOMContentLoaded', ()=>{
  initMap(); const t=token(); if(!t){location.href='/templates/login.html';return} 
  const loadBtn = document.getElementById('loadBtn'); if(loadBtn) loadBtn.addEventListener('click', loadAndRender);
  loadAndRender();
});