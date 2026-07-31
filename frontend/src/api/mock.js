// 演示数据层：GitHub Pages 静态环境无后端 API，用 Mock 数据让全站可演示
// 数据结构与 Django 后端 API 完全一致

const NOW = Date.now()
const daysAgo = n => {
  const d = new Date(NOW - n * 86400000)
  return d.toISOString().replace('T', ' ').slice(0, 19)
}

// ---------- 演示线索数据 ----------
const LEADS = [
  { id: 1, platform: 'weibo', title: '成都装修求推荐！刚拿到新房钥匙，140平想找靠谱的全屋定制公司', author: '蓉城新居', content: '刚在成都高新区拿到新房，140平，想找靠谱的全屋定制公司，环保板材优先，预算30万以内。有装过的朋友推荐一下吗？', summary: '成都高新区新房140平，求全屋定制公司推荐，环保板材优先，预算30万', region: '成都', demand: '全屋定制', intent_score: 86, intent_label: 'high', url: 'https://weibo.com', like_count: 12, comment_count: 8, share_count: 3, note: '', status: 'new', is_blacklisted: false, created_at: daysAgo(0) },
  { id: 2, platform: 'xiaohongshu', title: '旧房改造日记｜老破小变身奶油风，附改造清单', author: '小鹿装修记', content: '坐标广州，30年老破小改造完成！拆改、水电、全屋定制一站式搞定，总花费18万。分享我的改造清单和避坑指南，装修公司对比了好几家。', summary: '广州老破小改造完成，分享改造清单和装修公司对比经验', region: '广州', demand: '旧房改造', intent_score: 74, intent_label: 'high', url: 'https://www.xiaohongshu.com', like_count: 342, comment_count: 56, share_count: 21, note: '', status: 'new', is_blacklisted: false, created_at: daysAgo(0) },
  { id: 3, platform: 'douyin', title: '上海办公室装修，300平创意园区，求设计公司', author: '沪上创业人', content: '公司新租了300平的创意园区办公室，想找上海本地的办公室装修设计公司，现代简约风，工期45天左右，有推荐的吗？预算80万。', summary: '上海300平办公室装修需求，求本地设计公司', region: '上海', demand: '办公室装修', intent_score: 91, intent_label: 'high', url: 'https://www.douyin.com', like_count: 3, comment_count: 5, share_count: 1, note: '', status: 'new', is_blacklisted: false, created_at: daysAgo(1) },
  { id: 4, platform: 'zhihu', title: '全屋定制和木工现场打柜子到底哪个好？', author: '家居老司机', content: '准备装修了，全屋定制和木工现场打柜子纠结中。定制贵但好看，木工便宜但怕手艺不行。有没有过来人说说？坐标杭州。', summary: '杭州业主纠结全屋定制与木工打柜，寻求建议', region: '杭州', demand: '全屋定制', intent_score: 58, intent_label: 'medium', url: 'https://www.zhihu.com', like_count: 45, comment_count: 89, share_count: 12, note: '', status: 'new', is_blacklisted: false, created_at: daysAgo(1) },
  { id: 5, platform: 'tieba', title: '农村自建房装修，两层小楼，怎么省钱又好看？', author: '回乡建房的阿伟', content: '老家两层自建房准备装修，预算20万以内，湖南岳阳。想要现代简约风，本地装修公司靠谱吗？求推荐岳阳本地的装修队。', summary: '湖南岳阳自建房装修，预算20万求本地装修队', region: '岳阳', demand: '家装', intent_score: 62, intent_label: 'medium', url: 'https://tieba.baidu.com', like_count: 8, comment_count: 15, share_count: 2, note: '', status: 'new', is_blacklisted: false, created_at: daysAgo(2) },
  { id: 6, platform: 'weibo', title: '避雷！某装修公司收了定金跑路了，大家擦亮眼睛', author: '装修维权中', content: '曝光！XX装修公司收了3万定金后失联，还在多个平台接单。大家找装修公司一定要看资质！血泪教训，千万不要贪便宜。', summary: '曝光装修公司跑路，警示找装修公司要看资质', region: '未知地域', demand: '其他', intent_score: 15, intent_label: 'low', url: 'https://weibo.com', like_count: 567, comment_count: 210, share_count: 88, note: '', status: 'new', is_blacklisted: false, created_at: daysAgo(2) },
  { id: 7, platform: 'xiaohongshu', title: '深圳小户型装修灵感｜60平两房爆改三房', author: '深漂小窝', content: '深圳60平小户型改造案例，两房改三房，全屋收纳设计，装修花了15万。设计师是深圳本地的，全程跟进很负责，推荐！', summary: '深圳60平小户型改造案例分享，含本地设计师推荐', region: '深圳', demand: '家装', intent_score: 68, intent_label: 'medium', url: 'https://www.xiaohongshu.com', like_count: 289, comment_count: 43, share_count: 17, note: '', status: 'new', is_blacklisted: false, created_at: daysAgo(3) },
  { id: 8, platform: 'douyin', title: '北京办公室装修完工实拍｜500平科技公司', author: '工装设计师老王', content: '刚完工的北京500平科技公司办公室，现代科技风，工期40天。灯光和隔断是亮点，报价明细可以私信看。', summary: '北京500平办公室装修完工实拍', region: '北京', demand: '办公室装修', intent_score: 43, intent_label: 'medium', url: 'https://www.douyin.com', like_count: 156, comment_count: 28, share_count: 9, note: '', status: 'new', is_blacklisted: false, created_at: daysAgo(3) },
  { id: 9, platform: 'zhihu', title: '装修公司报价单怎么看？有哪些坑要注意？', author: '装修过来人', content: '收到三份装修报价单，价格差了一倍多。全包半包怎么选？增项一般会加多少？坐标南京，求指点。', summary: '南京业主咨询装修报价单鉴别与避坑', region: '南京', demand: '家装', intent_score: 51, intent_label: 'medium', url: 'https://www.zhihu.com', like_count: 23, comment_count: 67, share_count: 5, note: '', status: 'new', is_blacklisted: false, created_at: daysAgo(4) },
  { id: 10, platform: 'tieba', title: '成都装修公司前十名是哪几家？靠谱吗？', author: '贴吧老铁', content: '准备装修了，网上看到各种成都装修公司排名，也不知道真假。有没有成都本地的吧友说下哪家靠谱？半包还是全包？', summary: '成都业主求装修公司推荐，咨询半包全包选择', region: '成都', demand: '家装', intent_score: 66, intent_label: 'medium', url: 'https://tieba.baidu.com', like_count: 5, comment_count: 32, share_count: 1, note: '', status: 'new', is_blacklisted: false, created_at: daysAgo(5) },
  { id: 11, platform: 'kuaishou', title: '老铁们，村里翻新房，墙面粉刷师傅有推荐吗？', author: '快手老张', content: '河南周口农村，家里翻新房，需要粉刷墙面和铺地砖，想找本地的师傅，价格实惠点。', summary: '河南周口翻新房找本地施工师傅', region: '周口', demand: '翻新', intent_score: 47, intent_label: 'medium', url: 'https://www.kuaishou.com', like_count: 2, comment_count: 6, share_count: 0, note: '', status: 'new', is_blacklisted: false, created_at: daysAgo(6) },
  { id: 12, platform: 'kuaishou', title: '分享个装修小技巧，瓷砖美缝这样做省钱又好看', author: '装修达人小王', content: '美缝剂选色、施工步骤分享，自己动手省了2000块。装修干货持续更新。', summary: '装修美缝技巧分享', region: '未知地域', demand: '其他', intent_score: 22, intent_label: 'low', url: 'https://www.kuaishou.com', like_count: 89, comment_count: 12, share_count: 4, note: '', status: 'new', is_blacklisted: false, created_at: daysAgo(6) }
]

// ---------- 关键词 ----------
const KEYWORDS = [
  { id: 1, word: '装修', group: 1, group_name: '核心词', negative_words: '不需要,避雷,跑路,维权', hit_count: 132, created_at: daysAgo(10) },
  { id: 2, word: '全屋定制', group: 1, group_name: '核心词', negative_words: '', hit_count: 87, created_at: daysAgo(10) },
  { id: 3, word: '旧房改造', group: 1, group_name: '核心词', negative_words: '不需要', hit_count: 54, created_at: daysAgo(9) },
  { id: 4, word: '办公室装修', group: 2, group_name: '工装', negative_words: '广告,招聘', hit_count: 41, created_at: daysAgo(8) },
  { id: 5, word: '成都装修', group: 3, group_name: '地域词', negative_words: '', hit_count: 66, created_at: daysAgo(8) },
  { id: 6, word: '上海装修', group: 3, group_name: '地域词', negative_words: '', hit_count: 38, created_at: daysAgo(7) },
  { id: 7, word: '整装', group: 1, group_name: '核心词', negative_words: '', hit_count: 29, created_at: daysAgo(6) },
  { id: 8, word: '家装', group: 1, group_name: '核心词', negative_words: '', hit_count: 95, created_at: daysAgo(5) }
]
const GROUPS = [
  { id: 1, name: '核心词', count: 4 },
  { id: 2, name: '工装', count: 1 },
  { id: 3, name: '地域词', count: 2 }
]

// ---------- 任务 ----------
const TASKS = [
  { id: 1, name: '装修获客任务', keywords: '装修,全屋定制', platforms: ['weibo', 'zhihu', 'tieba'], status: 'completed', progress: 100, message: '采集完成', created_at: daysAgo(1) },
  { id: 2, name: '成都地域拓客', keywords: '成都装修,成都全屋定制', platforms: ['douyin', 'xiaohongshu'], status: 'running', progress: 62, message: '正在采集小红书...', created_at: daysAgo(0) },
  { id: 3, name: '工装专项', keywords: '办公室装修', platforms: ['weibo', 'douyin'], status: 'paused', progress: 35, message: '已暂停', created_at: daysAgo(2) },
  { id: 4, name: '全国翻新需求', keywords: '旧房改造,翻新', platforms: ['kuaishou', 'tieba'], status: 'failed', progress: 40, message: '平台风控拦截，等待重试', created_at: daysAgo(3) }
]

// ---------- 操作日志 ----------
const LOGS = [
  { id: 1, action: 'POST /api/tasks/', detail: '创建任务「装修获客任务」', ip: '127.0.0.1', created_at: daysAgo(1) },
  { id: 2, action: 'POST /api/keywords/', detail: '新增关键词「成都装修」', ip: '127.0.0.1', created_at: daysAgo(1) },
  { id: 3, action: 'POST /api/leads/1', detail: '拉黑线索 #6', ip: '127.0.0.1', created_at: daysAgo(2) },
  { id: 4, action: 'GET /api/leads/export', detail: '导出线索 Excel', ip: '127.0.0.1', created_at: daysAgo(2) }
]

const INDUSTRIES = ['装修', '全屋定制', '家装', '旧房改造', '办公室装修', '翻新', '整装', '装饰']
const CITIES = ['北京', '上海', '广州', '深圳', '成都', '杭州', '南京', '武汉', '长沙', '重庆', '西安', '郑州', '岳阳', '周口']
const INDUSTRY_DICT = {
  '装修': ['装修', '全屋定制', '整装', '家装', '旧房改造', '翻新'],
  '全屋定制': ['全屋定制', '定制柜', '衣柜定制', '橱柜定制'],
  '家装': ['家装', '家庭装修', '室内设计'],
  '旧房改造': ['旧房改造', '老房翻新', '二手房装修'],
  '办公室装修': ['办公室装修', '工装', '写字楼装修'],
  '翻新': ['翻新', '墙面翻新', '局部改造'],
  '整装': ['整装', '拎包入住'],
  '装饰': ['装饰', '软装', '硬装']
}

const HEATMAP = [
  { lng: 104.07, lat: 30.67, count: 132, city: '成都' },
  { lng: 121.47, lat: 31.23, count: 87, city: '上海' },
  { lng: 113.26, lat: 23.13, count: 74, city: '广州' },
  { lng: 114.06, lat: 22.54, count: 68, city: '深圳' },
  { lng: 120.15, lat: 30.28, count: 58, city: '杭州' },
  { lng: 116.41, lat: 39.91, count: 51, city: '北京' },
  { lng: 118.80, lat: 32.06, count: 33, city: '南京' },
  { lng: 113.13, lat: 29.37, count: 21, city: '岳阳' },
  { lng: 114.70, lat: 33.63, count: 17, city: '周口' },
  { lng: 103.83, lat: 36.06, count: 15, city: '兰州' }
]

const DISCLAIMER = `本平台提供的客户大数据采集与分析服务，旨在帮助用户合法合规地开展市场调研与客户开发工作。
使用本平台前，请您仔细阅读并理解以下条款：

一、合法性声明
1. 本平台采集的数据来源于互联网公开信息，仅限用于合法的商业调研、客户服务与市场分析用途。
2. 用户承诺：不得将本平台数据用于骚扰、诈骗、侵犯个人隐私、不正当竞争或其他任何违法违规活动。
3. 涉及个人信息的数据，用户应遵守《中华人民共和国个人信息保护法》《中华人民共和国数据安全法》及《中华人民共和国网络安全法》等相关法律法规。

二、使用限制
1. 禁止利用本平台对任何平台进行恶意攻击、高频抓取、绕过风控等破坏性行为。
2. 禁止将线索数据出售、转售或提供给任何第三方用于非法用途。
3. 用户应合理控制采集频率，尊重各平台的服务协议与 robots 协议。

三、数据合规
1. 本平台对采集的数据执行 30 天自动清理机制，到期数据将自动删除。
2. 本平台记录全部操作日志与采集日志，留存备查。
3. 用户应对自身账号下的所有操作行为负责。

四、免责声明
1. 因用户违规使用本平台导致的法律责任，由用户自行承担。
2. 本平台不保证数据的完整性、准确性或时效性，数据仅供参考。
3. 本平台不对因使用数据产生的任何直接或间接损失承担责任。

五、其他
1. 本声明解释权归本平台所有，平台有权根据法律法规变化适时更新本声明。
2. 继续使用本平台即视为您已阅读并同意本声明的全部内容。`

// ---------- 系统管理：用户 ----------
const SYS_USERS = [
  { id: 1, username: 'admin', nickname: '演示管理员', email: 'admin@example.com', phone: '', role_type: 'admin', is_active: true, plan: { plan_type: 'premium', quota_used: 12, quota_total: 50000, expire_at: '2027-01-01', concurrent_tasks: 20, daily_crawl_limit: 1000, api_access: true }, created_at: daysAgo(30) },
  { id: 2, username: 'demo', nickname: '演示用户', email: 'demo@example.com', phone: '', role_type: 'user', is_active: true, plan: { plan_type: 'free', quota_used: 3, quota_total: 1000, expire_at: '', concurrent_tasks: 1, daily_crawl_limit: 100, api_access: false }, created_at: daysAgo(12) },
  { id: 3, username: 'market01', nickname: '市场部小王', email: 'market@example.com', phone: '', role_type: 'user', is_active: true, plan: { plan_type: 'premium', quota_used: 45, quota_total: 50000, expire_at: '2026-12-01', concurrent_tasks: 20, daily_crawl_limit: 1000, api_access: true }, created_at: daysAgo(20) },
  { id: 4, username: 'sales02', nickname: '销售小李', email: 'sales@example.com', phone: '', role_type: 'user', is_active: false, plan: { plan_type: 'free', quota_used: 0, quota_total: 1000, expire_at: '', concurrent_tasks: 1, daily_crawl_limit: 100, api_access: false }, created_at: daysAgo(8) }
]

// ---------- 系统管理：参数 ----------
const SYS_PARAMS = {
  min_interval: 3, max_per_minute: 20, retry_times: 3,
  high_intent_threshold: 60, retention_days: 30, mode: 'mock'
}

// ---------- 系统管理：日志 ----------
const SYS_LOGS = [
  ...LOGS.map(l => ({ ...l, type: 'operation' })),
  { id: 10, type: 'crawl', action: 'crawl.douyin', detail: '抖音「装修」采集 45 条，风控正常', ip: '127.0.0.1', created_at: daysAgo(0) },
  { id: 11, type: 'crawl', action: 'crawl.xiaohongshu', detail: '小红书「全屋定制」采集 32 条，去重后 28 条', ip: '127.0.0.1', created_at: daysAgo(1) },
  { id: 12, type: 'crawl', action: 'crawl.weibo', detail: '微博「成都装修」采集 18 条，含 2 条广告已过滤', ip: '127.0.0.1', created_at: daysAgo(1) },
  { id: 13, type: 'crawl', action: 'crawl.zhihu', detail: '知乎「办公室装修」问答解析 12 条', ip: '127.0.0.1', created_at: daysAgo(2) },
  { id: 14, type: 'crawl', action: 'crawl.tieba', detail: '贴吧「旧房改造」采集 9 条，1 条触发限速等待', ip: '127.0.0.1', created_at: daysAgo(2) }
]

// ---------- Mock 路由 ----------
const json = (data, status = 200) => Promise.resolve({ data, status })

function route(config) {
  const method = (config.method || 'get').toLowerCase()
  const url = config.url || ''
  const body = config.data ? (typeof config.data === 'string' ? JSON.parse(config.data) : config.data) : {}
  const params = config.params || {}

  // 认证
  if (url === '/auth/login' && method === 'post') {
    if (body.username === 'admin' && body.password === 'admin123456') {
      return json({
        token: 'mock-jwt-token-for-demo',
        user: { id: 1, username: 'admin', nickname: '演示管理员', email: 'admin@example.com', phone: '', role_type: 'admin', plan: { plan_type: 'premium', quota_used: 12, quota_total: 50000, expire_at: '2027-01-01', concurrent_tasks: 20, daily_crawl_limit: 1000, api_access: true } }
      })
    }
    return json({ detail: '用户名或密码错误' }, 400)
  }
  if (url === '/auth/register' && method === 'post') {
    return json({ token: 'mock-jwt-token-for-demo', user: { id: 2, username: body.username, nickname: body.username, email: body.email || '', phone: '', role_type: 'user', plan: { plan_type: 'free', quota_used: 0, quota_total: 1000, expire_at: '', concurrent_tasks: 1, daily_crawl_limit: 100, api_access: false } } })
  }
  if (url === '/auth/profile') {
    return json({ id: 1, username: 'admin', nickname: '演示管理员', email: 'admin@example.com', phone: '', role_type: 'admin', plan: { plan_type: 'premium', quota_used: 12, quota_total: 50000, expire_at: '2027-01-01', concurrent_tasks: 20, daily_crawl_limit: 1000, api_access: true } })
  }
  if (url === '/auth/plan' && method === 'post') {
    return json({ detail: '套餐已升级' })
  }

  // 仪表盘统计
  if (url === '/stats/dashboard') {
    const total = LEADS.length
    const high = LEADS.filter(l => l.intent_label === 'high').length
    const avg = Math.round(LEADS.reduce((s, l) => s + l.intent_score, 0) / total)
    return json({ result: { total_leads: total, high_intent_leads: high, avg_intent_score: avg, running_tasks: TASKS.filter(t => t.status === 'running').length, total_tasks: TASKS.length, platforms_covered: 6 } })
  }
  if (url === '/stats/distribution') {
    const kind = params.kind || 'platform'
    if (kind === 'platform') {
      const map = {}
      LEADS.forEach(l => { map[l.platform] = (map[l.platform] || 0) + 1 })
      const names = { douyin: '抖音', xiaohongshu: '小红书', kuaishou: '快手', weibo: '微博', zhihu: '知乎', tieba: '贴吧' }
      return json({ results: Object.entries(map).map(([k, v]) => ({ name: names[k] || k, value: v })) })
    }
    if (kind === 'intent') {
      const map = {}
      LEADS.forEach(l => { map[l.intent_label] = (map[l.intent_label] || 0) + 1 })
      const names = { high: '高意向', medium: '中意向', low: '低意向', none: '无意向' }
      return json({ results: Object.entries(map).map(([k, v]) => ({ name: names[k] || k, value: v })) })
    }
    if (kind === 'task_status') {
      const map = {}
      TASKS.forEach(t => { map[t.status] = (map[t.status] || 0) + 1 })
      const names = { pending: '待启动', running: '运行中', paused: '已暂停', completed: '已完成', failed: '失败', stopped: '已终止' }
      return json({ results: Object.entries(map).map(([k, v]) => ({ name: names[k] || k, value: v })) })
    }
    return json({ results: [] })
  }
  if (url === '/stats/trend') {
    const days = parseInt(params.days || 7, 10)
    const results = []
    for (let i = days - 1; i >= 0; i--) {
      const d = new Date(NOW - i * 86400000)
      const key = `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
      results.push({ date: key, value: LEADS.filter(l => l.created_at.slice(0, 10) === d.toISOString().slice(0, 10)).length + Math.floor(Math.random() * 3) })
    }
    return json({ results })
  }
  if (url === '/stats/heatmap') {
    return json({ results: HEATMAP })
  }
  if (url === '/stats/keyword-effect') {
    const map = {}
    LEADS.forEach(l => { map[l.demand] = (map[l.demand] || 0) + 1 })
    return json({ results: Object.entries(map).map(([k, v]) => ({ name: k, count: v, avg_score: Math.round(50 + Math.random() * 30) })) })
  }

  // 关键词
  if (url === '/keywords/' && method === 'get') {
    let list = [...KEYWORDS]
    if (params.q) list = list.filter(k => k.word.includes(params.q))
    if (params.group) list = list.filter(k => k.group == params.group)
    return json({ results: list, total: list.length })
  }
  if (url === '/keywords/' && method === 'post') {
    const kw = { id: KEYWORDS.length + 1, word: body.word, group: body.group || null, group_name: GROUPS.find(g => g.id == body.group)?.name || '', negative_words: body.negative_words || '', hit_count: 0, created_at: daysAgo(0) }
    KEYWORDS.push(kw)
    return json({ result: kw }, 201)
  }
  if (url === '/keywords/groups') {
    return json({ results: GROUPS })
  }
  if (url === '/keywords/suggest') {
    const q = params.q || ''
    if (!q) return json({ results: [] })
    const hits = KEYWORDS.filter(k => k.word.includes(q)).map(k => k.word)
    const extra = INDUSTRIES.filter(i => i.includes(q) && !hits.includes(i))
    return json({ results: [...new Set([...hits, ...extra])].slice(0, 10) })
  }
  if (url === '/keywords/expand' && method === 'post') {
    const seed = body.seed || ''
    const city = body.city || ''
    let expanded = [...(INDUSTRY_DICT[body.industry] || []).filter(w => w !== seed)]
    if (city) expanded = [...expanded.map(w => city + w), ...expanded]
    expanded = [...new Set(expanded)]
    expanded.forEach(w => {
      if (!KEYWORDS.find(k => k.word === w)) {
        KEYWORDS.push({ id: KEYWORDS.length + 1, word: w, group: 1, group_name: '核心词', negative_words: '', hit_count: 0, created_at: daysAgo(0) })
      }
    })
    return json({ created: expanded.length, expanded })
  }
  if (/^\/keywords\/\d+$/.test(url) && method === 'put') {
    const id = parseInt(url.split('/')[2], 10)
    const kw = KEYWORDS.find(k => k.id === id)
    if (kw) Object.assign(kw, body)
    return json({ result: kw })
  }
  if (/^\/keywords\/\d+$/.test(url) && method === 'delete') {
    const id = parseInt(url.split('/')[2], 10)
    const idx = KEYWORDS.findIndex(k => k.id === id)
    if (idx >= 0) KEYWORDS.splice(idx, 1)
    return json({ detail: '已删除' })
  }

  // 任务
  if (url === '/tasks/' && method === 'get') {
    let list = [...TASKS]
    if (params.status) list = list.filter(t => t.status === params.status)
    return json({ results: list, total: list.length })
  }
  if (url === '/tasks/' && method === 'post') {
    const task = { id: TASKS.length + 1, name: body.name || (body.keywords || '').slice(0, 20), keywords: body.keywords, platforms: body.platforms, status: 'running', progress: Math.floor(Math.random() * 20), message: '任务已启动', created_at: daysAgo(0) }
    TASKS.unshift(task)
    return json({ result: task }, 201)
  }
  if (/^\/tasks\/\d+$/.test(url) && method === 'post') {
    const id = parseInt(url.split('/')[2], 10)
    const task = TASKS.find(t => t.id === id)
    const action = body.action
    if (task) {
      if (action === 'start' || action === 'resume') { task.status = 'running'; task.message = '任务运行中' }
      if (action === 'pause') { task.status = 'paused'; task.message = '已暂停' }
      if (action === 'stop') { task.status = 'stopped'; task.message = '已终止' }
      if (action === 'retry') { task.status = 'running'; task.progress = 0; task.message = '重试中' }
      if (action === 'delete') {
        const idx = TASKS.findIndex(t => t.id === id)
        if (idx >= 0) TASKS.splice(idx, 1)
        return json({ detail: '已删除' })
      }
    }
    return json({ result: task })
  }

  // 线索
  if (url === '/leads/' && method === 'get') {
    let list = LEADS.filter(l => !l.is_blacklisted)
    if (params.keyword) list = list.filter(l => (l.title + l.content).includes(params.keyword))
    if (params.platform) list = list.filter(l => l.platform === params.platform)
    if (params.intent) list = list.filter(l => l.intent_label === params.intent)
    if (params.region) list = list.filter(l => l.region === params.region)
    const page = parseInt(params.page || 1, 10)
    const pageSize = parseInt(params.page_size || 20, 10)
    const total = list.length
    const paged = list.slice((page - 1) * pageSize, page * pageSize)
    const regions = [...new Set(LEADS.filter(l => l.region && l.region !== '未知地域').map(l => l.region))]
    return json({ results: paged, total, regions })
  }
  if (/^\/leads\/\d+$/.test(url) && method === 'post') {
    const id = parseInt(url.split('/')[2], 10)
    const lead = LEADS.find(l => l.id === id)
    if (lead && body.action === 'note') lead.note = body.note
    if (lead && body.action === 'blacklist') lead.is_blacklisted = true
    return json({ result: lead })
  }

  // AI 分析
  if (/^\/analysis\/lead\/\d+$/.test(url)) {
    const id = parseInt(url.split('/')[3], 10)
    const lead = LEADS.find(l => l.id === id)
    if (!lead) return json({ detail: '不存在' }, 404)
    const region = lead.region !== '未知地域' ? lead.region : '您所在区域'
    const opening = lead.intent_score >= 60 ? '您好，看到您最近在关注' : '您好，打扰一下，注意到您提到'
    const closing = lead.intent_score >= 60 ? '我们正好提供该服务，可以给您一份详细的方案和报价，方便的话加个联系方式详聊？' : '如果后续有需要，可以随时联系我们，先给您留个资料参考。'
    const script = `${opening}「${lead.demand}」方面的问题。针对${region}的需求，我们可以提供专业建议与定制方案，已有多个类似客户案例。${closing}`
    return json({
      result: {
        lead,
        summary: lead.summary,
        sentiment: { keep: lead.intent_score >= 30, reason: lead.intent_score >= 30 ? '正向表达，存在明确需求' : '含负面词或低意向表达', pos_hits: ['需求', '推荐', '预算'], neg_hits: lead.intent_score < 30 ? ['避雷', '跑路'] : [] },
        script: { opening, body: `针对${region}的需求，我们可以提供专业建议与定制方案，已有多个类似客户案例。`, closing, full: script }
      }
    })
  }
  if (url === '/analysis/rescreen' && method === 'post') {
    const min = parseInt(body.min_score || 40, 10)
    let updated = 0
    LEADS.forEach(l => {
      if (l.intent_score < min) { l.status = 'filtered'; updated++ }
    })
    return json({ result: { updated } })
  }
  if (url === '/analysis/script' && method === 'post') {
    return json({ results: [] })
  }

  // 合规/杂项
  if (url === '/misc/disclaimer') {
    return json({ result: { text: DISCLAIMER, accepted: false } })
  }
  if (url === '/misc/logs') {
    return json({ results: LOGS })
  }
  if (url === '/misc/industry-nav') {
    if (params.industry && INDUSTRY_DICT[params.industry]) {
      let words = INDUSTRY_DICT[params.industry]
      if (params.city) words = [...words.map(w => params.city + w), ...words]
      return json({ results: { industry: params.industry, city: params.city || '', keywords: [...new Set(words)] } })
    }
    return json({ results: { industries: INDUSTRIES, cities: CITIES } })
  }

  // 系统管理
  if (url === '/admin/users' && method === 'get') {
    let list = [...SYS_USERS]
    if (params.q) list = list.filter(u => (u.username + u.nickname).includes(params.q))
    return json({ results: list, total: list.length })
  }
  if (url === '/admin/users' && method === 'post') {
    const u = { id: SYS_USERS.length + 1, username: body.username, nickname: body.nickname || body.username, email: body.email || '', phone: '', role_type: body.role_type || 'user', is_active: true, plan: { plan_type: 'free', quota_used: 0, quota_total: 1000, expire_at: '', concurrent_tasks: 1, daily_crawl_limit: 100, api_access: false }, created_at: daysAgo(0) }
    SYS_USERS.push(u)
    return json({ result: u }, 201)
  }
  if (/^\/admin\/users\/\d+$/.test(url) && method === 'put') {
    const id = parseInt(url.split('/')[3], 10)
    const u = SYS_USERS.find(x => x.id === id)
    if (u) Object.assign(u, { nickname: body.nickname, email: body.email, role_type: body.role_type })
    return json({ result: u })
  }
  if (/^\/admin\/users\/\d+$/.test(url) && method === 'post') {
    const id = parseInt(url.split('/')[3], 10)
    const u = SYS_USERS.find(x => x.id === id)
    if (u) u.is_active = !u.is_active
    return json({ result: u })
  }
  if (url === '/admin/params' && method === 'get') {
    return json({ result: { ...SYS_PARAMS } })
  }
  if (url === '/admin/params' && method === 'post') {
    Object.assign(SYS_PARAMS, body)
    return json({ result: { ...SYS_PARAMS } })
  }
  if (url === '/admin/logs') {
    let list = [...SYS_LOGS]
    if (params.type) list = list.filter(l => l.type === params.type)
    return json({ results: list, total: list.length })
  }
  if (url === '/admin/mode' && method === 'get') {
    return json({ result: { mode: SYS_PARAMS.mode } })
  }
  if (url === '/admin/mode' && method === 'post') {
    SYS_PARAMS.mode = body.mode || 'mock'
    return json({ result: { mode: SYS_PARAMS.mode } })
  }

  // 爬虫
  if (url === '/crawler/platforms') {
    const names = { douyin: '抖音', xiaohongshu: '小红书', kuaishou: '快手', weibo: '微博', zhihu: '知乎', tieba: '贴吧' }
    return json({ results: Object.entries(names).map(([k, v]) => ({ platform: k, name: v, enabled: true, mode: 'mock' })) })
  }
  if (url === '/crawler/mode') {
    return json({ result: { mode: 'mock' } })
  }
  if (url === '/crawler/config') {
    return json({ result: { min_interval: 3, max_per_minute: 20, retry_times: 3, mode: 'mock 演示模式' } })
  }

  // 未匹配
  return json({ detail: `Mock 未实现: ${method.toUpperCase()} ${url}` }, 404)
}

export default { route }
