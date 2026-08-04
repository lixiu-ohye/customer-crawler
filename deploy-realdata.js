// deploy-realdata.js — 用 Contents API 上传 real-data.json 到 gh-pages（大文件专用）
const fs = require('fs');
const TOKEN = process.env.GH_TOKEN;
const REPO = 'lixiu-ohye/customer-crawler';
const BRANCH = 'gh-pages';
const REL = 'real-data.json';
const LOCAL = require('path').join(__dirname, 'frontend', 'dist', 'real-data.json');
const BASE = 'https://api.github.com/repos/' + REPO;

if (!TOKEN) { console.error('✗ 缺少 GH_TOKEN'); process.exit(1); }

async function gh(method, url, body) {
  const r = await fetch(BASE + url, {
    method,
    headers: { Authorization: `token ${TOKEN}`, 'User-Agent': 'deploy-realdata', 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  let j = null;
  try { j = await r.json(); } catch (e) {}
  return { status: r.status, json: j };
}

(async () => {
  if (!fs.existsSync(LOCAL)) { console.error('✗ 文件不存在:', LOCAL); process.exit(1); }
  const content = fs.readFileSync(LOCAL, 'utf-8');
  const bytes = Buffer.byteLength(content);
  console.log(`real-data.json: ${(bytes / 1024 / 1024).toFixed(2)} MB`);
  if (bytes > 5 * 1024 * 1024) {
    console.error('✗ 超过 5MB 阈值，Contents API 可能 401，请先精简'); process.exit(1);
  }
  let sha = null;
  try {
    const r = await gh('GET', `/contents/${REL}?ref=${BRANCH}`);
    if (r.status === 200) sha = r.json.sha;
  } catch (e) {}
  console.log('existing sha:', sha || '(none)');
  const body = {
    message: `update real-data.json (${bytes} bytes) ${new Date().toISOString()}`,
    content: Buffer.from(content, 'utf-8').toString('base64'),
    sha: sha || undefined,
    branch: BRANCH,
  };
  const r = await gh('PUT', `/contents/${REL}`, body);
  console.log('PUT:', r.status);
  if (r.status !== 200 && r.status !== 201) {
    console.error('resp:', JSON.stringify(r.json).slice(0, 300));
    process.exit(1);
  }
  console.log('✓ real-data.json 已上传（sha', r.json.content.sha.slice(0, 7) + '）');
})().catch(e => { console.error('✗ ERR:', e.message); process.exit(1); });
