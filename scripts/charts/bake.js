// Bakes web/charts/NN.json for every supplied track using the game's own core.
const fs = require('fs');
const html = fs.readFileSync('/home/claude/beatbombasement/index.html', 'utf8');
const core = html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const M = new Function(core + ';return {analyzeMono,detectGrid,signalChart,chartFromOnsets,envPrint,SIG,HEAD_HALF,HEAD_SPEED};')();
const meta = JSON.parse(fs.readFileSync('/home/claude/bbb/report/meta.json'));
const r3 = v => Math.round(v*1000)/1000;
(async () => {
  fs.mkdirSync('/home/claude/bbb/web/charts', { recursive:true });
  const summary = [];
  for (const m of meta){
    const buf = fs.readFileSync(`/home/claude/bbb/pcm/${m.no}.f32`);
    const mono = new Float32Array(buf.buffer, buf.byteOffset, buf.length/4), sr = 22050, dur = mono.length/sr;
    const an = await M.analyzeMono(mono, sr);
    const grid = M.detectGrid(an, dur);
    const opt = { grid };
    const charts = { signal:{}, lanes:{} };
    for (const d of ['easy','normal','hard']){
      charts.signal[d] = M.signalChart(an, dur, d, opt).map(n => n.kind === 'tap' ? { k:'t', t:r3(n.t), x:r3(n.x) } : { k:'b', p:n.pts.map(p => [r3(p.t), r3(p.x)]) });
      charts.lanes[d] = M.chartFromOnsets(an.onsets, dur, d, opt).map(n => ({ t:r3(n.t), l:n.lane }));
    }
    // fingerprint from the 44.1 kHz decode, 10 s starting half a second after the music starts
    const b44 = fs.readFileSync(`/home/claude/bbb/pcm/${m.no}.44k.f32`), x44 = new Float32Array(b44.buffer, b44.byteOffset, b44.length/4);
    const from = Math.min(25, m.lead + 0.5), pr = M.envPrint(x44, 44100, from, 10);
    let mx = 0; for (const v of pr) mx = Math.max(mx, Math.sqrt(v));
    const q = Buffer.from(Array.from(pr, v => Math.round(255*Math.sqrt(v)/(mx || 1))));
    const out = { version:1, slot:+m.no, title:m.title, audio:m.audio, duration:r3(dur), gainDb:m.gainDb, lufs:m.lufs,
      grid:{ on:grid.on, bpm:+grid.bpm.toFixed(3), period:+grid.period.toFixed(6), phase:+grid.phase.toFixed(4), fit8:+grid.fit8.toFixed(3) },
      print:{ from:r3(from), len:10, bin:0.002, data:q.toString('base64') }, charts };
    fs.writeFileSync(`/home/claude/bbb/web/charts/${m.no}.json`, JSON.stringify(out));
    const sg = charts.signal;
    const row = { no:m.no, title:m.title, grid:grid.on ? grid.bpm + ' BPM' : 'free', fit8:+grid.fit8.toFixed(2) };
    for (const d of ['easy','normal','hard']){ const t = sg[d].filter(n => n.k === 't').length, b = sg[d].filter(n => n.k === 'b'); row[d] = `${t} hits ${(t/dur).toFixed(2)}/s · ${b.length} bands ${b.reduce((a,x) => a + x.p[x.p.length-1][0] - x.p[0][0], 0).toFixed(0)} s`; }
    summary.push(row); console.log(JSON.stringify(row));
  }
  fs.writeFileSync('/home/claude/bbb/report/summary.json', JSON.stringify(summary, null, 1));
})();
