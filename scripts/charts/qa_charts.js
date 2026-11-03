const fs = require('fs');
const html = fs.readFileSync('/home/claude/beatbombasement/index.html', 'utf8');
const core = html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const M = new Function(core + ';return {SIG,HEAD_HALF,HEAD_SPEED,DIFF};')();
let bad = 0;
for (const f of fs.readdirSync('web/charts').sort()){
  const c = JSON.parse(fs.readFileSync('web/charts/' + f)); const line = [f];
  for (const d of ['easy','normal','hard']){
    const reach = M.HEAD_HALF + M.SIG[d].half, wps = [];
    c.charts.signal[d].forEach(n => n.k === 't' ? wps.push({ t:n.t, x:n.x }) : n.p.forEach(p => wps.push({ t:p[0], x:p[1] })));
    wps.sort((a,b) => a.t - b.t);
    let px = 0.5, pt = wps[0].t - 3, fails = 0, overlap = 0, minGap = 9;
    for (let i = 0; i < wps.length; i++){ const w = wps[i]; px += Math.sign(w.x - px)*Math.min(Math.abs(w.x - px), M.HEAD_SPEED*(w.t - pt)); if (Math.abs(px - w.x) > reach + 1e-9) fails++; pt = w.t; }
    const taps = c.charts.signal[d].filter(n => n.k === 't');
    for (let i = 1; i < taps.length; i++) minGap = Math.min(minGap, taps[i].t - taps[i-1].t);
    // taps inside bands would be ambiguous
    const bands = c.charts.signal[d].filter(n => n.k === 'b');
    for (const t of taps) for (const b of bands) if (t.t > b.p[0][0] && t.t < b.p[b.p.length-1][0]) overlap++;
    const lanes = c.charts.lanes[d]; let jam = 0; for (let i = 1; i < lanes.length; i++) if (lanes[i].t - lanes[i-1].t < M.DIFF[d].gap - 0.001) jam++;
    bad += fails + overlap + jam + (minGap < M.SIG[d].gap - 0.031 ? 1 : 0);
    line.push(`${d}: unreachable ${fails}, hit-in-band ${overlap}, min gap ${(minGap*1000).toFixed(0)} ms, lanes gap violations ${jam}`);
  }
  console.log(line.join(' | '));
}
console.log(bad ? 'PROBLEMS: ' + bad : 'all charts pass');
