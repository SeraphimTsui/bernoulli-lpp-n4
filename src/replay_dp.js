'use strict';
// Independent replay: no bitmask path scores and no imported main-counting logic.
// Bit indices label random vertices only. Path scores are sums of grid entries.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const args = process.argv.slice(2);
const n = Number(args[0] || 4);
const limitArg = args[1] === undefined ? null : Number(args[1]);
if (!Number.isInteger(n) || n < 1 || n > 4) throw new Error('Hard scope is 1 <= n <= 4.');
const width = n + 1, gridSize = width * width, m = gridSize - 2;
const total = 2 ** m;
const limit = limitArg === null ? total : Math.min(total, limitArg);
if (!Number.isInteger(limit) || limit < 1) throw new Error('Invalid limit.');
const words = [], paths = [];
function walk(x, y, word, vertices) {
  if (x === n && y === n) { words.push(word); paths.push(vertices.slice(0, -1)); return; }
  if (x < n) walk(x + 1, y, word + 'R', vertices.concat(y * width + x + 1));
  if (y < n) walk(x, y + 1, word + 'U', vertices.concat((y + 1) * width + x));
}
walk(0, 0, '', []);
const pathLength = 2 * n - 1;
if (paths.some(p => p.length !== pathLength)) throw new Error('Wrong path length.');
const flat = Uint8Array.from(paths.flat());
const counts = new Uint32Array(words.length * (m + 1));
const layers = new Uint32Array(m + 1);
const weights = new Uint8Array(gridSize);
const dp = new Uint8Array(gridSize);
const started = new Date().toISOString();
const cpuStart = process.cpuUsage();
const timeStart = performance.now();
let uniqueConfigurations = 0, allTiedConfigurations = 0;
const tieHistogram = new Uint32Array(words.length + 1);
for (let configuration = 0; configuration < limit; configuration++) {
  let k = 0;
  // Every nonendpoint cell occurs in row-major order, hence its grid index is bit+1.
  for (let b = 0; b < m; b++) {
    const bit = (configuration >>> b) & 1;
    weights[b + 1] = bit;
    k += bit;
  }
  layers[k]++;
  // Global maximizing weight by the elementary lattice Bellman recurrence.
  dp[0] = 0;
  for (let x = 1; x <= n; x++) dp[x] = weights[x] + dp[x - 1];
  for (let y = 1; y <= n; y++) {
    const row = y * width;
    dp[row] = weights[row] + dp[row - width];
    for (let x = 1; x <= n; x++) {
      const v = row + x;
      dp[v] = weights[v] + Math.max(dp[v - 1], dp[v - width]);
    }
  }
  const maximum = dp[gridSize - 1];
  let tied = 0;
  for (let j = 0, offset = 0; j < words.length; j++, offset += pathLength) {
    let value = 0;
    for (let t = 0; t < pathLength; t++) value += weights[flat[offset + t]];
    if (value === maximum) { counts[j * (m + 1) + k]++; tied++; }
    if (value > maximum) throw new Error('A path exceeds the DP optimum.');
  }
  if (tied === 0) throw new Error('No maximizing path.');
  tieHistogram[tied]++;
  if (tied === 1) uniqueConfigurations++;
  if (tied === words.length) allTiedConfigurations++;
}
const wallSeconds = (performance.now() - timeStart) / 1000;
const used = process.cpuUsage(cpuStart);
const cpuSeconds = (used.user + used.system) / 1e6;
const rows = Object.fromEntries(words.map((word, j) => [word, Array.from(counts.slice(j * (m + 1), (j + 1) * (m + 1)))]));
function binomial(a, b) { let v = 1; for (let i = 1; i <= b; i++) v = v * (a - i + 1) / i; return Math.round(v); }
const complete = limit === total;
const checks = { complete, every_configuration_has_geodesic: true, no_path_exceeds_dp_optimum: true,
  layer_total: Array.from(layers).reduce((a, b) => a + b, 0) === limit,
  binomial_layers: complete ? Array.from(layers).every((v, k) => v === binomial(m, k)) : null,
  coefficient_bounds: Object.values(rows).every(row => row.every((v, k) => v <= binomial(m, k))),
  endpoint_columns: complete ? Object.values(rows).every(row => row[0] === 1 && row[m] === 1) : null,
  diagonal_reflection: complete ? words.every(word => JSON.stringify(rows[word]) === JSON.stringify(rows[word.replace(/[RU]/g, c => c === 'R' ? 'U' : 'R')])) : null,
  central_reversal: complete ? words.every(word => JSON.stringify(rows[word]) === JSON.stringify(rows[[...word].reverse().join('')])) : null,
  n1_hand_result: n === 1 && complete ? Object.values(rows).every(row => JSON.stringify(row) === '[1,1,1]') : null };
if (Object.entries(checks).some(([name, value]) => name !== 'complete' && value === false)) throw new Error('Independent replay invariant failed.');
const result = { schema_version: 1, implementation: 'independent lattice DP optimum plus direct grid-entry sums for every path',
  n, vertices: gridSize, free_vertices: m, endpoint_weights: 0, path_count: words.length,
  free_vertex_order: 'row-major y then x, omitting (0,0) and (n,n)',
  path_order: 'lexicographic R < U', all_ties_counted: true,
  start_mask: 0, stop_mask_exclusive: limit, full_configuration_count: total,
  started_utc: started, completed_utc: new Date().toISOString(), wall_seconds: wallSeconds,
  cpu_seconds: cpuSeconds, peak_rss_bytes: process.resourceUsage().maxRSS * 1024,
  node_version: process.version, script_sha256: crypto.createHash('sha256').update(fs.readFileSync(__filename)).digest('hex'),
  checks, layers: Array.from(layers), unique_configurations: uniqueConfigurations,
  all_tied_configurations: allTiedConfigurations, tie_histogram: Array.from(tieHistogram), counts: rows };
const output = path.resolve(__dirname, '..', 'results', `replay_n${n}${complete ? '' : '_benchmark'}.json`);
fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ output, n, complete, configurations: limit, paths: words.length, wall_seconds: wallSeconds, cpu_seconds: cpuSeconds, checks }));
