#!/usr/bin/env node
/* 公害大気3種 — ロジック検証
 * 1) データ整合性(選択肢5個・正解インデックス妥当・single/multi・解説有無・重複)
 * 2) 選択肢シャッフル＋正解再マップが正しいか(テンプレと同じ buildSet を多数回試行)
 * 使い方: node verify.js [path/to/komu-3-air-questions.json]
 */
const fs = require('fs');
const path = require('path');

const file = process.argv[2] ||
  path.join(__dirname, '..', 'komu3', 'komu-3-air-questions.json');
const bank = JSON.parse(fs.readFileSync(file, 'utf8'));
const Q = bank.questions;

let errors = [];
function chk(cond, msg){ if(!cond) errors.push(msg); }

// ---- 1) 整合性 ----
const ids = new Set();
for (const q of Q){
  const tag = `#${q.id} (${q.domain})`;
  chk(!ids.has(q.id), `${tag}: id重複`); ids.add(q.id);
  chk(Array.isArray(q.options) && q.options.length === 5, `${tag}: 選択肢が5個でない`);
  chk(new Set(q.options).size === q.options.length, `${tag}: 選択肢重複`);
  chk(['single','multi'].includes(q.type), `${tag}: type不正`);
  chk(Array.isArray(q.answer) && q.answer.length >= 1, `${tag}: answer空`);
  for (const a of q.answer) chk(a>=0 && a<q.options.length, `${tag}: answerインデックス範囲外(${a})`);
  chk(new Set(q.answer).size === q.answer.length, `${tag}: answer重複`);
  if (q.type==='single') chk(q.answer.length===1, `${tag}: singleなのに正解数${q.answer.length}`);
  if (q.type==='multi')  chk(q.answer.length>=2, `${tag}: multiなのに正解数${q.answer.length}`);
  chk(q.explanation && q.explanation.length>=20, `${tag}: 解説が短い/空`);
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
  // 再マップ後の正解テキスト集合 が 元の正解テキスト集合 と一致するか
  const after = new Set(answer.map(i=>options[i]));
  const before = new Set(q.answer.map(i=>q.options[i]));
  const same = after.size===before.size && [...before].every(x=>after.has(x));
  if(!same) remapFail++;
}
chk(remapFail===0, `シャッフル再マップ不整合: ${remapFail}/${TRIALS}`);

// ---- 結果 ----
console.log(`問題数: ${Q.length} / multi: ${Q.filter(q=>q.type==='multi').length}`);
console.log(`シャッフル試行: ${TRIALS}（再マップ不整合 ${remapFail}）`);
if(errors.length){
  console.log(`\n‼ NG: ${errors.length}件`);
  errors.slice(0,50).forEach(e=>console.log('  - '+e));
  process.exit(1);
} else {
  console.log('\n✅ すべての検証に合格');
}
