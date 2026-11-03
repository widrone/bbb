// Runs the game's own analysis core over decoded mono PCM (22.05 kHz f32) for each track.
const fs = require('fs');
const html = fs.readFileSync('/home/claude/beatbombasement/index.html', 'utf8');
const core = html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const M = new Function(core + ';return {analyzeMono,tempoOf,gridFit,signalChart,chartFromOnsets,pickOnsets,SIG,DIFF};')();
(async () => {
  const out = {};
  for (const n of process.argv.slice(2)){
    const buf = fs.readFileSync(`/home/claude/bbb/pcm/${n}.f32`);
    const mono = new Float32Array(buf.buffer, buf.byteOffset, buf.length/4);
    const sr = 22050, dur = mono.length/sr;
    const an = await M.analyzeMono(mono, sr);
    const g = M.tempoOf(an.env, an.fps, an.envT0);
    // tempo stability: best phase per 30 s window vs global phase
    const fit16 = M.gridFit(an.onsets, g, 4, 0.03), fit8 = M.gridFit(an.onsets, g, 2, 0.03);
    const res = { n, dur:+dur.toFixed(2), onsets:an.onsets.length, onsetRate:+(an.onsets.length/dur).toFixed(2),
      bpm:+g.bpm.toFixed(2), conf:+g.conf.toFixed(2), phase:+g.phase.toFixed(3), fit16:+fit16.toFixed(2), fit8:+fit8.toFixed(2) };
    for (const d of ['easy','normal','hard']){
      const c = M.signalChart(an, dur, d);
      const taps = c.filter(x => x.kind === 'tap'), bands = c.filter(x => x.kind === 'band');
      res['sig_'+d] = `${taps.length} hits, ${bands.length} bands (${bands.reduce((a,b) => a + b.t1 - b.t, 0).toFixed(0)} s)`;
    }
    out[n] = { res, env:Array.from(an.env, v => +v.toFixed(3)), fps:an.fps, cen:Array.from(an.cen, v => +v.toFixed(3)), rms:Array.from(an.rms, v => +v.toFixed(4)), rmsQuiet:an.rmsQuiet,
      onsets:an.onsets.map(o => ({ t:+o.t.toFixed(4), s:+o.s.toFixed(3), x:+o.x.toFixed(3) })), grid:g,
      normal:M.signalChart(an, dur, 'normal') };
    console.log(JSON.stringify(res));
  }
  fs.writeFileSync('/home/claude/bbb/report/analysis.json', JSON.stringify(out));
})();
