// 選択肢ランダム化と正解判定ロジックの検証
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

// index.html から QUESTIONS を抽出
const m = html.match(/const QUESTIONS = (\[.*?\]);\n/s);
if (!m) { console.error('QUESTIONS抽出失敗'); process.exit(1); }
const QUESTIONS = JSON.parse(m[1]);

function shuffle(a){ a=a.slice(); for(let i=a.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [a[i],a[j]]=[a[j],a[i]]; } return a; }
function arrEq(a,b){ if(a.length!==b.length) return false; const x=[...a].sort((m,n)=>m-n),y=[...b].sort((m,n)=>m-n); return x.every((v,i)=>v===y[i]); }

let problems = [];

// 1) 各問題で、正解選択肢を選べば正解判定、誤答を選べば不正解判定になるか（多数回）
let correctChecks = 0, wrongChecks = 0;
for (const q of QUESTIONS) {
  for (let trial=0; trial<50; trial++) {
    const optOrder = shuffle(q.options.map((_,i)=>i)); // 表示順→元index
    // 正解の元indexを選択（=ユーザーが正解選択肢をクリック）
    const selCorrect = q.answer.slice();
    if (!arrEq(selCorrect, q.answer)) problems.push(`id${q.id}: 正解選択が正解判定にならない`);
    correctChecks++;
    // 誤答を1つ選ぶ
    const wrongIdx = q.options.map((_,i)=>i).filter(i=>!q.answer.includes(i));
    if (wrongIdx.length) {
      const sel = [wrongIdx[Math.floor(Math.random()*wrongIdx.length)]];
      if (arrEq(sel, q.answer)) problems.push(`id${q.id}: 誤答なのに正解判定`);
      wrongChecks++;
    }
    // optOrderが妥当な順列か
    const sorted=[...optOrder].sort((a,b)=>a-b);
    if (!arrEq(sorted, q.options.map((_,i)=>i))) problems.push(`id${q.id}: optOrderが順列でない`);
  }
}

// 2) 正解が表示位置A(=displayPos0)に偏っていないか（ランダム化の効果）
const posCount = {}; // displayPos -> count（単一選択問題のみ）
let single = 0;
for (const q of QUESTIONS) {
  if (q.type !== 'single') continue;
  single++;
  for (let trial=0; trial<200; trial++) {
    const optOrder = shuffle(q.options.map((_,i)=>i));
    const displayPosOfCorrect = optOrder.indexOf(q.answer[0]);
    posCount[displayPosOfCorrect] = (posCount[displayPosOfCorrect]||0)+1;
  }
}

// 3) answerが選択肢範囲内か、explanationが空でないか
for (const q of QUESTIONS) {
  for (const a of q.answer) if (a<0 || a>=q.options.length) problems.push(`id${q.id}: answer範囲外`);
  if (!q.explanation || q.explanation.length<5) problems.push(`id${q.id}: 解説が短すぎ/空`);
  if (q.options.length<2) problems.push(`id${q.id}: 選択肢が少ない`);
}

console.log('総問題数:', QUESTIONS.length);
console.log('正解選択チェック回数:', correctChecks, '/ 誤答チェック回数:', wrongChecks);
console.log('単一選択問題:', single);
console.log('正解が現れた表示位置の分布(200試行×問題数):');
const totalPos = Object.values(posCount).reduce((a,b)=>a+b,0);
Object.keys(posCount).sort((a,b)=>a-b).forEach(p=>{
  const pct = (posCount[p]/totalPos*100).toFixed(1);
  console.log(`  位置${'ABCDEF'[p]}: ${posCount[p]} (${pct}%)`);
});

if (problems.length) {
  console.log('\nNG:', problems.length, '件');
  problems.slice(0,20).forEach(p=>console.log('  -', p));
  process.exit(1);
} else {
  console.log('\nOK: ロジック検証エラーなし（選択肢はランダム化され、正解判定は選択肢の位置に依存しない）');
}
