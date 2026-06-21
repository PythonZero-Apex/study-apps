#!/usr/bin/env node
/* AZ-900 Power Platform Fundamentals — ロジック検証
 * 1) データ整合性(選択肢4個以上・正解インデックス妥当・single/multi・解説有無・重複)
 * 2) 選択肢シャッフル＋正解再マップが正しいか(テンプレと同じ buildSet を多数回試行)
 * 使い方: node verify_az900.js [path/to/az-900-questions.json]
 */
const fs = require('fs');
const path = require('path');

const file = process.argv[2] ||
  path.join(__dirname, '..', 'az900', 'az-900-questions.json');
const bank = JSON.parse(fs.readFileSync(file, 'utf8'));
const Q = bank.questions;

let errors = [];
function chk(cond, msg){ if(!cond) errors.push(msg); }

// ---- 1) 整合性 ----
const ids = new Set();
const norm = t => (t||'').replace(/\s+/g,'');
const seen = {};
for (const q of Q){
  const tag = `#${q.id} (${q.domain||q.area})`;
  chk(!ids.has(q.id), `${tag}: id重複`); ids.add(q.id);
  chk(Array.isArray(q.options) && q.options.length >= 4, `${tag}: 選択肢が4未満`);
  chk(new Set(q.options).size === q.options.length, `${tag}: 選択肢重複`);
  chk(['single','multi'].includes(q.type), `${tag}: type不正`);
  chk(Array.isArray(q.answer) && q.answer.length >= 1, `${tag}: answer空`);
  for (const a of q.answer) chk(a>=0 && a<q.options.length, `${tag}: answerインデックス範囲外(${a})`);
  chk(new Set(q.answer).size === q.answer.length, `${tag}: answer重複`);
  if (q.type==='single') chk(q.answer.length===1, `${tag}: singleなのに正解数${q.answer.length}`);
  if (q.type==='multi')  chk(q.answer.length>=2, `${tag}: multiなのに正解数${q.answer.length}`);
  chk(q.explanation && q.explanation.length>=20, `${tag}: 解説が短い/空`);
  const n = norm(q.q);
  if (seen[n]!==undefined) errors.push(`${tag}: 完全重複 with #${seen[n]}`);
  seen[n] = q.id;
}

// ---- 2) シャッフル＋再マップ検証(テンプレ buildSet と同一ロジック) ----
function shuffle(a){ for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; }
const TRIALS = 3000;
let remapFail = 0;
for (let t=0;t<TRIALS;t++){
  const q = Q[Math.floor(Math.random()*Q.length)];
  const idx = q.options.map((_,i)=>i);
  shuffle(idx);
  const options = idx.map(i=>q.options[i]);
  const answer = q.answer.map(a=>idx.indexOf(a)).sort((x,y)=>x-y);
  const after = new Set(answer.map(i=>options[i]));
  const before = new Set(q.answer.map(i=>q.options[i]));
  const same = after.size===before.size && [...before].every(x=>after.has(x));
  if(!same) remapFail++;
}
chk(remapFail===0, `シャッフル再マップ不整合: ${remapFail}/${TRIALS}`);

// ---- 集計 & 結果 ----
const multi = Q.filter(q=>q.type==='multi').length;
const dom = {};
for (const q of Q){ const d=q.domain||q.area; dom[d]=(dom[d]||0)+1; }
console.log(`問題数: ${Q.length} / multi: ${multi} (${(multi/Q.length*100).toFixed(1)}%)`);
Object.entries(dom).forEach(([d,n])=>console.log(`  - ${d}: ${n} (${(n/Q.length*100).toFixed(1)}%)`));
console.log(`シャッフル試行: ${TRIALS}（再マップ不整合 ${remapFail}）`);
if(errors.length){
  console.log(`\n‼ NG: ${errors.length}件`);
  errors.slice(0,50).forEach(e=>console.log('  - '+e));
  process.exit(1);
} else {
  console.log('\n✅ すべての検証に合格');
}
