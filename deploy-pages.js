/**
 * deploy-pages.js — 干净部署 dist 到 GitHub Pages (gh-pages 分支)
 * 用法: node deploy-pages.js
 * 环境变量: GH_TOKEN (必填, GitHub PAT)
 */
const https = require('https')
const fs = require('fs')
const path = require('path')

const TOKEN = process.env.GH_TOKEN
const REPO = 'lixiu-ohye/customer-crawler'
const DIST = path.join(__dirname, 'frontend', 'dist')
const BRANCH = 'gh-pages'

if (!TOKEN) {
  console.error('✗ 缺少 GH_TOKEN 环境变量')
  process.exit(1)
}
if (!fs.existsSync(DIST)) {
  console.error('✗ dist 目录不存在:', DIST)
  process.exit(1)
}

function gh(method, url, body) {
  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        hostname: 'api.github.com',
        path: url,
        method,
        headers: {
          Authorization: `token ${TOKEN}`,
          'User-Agent': 'deploy-pages',
          Accept: 'application/vnd.github+json',
          'Content-Type': 'application/json',
        },
      },
      res => {
        let data = ''
        res.on('data', c => (data += c))
        res.on('end', () => {
          let json = null
          try { json = JSON.parse(data) } catch (e) { /* 非 JSON */ }
          resolve({ status: res.statusCode, json, raw: data })
        })
      }
    )
    req.on('error', reject)
    if (body !== undefined) req.write(JSON.stringify(body))
    req.end()
  })
}

// 收集 dist 文件 (相对路径 -> 绝对路径)
function collectFiles(dir, prefix = '') {
  const out = []
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name)
    const rel = prefix ? `${prefix}/${name}` : name
    const stat = fs.statSync(full)
    if (stat.isDirectory()) out.push(...collectFiles(full, rel))
    else {
      // real-data.json 由单独脚本用 Contents API 上传（大文件 Git Data API 会被网络层拦截 401）
      if (rel === 'real-data.json') {
        console.log('   跳过 real-data.json（用 Contents API 单独上传）')
        continue
      }
      out.push({ rel, full })
    }
  }
  return out
}

async function main() {
  console.log('=== 1. 读取 main 分支 HEAD ===')
  const head = await gh('GET', `/repos/${REPO}/git/ref/heads/main`)
  const mainSha = head.json.object.sha
  console.log('   main HEAD:', mainSha)

  console.log('=== 2. 获取/创建 gh-pages 分支 ===')
  let ghRef = await gh('GET', `/repos/${REPO}/git/ref/heads/${BRANCH}`)
  let parentSha = null
  if (ghRef.status === 200) {
    parentSha = ghRef.json.object.sha
    console.log('   已有 gh-pages:', parentSha)
  } else {
    const created = await gh('POST', `/repos/${REPO}/git/refs`, {
      ref: `refs/heads/${BRANCH}`,
      sha: mainSha,
    })
    if (created.status === 201) {
      parentSha = created.json.object.sha
      console.log('   创建 gh-pages:', parentSha)
    } else {
      console.error('   创建失败:', created.raw.slice(0, 300))
      process.exit(1)
    }
  }

  console.log('=== 3. 上传 dist 文件 blob ===')
  const files = collectFiles(DIST)
  console.log(`   ${files.length} 个文件`)
  const blobShas = {}
  for (const f of files) {
    const content = fs.readFileSync(f.full)
    const res = await gh('POST', `/repos/${REPO}/git/blobs`, {
      content: content.toString('base64'),
      encoding: 'base64',
    })
    if (res.status !== 201) {
      console.error('   blob 失败:', f.rel, res.raw.slice(0, 200))
      process.exit(1)
    }
    blobShas[f.rel] = res.json.sha
    console.log(`   ✓ ${f.rel}`)
  }

  console.log('=== 4. 构建 tree (干净: 无 base_tree) ===')
  const tree = files.map(f => ({ path: f.rel, mode: '100644', type: 'blob', sha: blobShas[f.rel] }))
  const treeRes = await gh('POST', `/repos/${REPO}/git/trees`, { tree })
  if (treeRes.status !== 201) {
    console.error('   tree 失败:', treeRes.raw.slice(0, 300))
    process.exit(1)
  }
  const treeSha = treeRes.json.sha
  console.log('   tree:', treeSha)

  console.log('=== 5. 创建 commit ===')
  const commitRes = await gh('POST', `/repos/${REPO}/git/commits`, {
    message: `deploy: ${new Date().toISOString()}`,
    tree: treeSha,
    parents: parentSha ? [parentSha] : [],
  })
  if (commitRes.status !== 201) {
    console.error('   commit 失败:', commitRes.raw.slice(0, 300))
    process.exit(1)
  }
  const commitSha = commitRes.json.sha
  console.log('   commit:', commitSha)

  console.log('=== 6. 更新 gh-pages ref ===')
  const refRes = await gh('PATCH', `/repos/${REPO}/git/refs/heads/${BRANCH}`, {
    sha: commitSha,
    force: true,
  })
  if (refRes.status !== 200) {
    console.error('   ref 更新失败:', refRes.raw.slice(0, 300))
    process.exit(1)
  }
  console.log('   gh-pages ->', commitSha)

  console.log('=== 7. 启用 Pages (409 already enabled 属预期) ===')
  const pages = await gh('POST', `/repos/${REPO}/pages`, { source: { branch: BRANCH, path: '/' } })
  console.log('   pages status:', pages.status)

  console.log('\n✓ 部署完成:', `https://lixiu-ohye.github.io/${REPO.split('/')[1]}/`)
}

main().catch(e => {
  console.error('✗ 部署失败:', e.message)
  process.exit(1)
})
