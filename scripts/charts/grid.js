const fs = require('fs');
const html = fs.readFileSync('/home/claude/beatbombasement/index.html', 'utf8');
const core = html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const M = new Function(core + ';return {refineGrid,gridFit};')();
const A = JSON.parse(fs.readFileSync('/home/claude/bbb/report/analysis.json'));
const out = {};
for (const n of Object.keys(A)){
  const a = A[n], g = M.refineGrid(a.onsets, a.grid);
  const step8 = g.period/2, chance8 = Math.min(1, 0.06/step8);
  const fit8 = M.gridFit(a.onsets, g, 2, 0.03);
  // drift check: refine each 40 s window on its own and compare tempo + phase to the global grid
  const wins = [];
  for (let t = 0; t + 30 < a.res.dur; t += 40){
    const w = M.refineGrid(a.onsets, g, t, t + 40);
    const dph = ((w.phase - g.phase) % step8 + 1.5*step8) % step8 - step8/2;
    wins.push(`${w.bpm.toFixed(2)}/${(dph*1000).toFixed(0)}ms`);
  }
  out[n] = { bpm:+g.bpm.toFixed(3), phase:+g.phase.toFixed(4), period:g.period, fit:+g.fit.toFixed(3), fit8:+fit8.toFixed(2), chance8:+chance8.toFixed(2) };
  console.log(n, 'bpm', g.bpm.toFixed(3), 'fit8', fit8.toFixed(2), '(chance', chance8.toFixed(2)+')', 'windows', wins.join('  '));
}
fs.writeFileSync('/home/claude/bbb/report/grid.json', JSON.stringify(out, null, 1));
