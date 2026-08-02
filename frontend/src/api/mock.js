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
// 官方 API 凭证热配置 (演示: 内存态)
const MOCK_CREDENTIALS = {}
MOCK_BATCHES = []
MOCK_INDUSTRIES = [
  { name: '法律行业', word_count: 6 }, { name: '装修家居', word_count: 5 },
  { name: '企业B端财税商务服务', word_count: 4 }, { name: '教育培训', word_count: 4 },
  { name: '汽车服务行业', word_count: 4 }, { name: '本地生活家政服务', word_count: 4 },
  { name: '美业医美', word_count: 4 }, { name: '房产同城服务', word_count: 4 },
  { name: '婚庆摄影', word_count: 4 }, { name: '口腔/健康理疗', word_count: 4 },
  { name: '工程建材行业', word_count: 4 }, { name: '宠物行业', word_count: 4 },
  { name: '互联网服务商（代运营/软件开发）', word_count: 4 },
]
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


// ---------- 商业化: 5 档套餐 ----------
const PLANS = [
  { id: 'free', name: '免费试用版', price: 0, yearly_price: 0, tag: '引流款', features: { concurrent_tasks: 1, daily_leads: 30, ai_summary: 10, ai_copy: 5, export_limit: 50, monitoring: 0, templates: 0, heatmap: false, sub_accounts: 0, lead_lock: false }, restrictions: { crawl_speed: '低速15分钟间隔', keyword_limit: 20, lead_masking: '轻度脱敏', retention: '7天' } },
  { id: 'basic', name: '简易创业体验版', price: 59, yearly_price: 599, tag: '兼职过渡', features: { concurrent_tasks: 3, daily_leads: 180, ai_summary: 150, ai_copy: 80, export_limit: 1000, monitoring: 2, templates: 1, heatmap: '简易', sub_accounts: 0, lead_lock: false }, restrictions: { regional: '无区县过滤', support: '无优先客服' } },
  { id: 'standard', name: '小微个体户盈利版', price: 199, yearly_price: 1999, tag: '主力盈利', features: { concurrent_tasks: 10, daily_leads: 800, ai_monthly: 50000, export_limit: 10000, monitoring: -1, templates: -1, heatmap: '完整', sub_accounts: 1, lead_lock: true }, restrictions: { data_reports: false, operation_service: false }, yearly_bonus: '赠3个月小额扩容包' },
  { id: 'professional', name: '企业团队尊享版', price: 399, yearly_price: 3999, tag: '高利润核心', features: { concurrent_tasks: 25, daily_leads: 3000, ai_monthly: 150000, export_limit: 100000, monitoring: -1, templates: -1, heatmap: '完整', sub_accounts: 6, lead_lock: true, data_reports: true, operation_service: true }, restrictions: { permission_levels: false, private_deploy: false }, yearly_bonus: '赠3个月大额扩容包+15天AI高级文案' },
  { id: 'enterprise', name: '机构定制大客户版', price: 7288, yearly_price: 7288, tag: '机构大客户', features: { concurrent_tasks: -1, daily_leads: 10000, ai_monthly: -1, export_limit: -1, monitoring: -1, templates: 'custom', heatmap: '完整', sub_accounts: -1, lead_lock: true, data_reports: true, operation_service: true, permission_levels: true, private_deploy: true }, restrictions: {}, addons: { branding: 1800 } }
]
const ADDON_SERVICES = [
  { code: 'lead_expansion_small', name: '小额线索扩容包', desc: '+300条/日', price: 49, type: 'monthly' },
  { code: 'lead_expansion_large', name: '大额线索扩容包', desc: '+1200条/日', price: 129, type: 'monthly' },
  { code: 'ai_copy', name: 'AI高级文案包', desc: '高级营销文案生成', price: 39, type: 'monthly' },
  { code: 'ai_analysis', name: 'AI线索深度研判包', desc: '客户需求分层研判', price: 59, type: 'monthly' },
  { code: 'data_backup', name: '月度云端线索自动备份', desc: '每月自动云端备份', price: 59, type: 'monthly' },
  { code: 'lead_lock', name: '永久锁定线索', desc: '突破30天自动清理', price: 79, type: 'monthly' },
  { code: 'custom_templates', name: '细分行业专属词库定制', desc: '按行业定制词库', price: 129, type: 'one_time' },
  { code: 'kw_optimize', name: '精细化否定词库优化', desc: '优化无效关键词过滤', price: 89, type: 'one_time' },
  { code: 'data_archive', name: '批量历史线索归档打包', desc: '历史数据整理与打包', price: 69, type: 'one_time' },
  { code: 'operation_support', name: '全年1v1运营陪跑', desc: '季度策略指导+全年调参', price: 1280, type: 'enterprise' }
]
const COUPONS = [
  { code: 'firstPurchase_30', name: '新人首充立减30', discount: 30, min_amount: 59, expiry_days: 30 },
  { code: 'upgradeFrom199', name: '199元用户升级优惠', discount: 100, min_amount: 399, expiry_days: 15 }
]

// ---------- 实名认证状态 ----------
const REALNAME_STATUS = { authenticated: true, real_name: '张**', id_card_md5: 'a1b2c3***', face_verified: true, auth_date: '2026-07-01', plan_locked: false }

// ---------- B2B 企业库演示数据 ----------
const BIZ_COMPANIES = [
  { id: 1, name: '苏州精工机械制造有限公司', credit_code: '91320594MA1X2Y3Z4A', legal_person: '王建国', reg_date: '2021-03-15', capital: 500, status: '在业', province: '江苏', city: '苏州', district: '吴中区', industry_l3: '机械加工', channel_type: '工厂', insured_count: 32, recruit_cnt_30d: 4, tender_cnt_90d: 3, patent_cnt: 12, last_tender_date: '2026-07-20', last_recruit_date: '2026-07-25', lng: 120.62, lat: 31.25, product_tags: ['CNC加工', '精密零件'], intent_score: 86, contact_count: 2, top_contact: { name: '李采购', role: '采购经理', role_score: 0.85 } },
  { id: 2, name: '东莞市鑫达五金制品厂', credit_code: '91441900MA5A1B2C3D', legal_person: '陈志强', reg_date: '2019-08-01', capital: 200, status: '在业', province: '广东', city: '东莞', district: '长安镇', industry_l3: '五金制品', channel_type: '工厂', insured_count: 18, recruit_cnt_30d: 2, tender_cnt_90d: 1, patent_cnt: 3, last_tender_date: '2026-07-28', last_recruit_date: '2026-07-10', lng: 113.80, lat: 22.82, product_tags: ['五金冲压', '模具'], intent_score: 74, contact_count: 1, top_contact: { name: '刘厂长', role: '总经理', role_score: 0.92 } },
  { id: 3, name: '杭州云栖科技有限公司', credit_code: '91330106MA2B3C4D5E', legal_person: '周晓芸', reg_date: '2022-01-10', capital: 1000, status: '在业', province: '浙江', city: '杭州', district: '西湖区', industry_l3: '软件服务', channel_type: '网店', insured_count: 45, recruit_cnt_30d: 8, tender_cnt_90d: 5, patent_cnt: 20, last_tender_date: '2026-07-30', last_financing_date: '2026-06-15', lng: 120.13, lat: 30.27, product_tags: ['SaaS', '企业服务'], intent_score: 91, contact_count: 3, top_contact: { name: '张总', role: '创始人', role_score: 0.95 } },
  { id: 4, name: '成都蜀香食品有限公司', credit_code: '91510107MA1C2D3E4F', legal_person: '赵敏', reg_date: '2015-05-20', capital: 800, status: '在业', province: '四川', city: '成都', district: '武侯区', industry_l3: '食品加工', channel_type: '工厂', insured_count: 120, recruit_cnt_30d: 6, tender_cnt_90d: 0, patent_cnt: 8, last_recruit_date: '2026-07-18', lng: 104.06, lat: 30.57, product_tags: ['火锅底料', '调味品'], intent_score: 58, contact_count: 1, top_contact: { name: '王经理', role: '行政主管', role_score: 0.45 } },
  { id: 5, name: '北京启航教育科技有限公司', credit_code: '91110108MA2E3F4G5H', legal_person: '孙丽', reg_date: '2020-09-01', capital: 300, status: '在业', province: '北京', city: '北京', district: '海淀区', industry_l3: '教育培训', channel_type: '网店', insured_count: 28, recruit_cnt_30d: 3, tender_cnt_90d: 2, patent_cnt: 0, last_tender_date: '2026-07-22', lng: 116.31, lat: 39.98, product_tags: ['职业教育', '在线课程'], intent_score: 62, contact_count: 2, top_contact: { name: '李校长', role: '校长', role_score: 0.78 } },
  { id: 6, name: '佛山市顺德区宏远电器厂', credit_code: '91440606MA3A4B5C6D', legal_person: '黄伟', reg_date: '2018-11-11', capital: 150, status: '在业', province: '广东', city: '佛山', district: '顺德区', industry_l3: '家电配件', channel_type: '工厂', insured_count: 55, recruit_cnt_30d: 5, tender_cnt_90d: 4, patent_cnt: 15, last_tender_date: '2026-07-29', last_recruit_date: '2026-07-26', lng: 113.28, lat: 22.81, product_tags: ['小家电', '注塑件'], intent_score: 79, contact_count: 2, top_contact: { name: '何生', role: '采购总监', role_score: 0.88 } },
  { id: 7, name: '上海澜海物流有限公司', credit_code: '91310115MA4B5C6D7E', legal_person: '徐海涛', reg_date: '2016-03-03', capital: 2000, status: '在业', province: '上海', city: '上海', district: '浦东新区', industry_l3: '物流运输', channel_type: '经销商', insured_count: 210, recruit_cnt_30d: 12, tender_cnt_90d: 6, patent_cnt: 2, last_tender_date: '2026-07-31', last_recruit_date: '2026-07-28', lng: 121.54, lat: 31.22, product_tags: ['冷链物流', '仓储'], intent_score: 67, contact_count: 1, top_contact: { name: '陈经理', role: '运营经理', role_score: 0.52 } },
  { id: 8, name: '武汉光谷光电技术有限公司', credit_code: '91420100MA5C6D7E8F', legal_person: '刘洋', reg_date: '2021-06-06', capital: 1200, status: '在业', province: '湖北', city: '武汉', district: '洪山区', industry_l3: '光电设备', channel_type: '工厂', insured_count: 38, recruit_cnt_30d: 7, tender_cnt_90d: 3, patent_cnt: 25, last_tender_date: '2026-07-19', lng: 114.41, lat: 30.50, product_tags: ['激光设备', '光学元件'], intent_score: 83, contact_count: 2, top_contact: { name: '吴总', role: '技术总监', role_score: 0.81 } },
  { id: 9, name: '深圳市星辰电子商务有限公司', credit_code: '91440300MA6D7E8F9G', legal_person: '林晓星', reg_date: '2022-12-12', capital: 100, status: '在业', province: '广东', city: '深圳', district: '南山区', industry_l3: '电商运营', channel_type: '网店', insured_count: 15, recruit_cnt_30d: 4, tender_cnt_90d: 0, patent_cnt: 0, last_recruit_date: '2026-07-15', lng: 113.93, lat: 22.54, product_tags: ['跨境电商', '品牌代运营'], intent_score: 55, contact_count: 1, top_contact: { name: '林总', role: '创始人', role_score: 0.90 } },
  { id: 10, name: '郑州中原建工集团有限公司', credit_code: '91410100MA7E8F9G0H', legal_person: '郭铁柱', reg_date: '2010-04-08', capital: 5000, status: '在业', province: '河南', city: '郑州', district: '金水区', industry_l3: '建筑工程', channel_type: '经销商', insured_count: 350, recruit_cnt_30d: 15, tender_cnt_90d: 8, patent_cnt: 30, last_tender_date: '2026-07-30', last_recruit_date: '2026-07-27', lng: 113.65, lat: 34.76, product_tags: ['市政工程', '装饰装修'], intent_score: 71, contact_count: 3, top_contact: { name: '马工', role: '项目负责人', role_score: 0.76 } },
  { id: 11, name: '长沙湘江新材料有限公司', credit_code: '91430100MA8F9G0H1I', legal_person: '彭伟', reg_date: '2017-07-07', capital: 600, status: '在业', province: '湖南', city: '长沙', district: '岳麓区', industry_l3: '新材料', channel_type: '工厂', insured_count: 42, recruit_cnt_30d: 3, tender_cnt_90d: 2, patent_cnt: 18, last_tender_date: '2026-07-21', lng: 112.94, lat: 28.23, product_tags: ['复合材料', '防水材料'], intent_score: 64, contact_count: 1, top_contact: { name: '杨主任', role: '办公室主任', role_score: 0.41 } },
  { id: 12, name: '青岛蓝海水产养殖有限公司', credit_code: '91370200MA9G0H1I2J', legal_person: '于大海', reg_date: '2014-02-14', capital: 300, status: '在业', province: '山东', city: '青岛', district: '黄岛区', industry_l3: '水产养殖', channel_type: '工厂', insured_count: 25, recruit_cnt_30d: 1, tender_cnt_90d: 0, patent_cnt: 4, last_recruit_date: '2026-07-05', lng: 120.19, lat: 36.07, product_tags: ['海参养殖', '生鲜供应链'], intent_score: 49, contact_count: 0, top_contact: null }
]
const BIZ_TEMPLATES = [
  { id: 1, name: '机械加工高意向', industry: '机械加工', conditions: '成立1-3年 + 参保10-50人 + 近30天招标 + 机械加工', is_public: true, usage_count: 128 },
  { id: 2, name: '厂房装修需求', industry: '装修工程', conditions: '成立1-5年 + 近30天招聘 + 广东', is_public: true, usage_count: 86 },
  { id: 3, name: '光电设备采购潮', industry: '光电设备', conditions: '专利≥10 + 近90天招标≥3 + 湖北', is_public: false, usage_count: 32 }
]

// ---------- 短视频询盘演示数据 ----------
const INQUIRIES = [
  { id: 1, uid: 'dy_88213', nickname: '装修小王', platform: 'douyin', content: '老板这厂房装修多少钱一平？我家1200平想翻新', hit_keyword: '多少钱', source_video: '厂房装修实拍案例', video_id: 'v_72901', fan_cnt: 320, region: '广东东莞', intent_score: 0.92, status: 'to_touch', comment_time: daysAgo(0) },
  { id: 2, uid: 'dy_77102', nickname: '机械加工李哥', platform: 'douyin', content: '你们能加工铝件吗？有图纸想找厂家', hit_keyword: '厂家', source_video: 'CNC精密加工现场', video_id: 'v_72887', fan_cnt: 1200, region: '江苏苏州', intent_score: 0.88, status: 'dm_sent', comment_time: daysAgo(0) },
  { id: 3, uid: 'ks_55671', nickname: '五金店老陈', platform: 'kuaishou', content: '求推荐靠谱的供应商，我们做五金批发的', hit_keyword: '求推荐', source_video: '五金制品生产线', video_id: 'v_72855', fan_cnt: 58, region: '河北保定', intent_score: 0.85, status: 'to_touch', comment_time: daysAgo(1) },
  { id: 4, uid: 'dy_66420', nickname: '设计工作室阿凯', platform: 'douyin', content: '怎么联系你们？有个展厅项目想咨询', hit_keyword: '怎么联系', source_video: '展厅设计案例合集', video_id: 'v_72830', fan_cnt: 860, region: '浙江杭州', intent_score: 0.81, status: 'dm_sent', comment_time: daysAgo(1) },
  { id: 5, uid: 'sp_44198', nickname: '工厂主老周', platform: 'shipinhao', content: '想了解定制方案，有报价单吗？', hit_keyword: '报价', source_video: '工厂改造升级指南', video_id: 'v_72801', fan_cnt: 45, region: '山东青岛', intent_score: 0.78, status: 'card_pushed', comment_time: daysAgo(2) },
  { id: 6, uid: 'dy_33815', nickname: '创业小白', platform: 'douyin', content: '同行做得不错，学习一下', hit_keyword: '', source_video: '行业趋势分析', video_id: 'v_72780', fan_cnt: 210, region: '福建厦门', intent_score: 0.35, status: 'filtered_ad', comment_time: daysAgo(2) },
  { id: 7, uid: 'ks_22093', nickname: '装修师傅阿贵', platform: 'kuaishou', content: '多少钱一平方？包工包料吗', hit_keyword: '多少钱', source_video: '厂房环氧地坪施工', video_id: 'v_72760', fan_cnt: 66, region: '江苏常州', intent_score: 0.90, status: 'to_touch', comment_time: daysAgo(3) },
  { id: 8, uid: 'dy_11876', nickname: '采购助理小刘', platform: 'douyin', content: '我们公司在找供应商，方便留个联系方式吗', hit_keyword: '联系方式', source_video: '精密零件加工展示', video_id: 'v_72740', fan_cnt: 430, region: '四川成都', intent_score: 0.94, status: 'converted', comment_time: daysAgo(3) }
]
const MONITOR_TARGETS = [
  { id: 1, target_type: 'video', target_id: 'v_72901', platform: 'douyin', title: '厂房装修实拍案例', status: 'active', last_pull_time: daysAgo(0), comments_total: 324, high_intent: 12 },
  { id: 2, target_type: 'competitor_account', target_id: 'acc_7788', platform: 'douyin', title: '竞品@机械加工王总', status: 'active', last_pull_time: daysAgo(0), comments_total: 1089, high_intent: 45 },
  { id: 3, target_type: 'live_room', target_id: 'live_5566', platform: 'kuaishou', title: '五金工具直播间', status: 'paused', last_pull_time: daysAgo(2), comments_total: 540, high_intent: 8 },
  { id: 4, target_type: 'video', target_id: 'v_72887', platform: 'douyin', title: 'CNC精密加工现场', status: 'active', last_pull_time: daysAgo(0), comments_total: 208, high_intent: 9 }
]
const ACCOUNTS = [
  { id: 1, platform: 'douyin', name: '运营号A', status: 'active', health: 0.95, today_sent: 8, hourly_sent: 3, last_error: '' },
  { id: 2, platform: 'douyin', name: '运营号B', status: 'active', health: 0.88, today_sent: 12, hourly_sent: 5, last_error: '' },
  { id: 3, platform: 'kuaishou', name: '快手号C', status: 'cooling', health: 0.60, today_sent: 15, hourly_sent: 8, last_error: '触发频控冷却' },
  { id: 4, platform: 'shipinhao', name: '视频号D', status: 'frozen', health: 0.25, today_sent: 0, hourly_sent: 0, last_error: '连发爆发冻结' }
]

// ---------- 开发者特权（开发者专属） ----------
const DEV_OPTIONS = {
  is_developer: true,
  privileges: [
    { code: 'unlimited_collect', name: '无限采集', desc: '不消耗任何额度，并发无上限' },
    { code: 'unlimited_ai', name: '无限AI', desc: 'AI摘要/话术不限次数' },
    { code: 'unlimited_export', name: '无限导出', desc: '全量导出无限制' },
    { code: 'all_plans', name: '全套餐体验', desc: '免费体验全部5档套餐功能' },
    { code: 'dev_menu', name: '开发者菜单', desc: '专属开发者选项入口' },
    { code: 'data_admin', name: '数据管理', desc: '全量数据管理与清理权限' }
  ]
}


// ---------- ??销体系 & ??者?后台数据 ----------

// ---------- 12 行业词库（与 pain-point-system 对齐） ----------
const INDUSTRY_LIBRARY = {
  '装修家居': { mainWords: ['装修', '旧房翻新', '防水补漏', '全屋定制', '门窗定制'], longTailWords: ['家里装修大概多少钱', '老房子翻新方案', '卫生间漏水怎么修', '阳台封窗哪家好', '全屋定制报价', '新房装修流程', '厨房改造', '墙面渗水维修'], negativeWords: ['教程', '培训', '加盟', '招商', '厂家批发', '材料批发', '招聘', '设计图纸免费', '自媒体', '博主分享'] },
  '本地生活家政服务': { mainWords: ['家政保洁', '开荒保洁', '除甲醛', '家电清洗', '搬家', '月嫂'], longTailWords: ['新房开荒保洁价格', '甲醛治理有用吗', '空调清洗多少钱', '搬家公司推荐', '月嫂价格', '深度保洁', '下水道疏通', '保姆怎么找'], negativeWords: ['工具批发', '设备售卖', '培训课程', '加盟', '教学', '视频教程', '摆摊', '货源'] },
  '汽车服务行业': { mainWords: ['二手车', '汽车维修', '汽车贴膜', '车险', '租车'], longTailWords: ['本地二手私家车出售', '汽车保养价格', '车窗贴膜多少钱', '车险哪家划算', '短期租车', '事故车维修', '新能源维修'], negativeWords: ['车评', '测评', '博主', '批发配件', '汽配工厂', '教学', '改装教程', '赛事'] },
  '美业医美': { mainWords: ['祛斑祛痘', '植发', '美甲美睫', '皮肤管理', '整形'], longTailWords: ['脸上色斑怎么去除', '祛痘机构推荐', '植发大概费用', '纹眉价格', '产后瘦身', '双眼皮咨询'], negativeWords: ['教程', '自学', '工具批发', '培训学校', '加盟', '博主测评', '避坑视频', '货源'] },
  '教育培训': { mainWords: ['早教', '公考培训', '学历提升', '技能培训', '托管班'], longTailWords: ['成人自考怎么报名', '考公培训机构推荐', '幼儿托管收费', '会计培训班', '专升本途径'], negativeWords: ['资料免费下载', '网课资源', '题库', '教师招聘', '加盟办学', '课件分享'] },
  '企业B端财税商务服务': { mainWords: ['注册公司', '代理记账', '商标注册', '资质办理'], longTailWords: ['开公司流程', '小规模记账多少钱', '商标申请流程', '建筑资质办理', '公司注销手续'], negativeWords: ['教程自学', '模板下载', '招商加盟', '创业讲座', '课程培训', '电子书'] },
  '房产同城服务': { mainWords: ['二手房', '租房', '新房', '商铺出租'], longTailWords: ['本地两居室租房', '二手房首付多少', '商铺租金多少钱', '刚需新房推荐'], negativeWords: ['房产分析', '楼市预测', '投资讲座', '自媒体看房博主', '买房科普视频'] },
  '婚庆摄影': { mainWords: ['婚纱摄影', '婚礼策划', '婚庆布置', '跟妆'], longTailWords: ['婚纱照多少钱', '小型婚礼方案', '婚礼跟妆推荐', '生日派对布置'], negativeWords: ['道具批发', '教程自学', '素材模板', '摄影师接单平台', '教学课程'] },
  '口腔/健康理疗': { mainWords: ['牙科', '牙齿矫正', '体检', '康复理疗', '中医推拿'], longTailWords: ['隐形矫正价格', '洗牙多少钱', '牙周治疗', '中老年体检套餐', '腰间盘理疗'], negativeWords: ['医学科普', '论文', '自学', '药品批发', '养生视频博主'] },
  '工程建材行业': { mainWords: ['建材', '工装施工', '厂房搭建', '工程机械租赁'], longTailWords: ['办公室装修报价', '工地工程机械出租', '装修建材采购', '厂房改造施工'], negativeWords: ['工厂货源', '厂家直销', '招商', '展会资讯', '行业新闻', '批发价格表'] },
  '宠物行业': { mainWords: ['宠物美容', '宠物医院', '宠物寄养', '猫狗售卖'], longTailWords: ['猫咪疫苗价格', '狗狗寄养多少钱', '宠物皮肤病治疗', '纯种小猫多少钱'], negativeWords: ['饲养教程', '宠物测评', '用品批发', '进货渠道', '繁育教学'] },
  '互联网服务商（代运营/软件开发）': { mainWords: ['小程序开发', '短视频代运营', '抖店运营', '网站搭建'], longTailWords: ['商家小程序怎么做', '抖音店铺代运营费用', '企业官网搭建', '千川投放咨询'], negativeWords: ['免费源码', '自学教程', '素材下载', '课程培训', '教学直播', '模板免费领'] }
};
const GLOBAL_NEGATIVE_WORDS = ['攻略', '干货', '教程', '视频', '博主', '测评', '避坑', '加盟', '招商', '批发', '货源', '培训', '招聘', '图纸下载'];


// ===== 行业导航与获客词库（12 大行业）=====
const NAV_INDUSTRIES = [
  { id: 1, name: '装修家居', description: '精准高转化行业', preview: ['装修', '旧房翻新', '防水补漏', '全屋定制'], keywords: ['装修', '旧房翻新', '防水补漏', '全屋定制', '门窗定制'] },
  { id: 2, name: '本地生活家政服务', description: '需求量最大行业', preview: ['家政保洁', '开荒保洁', '除甲醛', '家电清洗'], keywords: ['家政保洁', '开荒保洁', '除甲醛', '家电清洗', '搬家', '月嫂'] },
  { id: 3, name: '汽车服务行业', description: '汽车相关服务', preview: ['二手车', '汽车维修', '汽车贴膜', '车险'], keywords: ['二手车', '汽车维修', '汽车贴膜', '车险', '租车'] },
  { id: 4, name: '美业医美', description: '美容医疗行业', preview: ['祛斑祛痘', '植发', '美甲美睫', '皮肤管理'], keywords: ['祛斑祛痘', '植发', '美甲美睫', '皮肤管理', '整形'] },
  { id: 5, name: '教育培训', description: '教育培训行业', preview: ['早教', '公考培训', '学历提升', '技能培训'], keywords: ['早教', '公考培训', '学历提升', '技能培训', '托管班'] },
  { id: 6, name: '企业B端财税商务服务', description: 'B端高利润行业', preview: ['注册公司', '代理记账', '商标注册', '资质办理'], keywords: ['注册公司', '代理记账', '商标注册', '资质办理'] },
  { id: 7, name: '房产同城服务', description: '房产相关服务', preview: ['二手房', '租房', '新房', '商铺出租'], keywords: ['二手房', '租房', '新房', '商铺出租'] },
  { id: 8, name: '婚庆摄影', description: '婚庆摄影行业', preview: ['婚纱摄影', '婚礼策划', '婚庆布置', '跟妆'], keywords: ['婚纱摄影', '婚礼策划', '婚庆布置', '跟妆'] },
  { id: 9, name: '口腔/健康理疗', description: '医疗健康行业', preview: ['牙科', '牙齿矫正', '体检', '康复理疗'], keywords: ['牙科', '牙齿矫正', '体检', '康复理疗', '中医推拿'] },
  { id: 10, name: '工程建材行业', description: '工程设备行业', preview: ['建材', '工程施工', '厂房搭建', '工程机械租赁'], keywords: ['建材', '工程施工', '厂房搭建', '工程机械租赁'] },
  { id: 11, name: '宠物行业', description: '宠物相关服务', preview: ['宠物美容', '宠物医院', '宠物寄养', '猫狗售卖'], keywords: ['宠物美容', '宠物医院', '宠物寄养', '猫狗售卖'] },
  { id: 12, name: '法律行业', description: '法律需求高利润行业', preview: ['婚姻家庭', '刑事辩护', '交通事故', '劳动仲裁'], keywords: ['婚姻家庭', '刑事辩护', '交通事故', '劳动仲裁', '合同纠纷', '知识产权', '房产纠纷', '债权债务', '公司法务', '侵权赔偿'] },
  { id: 13, name: '互联网服务商（代运营/软件开发）', description: '互联网电商行业', preview: ['小程序开发', '短视频代运营', '抖店运营', '网站搭建'], keywords: ['小程序开发', '短视频代运营', '抖店运营', '网站搭建'] }
];
const NAV_KEYWORD_LIB = {

  '法律行业': { mainWords: ['婚姻家庭', '刑事辩护', '交通事故', '劳动仲裁', '合同纠纷', '知识产权', '房产纠纷', '债权债务', '公司法务', '侵权赔偿'], longTailWords: ['离婚财产怎么分割', '刑事辩护律师费用', '交通事故赔偿标准', '劳动仲裁怎么申请', '合同纠纷如何起诉', '商标被侵权怎么办', '二手房买卖纠纷', '欠钱不还怎么起诉', '公司股权纠纷律师', '人身损害怎么赔偿'], negativeWords: ['法考培训', '司法考试', '法条背诵', '考研资料', '公开课', '法学生求职', '律所招聘', '法学论文'] },
  '装修家居': { mainWords: ['装修', '旧房翻新', '防水补漏', '全屋定制', '门窗定制'], longTailWords: ['家里装修大概多少钱', '老房子翻新方案', '卫生间漏水怎么修', '阳台封窗哪家好', '全屋定制报价', '新房装修流程', '厨房改造', '墙面渗水维修'], negativeWords: ['教程', '培训', '加盟', '招商', '厂家批发', '材料批发', '招聘', '设计图纸免费', '自媒体', '博主分享'] },
  '本地生活家政服务': { mainWords: ['家政保洁', '开荒保洁', '除甲醛', '家电清洗', '搬家', '月嫂'], longTailWords: ['新房开荒保洁价格', '甲醛治理有用吗', '空调清洗多少钱', '搬家公司推荐', '月嫂价格', '深度保洁', '下水道疏通', '保姆怎么找'], negativeWords: ['工具批发', '设备售卖', '培训课程', '加盟', '教学', '视频教程', '摆摊', '货源'] },
  '汽车服务行业': { mainWords: ['二手车', '汽车维修', '汽车贴膜', '车险', '租车'], longTailWords: ['本地二手私家车出售', '汽车保养价格', '车窗贴膜多少钱', '车险哪家划算', '短期租车', '事故车维修', '新能源维修'], negativeWords: ['车评', '测评', '博主', '批发配件', '汽配工厂', '教学', '改装教程', '赛事'] },
  '美业医美': { mainWords: ['祛斑祛痘', '植发', '美甲美睫', '皮肤管理', '整形'], longTailWords: ['脸上色斑怎么去除', '祛痘机构推荐', '植发大概费用', '纹眉价格', '产后瘦身', '双眼皮咨询'], negativeWords: ['教程', '自学', '工具批发', '培训学校', '加盟', '博主测评', '避坑视频', '货源'] },
  '教育培训': { mainWords: ['早教', '公考培训', '学历提升', '技能培训', '托管班'], longTailWords: ['成人自考怎么报名', '考公培训机构推荐', '幼儿托管收费', '会计培训班', '专升本途径'], negativeWords: ['资料免费下载', '网课资源', '题库', '教师招聘', '加盟办学', '课件分享'] },
  '企业B端财税商务服务': { mainWords: ['注册公司', '代理记账', '商标注册', '资质办理'], longTailWords: ['开公司流程', '小规模记账多少钱', '商标申请流程', '建筑资质办理', '公司注销手续'], negativeWords: ['教程自学', '模板下载', '招商加盟', '创业讲座', '课程培训', '电子书'] },
  '房产同城服务': { mainWords: ['二手房', '租房', '新房', '商铺出租'], longTailWords: ['本地两居室租房', '二手房首付多少', '商铺租金多少钱', '刚需新房推荐'], negativeWords: ['房产分析', '楼市预测', '投资讲座', '自媒体看房博主', '买房科普视频'] },
  '婚庆摄影': { mainWords: ['婚纱摄影', '婚礼策划', '婚庆布置', '跟妆'], longTailWords: ['婚纱照多少钱', '小型婚礼方案', '婚礼跟妆推荐', '生日派对布置'], negativeWords: ['道具批发', '教程自学', '素材模板', '摄影师接单平台', '教学课程'] },
  '口腔/健康理疗': { mainWords: ['牙科', '牙齿矫正', '体检', '康复理疗', '中医推拿'], longTailWords: ['隐形矫正价格', '洗牙多少钱', '牙周治疗', '中老年体检套餐', '腰间盘理疗'], negativeWords: ['医学科普', '论文', '自学', '药品批发', '养生视频博主'] },
  '工程建材行业': { mainWords: ['建材', '工装施工', '厂房搭建', '工程机械租赁'], longTailWords: ['办公室装修报价', '工地工程机械出租', '装修建材采购', '厂房改造施工'], negativeWords: ['工厂货源', '厂家直销', '招商', '展会资讯', '行业新闻', '批发价格表'] },
  '宠物行业': { mainWords: ['宠物美容', '宠物医院', '宠物寄养', '猫狗售卖'], longTailWords: ['猫咪疫苗价格', '狗狗寄养多少钱', '宠物皮肤病治疗', '纯种小猫多少钱'], negativeWords: ['饲养教程', '宠物测评', '用品批发', '进货渠道', '繁育教学'] },
  '互联网服务商（代运营/软件开发）': { mainWords: ['小程序开发', '短视频代运营', '抖店运营', '网站搭建'], longTailWords: ['商家小程序怎么做', '抖音店铺代运营费用', '企业官网搭建', '千川投放咨询'], negativeWords: ['免费源码', '自学教程', '素材下载', '课程培训', '教学直播', '模板免费领'] }
}
const NAV_CITIES = ['北京', '上海', '广州', '深圳', '成都', '杭州', '南京', '武汉', '长沙', '重庆', '西安', '郑州', '岳阳', '周口']


// ---- 客户线索演示数据（行业地域导航 drill-down 用） ----
const NAV_LEADS = [
  { id: 1, industry: '装修家居', region: '深圳', field: '全屋定制', scenario: '新房装修', need: '全屋定制报价方案', contact: '张先生', phone: '138****2211', intent: 92, status: '待跟进', created_at: '2026-07-31 10:20:00', tags: ['高意向', '新房', '定制'] },
  { id: 2, industry: '装修家居', region: '广州', field: '旧房翻新', scenario: '老房改造', need: '旧房翻新改造服务', contact: '李女士', phone: '139****8834', intent: 85, status: '待跟进', created_at: '2026-07-30 16:45:00', tags: ['老房', '翻新'] },
  { id: 3, industry: '法律行业', region: '北京', field: '婚姻家庭', scenario: '离婚财产分割', need: '离婚财产分割法律咨询', contact: '王先生', phone: '136****5521', intent: 95, status: '待跟进', created_at: '2026-07-31 09:15:00', tags: ['高意向', '婚姻'] },
  { id: 4, industry: '法律行业', region: '上海', field: '交通事故', scenario: '事故赔偿', need: '交通事故赔偿标准咨询', contact: '赵女士', phone: '137****9987', intent: 88, status: '待跟进', created_at: '2026-07-29 14:30:00', tags: ['事故', '赔偿'] },
  { id: 5, industry: '法律行业', region: '深圳', field: '劳动仲裁', scenario: '欠薪维权', need: '劳动仲裁申请代理', contact: '陈先生', phone: '135****4432', intent: 90, status: '待跟进', created_at: '2026-07-31 11:05:00', tags: ['劳动', '仲裁'] },
  { id: 6, industry: '法律行业', region: '广州', field: '刑事辩护', scenario: '取保候审', need: '刑事辩护律师委托', contact: '刘女士', phone: '134****2219', intent: 97, status: '待跟进', created_at: '2026-07-28 10:00:00', tags: ['高意向', '刑事'] },
  { id: 7, industry: '教育培训', region: '成都', field: '学历提升', scenario: '成人高考', need: '成人高考报名辅导', contact: '周先生', phone: '133****7788', intent: 78, status: '待跟进', created_at: '2026-07-30 09:40:00', tags: ['学历', '成考'] },
  { id: 8, industry: '企业B端财税商务服务', region: '杭州', field: '代理记账', scenario: '新公司注册', need: '公司注册+代理记账套餐', contact: '吴女士', phone: '132****5566', intent: 82, status: '待跟进', created_at: '2026-07-29 15:20:00', tags: ['B端', '记账'] },
  { id: 9, industry: '婚庆摄影', region: '南京', field: '婚礼策划', scenario: '婚礼筹备', need: '一站式婚礼策划服务', contact: '郑女士', phone: '131****3344', intent: 75, status: '待跟进', created_at: '2026-07-28 17:10:00', tags: ['婚礼'] },
  { id: 10, industry: '汽车服务行业', region: '武汉', field: '汽车维修', scenario: '事故车维修', need: '事故车维修报价', contact: '孙先生', phone: '130****9981', intent: 80, status: '待跟进', created_at: '2026-07-31 08:50:00', tags: ['事故车'] },
  { id: 11, industry: '法律行业', region: '重庆', field: '合同纠纷', scenario: '货款拖欠', need: '合同纠纷起诉代理', contact: '钱先生', phone: '159****6622', intent: 93, status: '待跟进', created_at: '2026-07-31 13:30:00', tags: ['高意向', '合同'] },
  { id: 12, industry: '美业医美', region: '长沙', field: '皮肤管理', scenario: '祛斑祛痘', need: '祛斑疗程咨询', contact: '冯女士', phone: '158****1122', intent: 70, status: '待跟进', created_at: '2026-07-30 11:25:00', tags: ['医美'] },
  { id: 13, industry: '法律行业', region: '北京', field: '知识产权', scenario: '商标侵权', need: '商标侵权维权诉讼', contact: '何先生', phone: '157****7789', intent: 91, status: '待跟进', created_at: '2026-07-29 16:00:00', tags: ['高意向', '商标'] },
  { id: 14, industry: '房产同城服务', region: '西安', field: '二手房', scenario: '二手房买卖', need: '二手房买卖中介服务', contact: '罗女士', phone: '156****4455', intent: 72, status: '待跟进', created_at: '2026-07-28 10:35:00', tags: ['二手房'] },
];

// ---- 法律行业 drill-down 树（行业→领域→场景→需求） ----
const NAV_LEGAL_TREE = {
  '婚姻家庭': { fields: { '离婚纠纷': { scenarios: { '离婚财产分割': ['离婚财产怎么分割', '离婚抚养权争取', '离婚房产归属'], '离婚抚养权': ['抚养权怎么判', '抚养费标准'] }, needs: ['离婚财产分割法律咨询', '离婚协议起草', '抚养权诉讼代理'] }, '婚前协议': { scenarios: { '婚前财产公证': ['婚前财产公证流程', '婚前协议怎么写'] }, needs: ['婚前财产协议起草'] } } },
  '刑事辩护': { fields: { '取保候审': { scenarios: { '刑事拘留': ['刑事拘留多久', '取保候审条件'] }, needs: ['取保候审申请', '刑事辩护律师委托'] }, '案件辩护': { scenarios: { '开庭辩护': ['刑事案件开庭流程', '辩护律师怎么选'] }, needs: ['刑事辩护代理', '会见嫌疑人'] } } },
  '交通事故': { fields: { '事故赔偿': { scenarios: { '事故责任认定': ['交通事故责任认定', '事故赔偿标准'] }, needs: ['交通事故赔偿咨询', '事故诉讼代理'] }, '保险理赔': { scenarios: { '保险理赔纠纷': ['保险理赔流程', '理赔金额争议'] }, needs: ['保险理赔代理'] } } },
  '劳动仲裁': { fields: { '欠薪维权': { scenarios: { '工资拖欠': ['公司拖欠工资怎么办', '劳动仲裁申请流程'] }, needs: ['劳动仲裁申请代理', '欠薪追讨法律咨询'] }, '工伤赔偿': { scenarios: { '工伤认定': ['工伤认定标准', '工伤赔偿计算'] }, needs: ['工伤赔偿代理'] } } },
  '合同纠纷': { fields: { '货款拖欠': { scenarios: { '合同违约': ['合同违约怎么起诉', '货款追讨'] }, needs: ['合同纠纷起诉代理', '货款催收法律服务'] }, '合同审查': { scenarios: { '合同风险': ['合同审查要点', '合同陷阱规避'] }, needs: ['合同审查服务'] } } },
  '知识产权': { fields: { '商标侵权': { scenarios: { '商标被侵权': ['商标侵权怎么办', '商标维权流程'] }, needs: ['商标侵权维权诉讼'] }, '专利保护': { scenarios: { '专利申请': ['专利申请流程', '专利侵权判定'] }, needs: ['专利代理申请'] } } },
  '房产纠纷': { fields: { '二手房买卖': { scenarios: { '买卖合同纠纷': ['二手房买卖纠纷处理', '房屋过户纠纷'] }, needs: ['房产纠纷诉讼代理'] }, '租赁纠纷': { scenarios: { '租房纠纷': ['租房合同纠纷', '押金退还纠纷'] }, needs: ['房屋租赁纠纷咨询'] } } },
  '债权债务': { fields: { '欠款催收': { scenarios: { '民间借贷': ['欠钱不还怎么起诉', '借条法律效力'] }, needs: ['债权催收代理', '民间借贷诉讼'] }, '债务重组': { scenarios: { '企业债务': ['企业债务重组方案', '破产清算'] }, needs: ['债务重组法律服务'] } } },
  '公司法务': { fields: { '股权纠纷': { scenarios: { '股权争议': ['股权纠纷怎么处理', '股东权益保护'] }, needs: ['股权纠纷诉讼代理'] }, '企业合规': { scenarios: { '公司治理': ['公司法律顾问服务', '企业合规审查'] }, needs: ['企业常年法律顾问'] } } },
  '侵权赔偿': { fields: { '人身损害': { scenarios: { '人身伤害赔偿': ['人身损害赔偿标准', '伤残鉴定流程'] }, needs: ['人身损害赔偿代理'] }, '名誉侵权': { scenarios: { '名誉权纠纷': ['名誉侵权怎么起诉', '网络侵权维权'] }, needs: ['名誉侵权诉讼代理'] } } },
};

// ---- 地域热点（13 行业统一） ----
const NAV_REGION_HOTSPOTS = {
  '北京': ['婚姻家庭', '刑事辩护', '交通事故', '劳动仲裁', '合同纠纷', '知识产权', '房产纠纷', '债权债务', '公司法务', '侵权赔偿', '装修家居', '教育培训', '企业B端财税商务服务', '房产同城服务'],
  '上海': ['婚姻家庭', '刑事辩护', '交通事故', '劳动仲裁', '合同纠纷', '知识产权', '房产纠纷', '债权债务', '公司法务', '侵权赔偿', '装修家居', '教育培训', '企业B端财税商务服务'],
  '广州': ['婚姻家庭', '刑事辩护', '交通事故', '劳动仲裁', '合同纠纷', '知识产权', '房产纠纷', '债权债务', '公司法务', '侵权赔偿', '装修家居', '汽车服务行业', '美业医美'],
  '深圳': ['婚姻家庭', '刑事辩护', '交通事故', '劳动仲裁', '合同纠纷', '知识产权', '房产纠纷', '债权债务', '公司法务', '侵权赔偿', '装修家居', '互联网服务商', '企业B端财税商务服务'],
  '江苏': ['婚姻家庭', '刑事辩护', '交通事故', '劳动仲裁', '合同纠纷', '知识产权', '房产纠纷', '债权债务', '公司法务', '侵权赔偿', '工程建材行业', '宠物行业'],
  '浙江': ['婚姻家庭', '刑事辩护', '交通事故', '劳动仲裁', '合同纠纷', '知识产权', '房产纠纷', '债权债务', '公司法务', '侵权赔偿', '婚庆摄影', '教育培训'],
  '广东': ['婚姻家庭', '刑事辩护', '交通事故', '劳动仲裁', '合同纠纷', '知识产权', '房产纠纷', '债权债务', '公司法务', '侵权赔偿', '汽车服务行业', '美业医美'],
};

const PROMOTION_DATA = {
  // 推广员
  promoters: [
    { id: 1, name: '??三', invite_code: 'INV888', rate: 0.30, customers: 12, status: 'active', freeze_reason: '', created_at: '2026-07-20 10:00:00' },
    { id: 2, name: '李四', invite_code: 'INV666', rate: 0.25, customers: 8, status: 'active', freeze_reason: '', created_at: '2026-07-22 14:30:00' },
    { id: 3, name: '王五', invite_code: 'INV333', rate: 0.20, customers: 3, status: 'frozen', freeze_reason: '批量?注刷单', created_at: '2026-07-25 09:00:00' }
  ],
  // 订单（含渠道/状态）
  orders: [
    { id: 'ord_1785510338701', user: 'user01', plan: 'basic', amount: 59, channel: 'wechat', status: 'paid', created_at: '2026-07-30 10:12:00' },
    { id: 'ord_1785510438702', user: 'user02', plan: 'pro', amount: 199, channel: 'alipay', status: 'paid', created_at: '2026-07-30 15:40:00' },
    { id: 'ord_1785510538703', user: 'user03', plan: 'channel_agent', amount: 1280, channel: 'wechat', status: 'paid', created_at: '2026-07-31 09:05:00' },
    { id: 'ord_1785510638704', user: 'user04', plan: 'basic', amount: 59, channel: 'alipay', status: 'refunded', created_at: '2026-07-31 11:22:00' },
    { id: 'ord_1785510738705', user: 'user05', plan: 'basic', amount: 59, channel: 'wechat', status: 'paid', created_at: '2026-07-31 14:45:00' },
    { id: 'ord_1785510838706', user: 'user06', plan: 'trial', amount: 0.01, channel: 'wechat', status: 'paid', created_at: '2026-07-31 16:30:00' }
  ],
  // 佣金（按推广员聚合）
  commissions: {
    '??三': [
      { order_id: 'ord_1785510338701', amount: 17.7, rate: 0.30, status: 'paid', created_at: '2026-07-30 10:12:00' },
      { order_id: 'ord_1785510438702', amount: 59.7, rate: 0.30, status: 'paid', created_at: '2026-07-30 15:40:00' },
      { order_id: 'ord_1785510738705', amount: 17.7, rate: 0.30, status: 'pending', created_at: '2026-07-31 14:45:00' }
    ],
    '李四': [
      { order_id: 'ord_1785510538703', amount: 320, rate: 0.25, status: 'paid', created_at: '2026-07-31 09:05:00' },
      { order_id: 'ord_1785510838706', amount: 0.0025, rate: 0.25, status: 'pending', created_at: '2026-07-31 16:30:00' }
    ]
  },
  // 提现
  withdrawals: [
    { id: 'wd_1785510938701', user: '??三', amount: 50, channel: 'wechat', status: 'pending', request_time: '2026-07-31 12:00:00' },
    { id: 'wd_1785511038702', user: '李四', amount: 200, channel: 'alipay', status: 'approved', request_time: '2026-07-30 18:00:00' }
  ],
  // 客户登记报表
  userReports: [
    { userId: 'user01', registrationTime: '2026-07-30 10:12:00', paymentChannel: 'wechat', identitySubject: '张*', promoter: '??三', promoterId: 1, planStatus: 'basic', paymentHistory: 1, commissionHistory: 1, deviceIP: '113.87.160.11', operationLogs: 23, customerContact: '138****0000' },
    { userId: 'user02', registrationTime: '2026-07-30 15:40:00', paymentChannel: 'alipay', identitySubject: '李*', promoter: '??三', promoterId: 1, planStatus: 'pro', paymentHistory: 1, commissionHistory: 1, deviceIP: '120.36.88.22', operationLogs: 15, customerContact: '139****2222' },
    { userId: 'user03', registrationTime: '2026-07-31 09:05:00', paymentChannel: 'wechat', identitySubject: '王*', promoter: '李四', promoterId: 2, planStatus: 'channel_agent', paymentHistory: 1, commissionHistory: 1, deviceIP: '218.94.33.5', operationLogs: 31, customerContact: '137****8888' },
    { userId: 'user05', registrationTime: '2026-07-31 14:45:00', paymentChannel: 'wechat', identitySubject: '赵*', promoter: '??三', promoterId: 1, planStatus: 'basic', paymentHistory: 1, commissionHistory: 1, deviceIP: '114.96.201.7', operationLogs: 9, customerContact: '136****6666' },
    { userId: 'user06', registrationTime: '2026-07-31 16:30:00', paymentChannel: 'wechat', identitySubject: '孙*', promoter: '李四', promoterId: 2, planStatus: 'trial', paymentHistory: 1, commissionHistory: 1, deviceIP: '115.212.77.19', operationLogs: 4, customerContact: '135****1111' }
  ],
  // 全量用户（开发者视角）
  users: [
    { id: 1, username: 'admin', name: '', plan: 'premium', identity: 'verified', contact: 'dev@example.com', device_ip: '127.0.0.1', registered_at: '2026-07-01 00:00:00', is_promoter: false },
    { id: 2, username: 'user01', name: '', plan: 'basic', identity: 'verified', contact: '138****0000', device_ip: '113.87.160.11', registered_at: '2026-07-30 10:12:00', is_promoter: false },
    { id: 3, username: 'user02', name: '', plan: 'pro', identity: 'verified', contact: '139****2222', device_ip: '120.36.88.22', registered_at: '2026-07-30 15:40:00', is_promoter: false },
    { id: 4, username: 'user03', name: '', plan: 'channel_agent', identity: 'pending', contact: '137****8888', device_ip: '218.94.33.5', registered_at: '2026-07-31 09:05:00', is_promoter: false },
    { id: 5, username: 'user05', name: '', plan: 'basic', identity: 'verified', contact: '136****6666', device_ip: '114.96.201.7', registered_at: '2026-07-31 14:45:00', is_promoter: false }
  ],
  financeReports: {
    totalIncome: 1656.01,
    channelAgentFeeIncome: 1280,
    commissionExpense: 415.1025,
    wechatAlipayReconciliation: {
      wechat: { paid: 1398.01, refunded: 0, balance: 1398.01 },
      alipay: { paid: 258, refunded: 59, balance: 199 }
    },
    reportDate: '2026-07-31'
  }
}

function route(config) {
  const method = (config.method || 'get').toLowerCase()
  let url = config.url || ''
  const body = config.data ? (typeof config.data === 'string' ? JSON.parse(config.data) : config.data) : {}
  const params = Object.assign({}, config.params || {})
  // 兼容 URL 内嵌 query（如 /stats/distribution?kind=intent）
  const qIdx = url.indexOf('?')
  if (qIdx >= 0) {
    const qs = url.substring(qIdx + 1)
    url = url.substring(0, qIdx)
    qs.split('&').forEach(pair => {
      if (!pair) return
      const eq = pair.indexOf('=')
      const k = eq >= 0 ? pair.substring(0, eq) : pair
      const v = eq >= 0 ? pair.substring(eq + 1) : ''
      if (k && !(k in params)) params[k] = decodeURIComponent(v)
    })
  }

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
    const ind = params.industry
    if (ind && NAV_KEYWORD_LIB[ind]) {
      const lib = NAV_KEYWORD_LIB[ind]
      let words = [...lib.mainWords, ...lib.longTailWords]
      if (params.city) words = [...words.map(w => params.city + w), ...words]
      return json({ results: { industry: ind, city: params.city || '', keywords: [...new Set(words)], mainWords: lib.mainWords, longTailWords: lib.longTailWords, negativeWords: lib.negativeWords, globalNegativeWords: GLOBAL_NEGATIVE_WORDS, description: (NAV_INDUSTRIES.find(x => x.name === ind) || {}).description || '' } })
    }
    return json({ results: { industries: NAV_INDUSTRIES, cities: NAV_CITIES, keywords: {} } })
  }
  if (url === '/keywords/promoter-industries' && method === 'get') {
    const saved = ((typeof localStorage !== 'undefined' ? localStorage.getItem('promoter_industries') : '') || '').split(',').filter(Boolean).map(Number)
    const list = NAV_INDUSTRIES.filter(x => saved.includes(x.id))
    return json({ results: { industries: list.map(x => ({ id: x.id, name: x.name, description: x.description })) } })
  }
  if (url === '/keywords/promoter-industries' && method === 'post') {
    const ids = (body.industryIds || []).map(Number)
    if (typeof localStorage !== 'undefined') localStorage.setItem('promoter_industries', ids.join(','))
    return json({ result: { saved: ids.length, industryIds: ids } })
  }


  // 行业地域导航 · 客户线索（drill-down）
  if (url === '/misc/industry-leads' && method === 'get') {
    let list = NAV_LEADS.slice()
    if (params.industry) list = list.filter(x => params.industry.includes(x.industry) || x.industry.includes(params.industry))
    if (params.region) list = list.filter(x => params.region.includes(x.region) || x.region.includes(params.region))
    if (params.field) list = list.filter(x => params.field.includes(x.field) || x.field.includes(params.field))
    if (params.scenario) list = list.filter(x => params.scenario.includes(x.scenario) || x.scenario.includes(params.scenario))
    if (params.intent) {
      const min = Number(params.intent)
      list = list.filter(x => x.intent >= min)
    }
    return json({ results: list, total: list.length })
  }
  if (url === '/misc/industry-regions') {
    return json({ results: { hotspots: NAV_REGION_HOTSPOTS, cities: NAV_CITIES } })
  }
  if (url === '/misc/industry-tree' && method === 'get') {
    const ind = params.industry || ''
    if (ind === '法律行业') {
      return json({ results: { industry: ind, tree: NAV_LEGAL_TREE } })
    }
    // 其他行业：用词库主词/长尾词生成简化树
    const lib = NAV_KEYWORD_LIB[ind] || { mainWords: [], longTailWords: [] }
    const tree = {}
    lib.mainWords.forEach((m, i) => {
      tree[m] = { fields: { '常见需求': { scenarios: { [m + '咨询']: lib.longTailWords.slice(i * 2, i * 2 + 2) }, needs: [m + '服务咨询', m + '方案报价'] } } }
    })
    return json({ results: { industry: ind, tree } })
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
  // ---------- 官方开放 API 合规采集 ----------
  if (url === '/crawler/official/platforms') {
    const names = { douyin: '抖音', xiaohongshu: '小红书', kuaishou: '快手', weibo: '微博', zhihu: '知乎', tieba: '贴吧' }
    return json({
      results: Object.entries(names).map(([k, v]) => {
        const cred = MOCK_CREDENTIALS[k]
        return { platform: k, name: v, mode: cred && Object.keys(cred).length ? 'official_api' : 'demo', configured: !!(cred && Object.keys(cred).length), is_configured: !!(cred && Object.keys(cred).length) }
      }),
      compliance: {
        channels: '仅使用各平台官方开放 API / 公开接口',
        sensitive_data: '不采集手机号/微信号/私信/真实姓名等个人敏感信息',
        actions: '不自动私信/不批量评论/不破解风控',
        retention_days: 30,
        audit: true
      }
    })
  }
  if (url === '/crawler/official/search' && method === 'get') {
    const platform = params.platform || 'douyin'
    const keyword = params.keyword || '客户需求'
    const limit = Math.min(parseInt(params.limit || 5, 10), 50)
    const names = { douyin: '抖音', xiaohongshu: '小红书', kuaishou: '快手', weibo: '微博', zhihu: '知乎', tieba: '贴吧' }
    const templates = [
      '正在找' + keyword + '解决方案，有推荐吗？',
      '想知道' + keyword + '哪家靠谱',
      '刚接触' + keyword + '，求入门建议',
      keyword + '供应商怎么选？预算有限',
      keyword + '行业有哪些坑？',
      '谁用过' + keyword + '，体验如何',
      '想了解' + keyword + '的最新玩法',
      keyword + '案例分享',
      keyword + '合作渠道有哪些'
    ]
    const regions = ['广东', '浙江', '江苏', '北京', '上海', '四川']
    const results = Array.from({ length: Math.min(limit, 5) }, (_, i) => ({
      id: platform + '_demo_' + i,
      platform,
      platform_name: names[platform] || platform,
      title: templates[i % templates.length],
      content: '用户分享关于「' + keyword + '」的真实经历与需求, 希望寻找靠谱服务商。',
      summary: '',
      author: { nickname: '用户_' + Math.floor(1000 + Math.random() * 9000), gender: 'unknown', fans_count: Math.floor(Math.random() * 5000) },
      url: 'https://demo.' + platform + '.com/post/' + i,
      region: regions[i % regions.length],
      like_count: Math.floor(Math.random() * 500),
      comment_count: Math.floor(Math.random() * 100),
      share_count: Math.floor(Math.random() * 50),
      created_at: daysAgo(i),
      source: 'demo',
      collected_at: new Date().toISOString().slice(0, 19).replace('T', ' ')
    }))
    return json({ results, platform, platform_name: names[platform] || platform, mode: 'demo', keyword, total: results.length })
  }
  if (url === '/crawler/official/search' && method === 'post') {
    const searches = (body && body.searches) || []
    const names = { douyin: '抖音', xiaohongshu: '小红书', kuaishou: '快手', weibo: '微博', zhihu: '知乎', tieba: '贴吧' }
    const out = searches.map((s, idx) => {
      const platform = (s.platform || '').toLowerCase()
      const keyword = s.keyword || ''
      const limit = Math.min(parseInt(s.limit || 5, 10), 50)
      const results = Array.from({ length: Math.min(limit, 3) }, (_, i) => ({
        id: platform + '_demo_' + idx + '_' + i,
        platform,
        platform_name: names[platform] || platform,
        title: '[' + (names[platform] || platform) + '] ' + keyword + ' 意向线索 ' + (i + 1),
        content: '用户讨论「' + keyword + '」相关需求, 可能为潜在客户。',
        author: { nickname: '用户_' + Math.floor(1000 + Math.random() * 9000), gender: 'unknown', fans_count: 0 },
        url: 'https://demo.' + platform + '.com/post/' + idx + '_' + i,
        region: '未知',
        like_count: 0, comment_count: 0, share_count: 0,
        created_at: daysAgo(i),
        source: 'demo'
      }))
      return { platform, platform_name: names[platform] || platform, keyword, mode: 'demo', results, total: results.length }
    })
    return json({ results: out })
  }
  if (url === '/crawler/official/audit') {
    const logs = [
      { id: 'audit_1', platform: 'douyin', keyword: '装修', result_count: 5, mode: 'demo', ts: new Date().toISOString().slice(0, 19).replace('T', ' ') },
      { id: 'audit_2', platform: 'weibo', keyword: '全屋定制', result_count: 3, mode: 'demo', ts: new Date(Date.now() - 3600000).toISOString().slice(0, 19).replace('T', ' ') },
      { id: 'audit_3', platform: 'zhihu', keyword: '法律咨询', result_count: 4, mode: 'demo', ts: new Date(Date.now() - 7200000).toISOString().slice(0, 19).replace('T', ' ') }
    ]
    return json({ results: logs })
  }
  // 凭证热配置 (演示: 内存态, 演示配置后该平台切换为 official_api 状态)
  if (url === '/crawler/official/credentials') {
    const pnames = { douyin: '抖音', xiaohongshu: '小红书', kuaishou: '快手', weibo: '微博', zhihu: '知乎', tieba: '贴吧' }
    if (method === 'get') {
      const out = {}
      for (const p of Object.keys(pnames)) {
        const cred = MOCK_CREDENTIALS[p]
        if (cred && Object.keys(cred).length) {
          const masked = {}
          for (const [k, v] of Object.entries(cred)) masked[k] = String(v).slice(0, 3) + '***' + String(v).slice(-2)
          out[p] = { source: 'redis', credentials: masked }
        } else {
          out[p] = { source: 'none', credentials: {} }
        }
      }
      return json({ results: out })
    }
    if (method === 'post') {
      const platform = String(body.platform || '').toLowerCase()
      const creds = body.credentials || {}
      if (!pnames[platform] || typeof creds !== 'object') {
        return json({ detail: '平台或凭证格式无效' }, 400)
      }
      MOCK_CREDENTIALS[platform] = {}
      for (const [k, v] of Object.entries(creds)) {
        if (v) MOCK_CREDENTIALS[platform][k] = String(v)
      }
      return json({ ok: true, platform, mode: 'official_api', configured: true })
    }
    if (method === 'delete') {
      const platform = String(params.platform || '').toLowerCase()
      if (pnames[platform]) {
        delete MOCK_CREDENTIALS[platform]
        return json({ ok: true, platform, mode: 'demo' })
      }
      return json({ detail: '平台无效' }, 400)
    }

  // ---------- 行业关键词批量自动采集 ----------
  if (url === '/crawler/industry/batch' && method === 'post') {
    const ind = (body.industry || '').trim()
    const plats = Array.isArray(body.platforms) ? body.platforms : ['weibo']
    const mk = Math.max(1, Math.min(parseInt(body.max_keywords || 8, 10) || 8, 15))
    const industryPool = {
      '法律行业': ['婚姻家庭', '刑事辩护', '合同纠纷', '劳动仲裁', '交通事故', '债务纠纷'],
      '装修家居': ['旧房翻新', '办公室装修', '全屋定制', '水电改造', '墙面翻新'],
      '企业B端财税商务服务': ['税务筹划', '代理记账', '工商注册', '资质代办'],
      '教育培训': ['少儿编程', 'K12辅导', '职业培训', '成人学历'],
      '汽车服务行业': ['汽车保养', '洗车美容', '车险续保', '二手车评估'],
      '本地生活家政服务': ['月嫂育婴', '保洁清洗', '家电维修', '搬家服务'],
      '美业医美': ['皮肤管理', '医美整形', '美甲美睫', '纹绣'],
      '房产同城服务': ['二手房买卖', '新房团购', '商铺租赁', '房屋托管'],
      '婚庆摄影': ['婚礼策划', '婚纱摄影', '跟妆服务', '婚宴预订'],
      '口腔/健康理疗': ['种植牙', '牙齿矫正', '推拿理疗', '体检套餐'],
      '工程建材行业': ['防水工程', '瓷砖批发', '门窗定制', '钢结构'],
      '宠物行业': ['宠物美容', '宠物寄养', '宠物医院', '宠物用品'],
      '互联网服务商（代运营/软件开发）': ['电商代运营', '小程序开发', '网站建设', '短视频代运营'],
    }
    const pool = industryPool[ind] || ['关键词1', '关键词2', '关键词3']
    const keywords = pool.slice(0, mk)
    const batchId = 'MOCK' + Date.now().toString().slice(-8)
    MOCK_BATCHES.unshift({
      batch_id: batchId, industry: ind, platforms: plats, status: 'running',
      created_at: now(), finished_at: null, total_keywords: keywords.length,
      completed_keywords: 0, imported_count: 0,
      sub_tasks: keywords.map(k => ({ keyword: k, platform: plats[0], task_id: null, status: 'pending', result_count: 0, import_result: 0, error: null })),
    })
    // 模拟进度推进
    const b = MOCK_BATCHES[0]
    let done = 0
    const timer = setInterval(() => {
      if (done >= b.sub_tasks.length) { clearInterval(timer); b.status = 'completed'; b.finished_at = now(); return }
      b.sub_tasks[done].status = 'completed'
      b.sub_tasks[done].result_count = 5 + done * 3
      b.sub_tasks[done].import_result = 3 + done * 2
      b.completed_keywords = ++done
      b.imported_count += b.sub_tasks[done - 1].import_result
    }, 1500)
    return json({ success: true, batch_id: batchId, industry: ind, platforms: plats, keywords, sub_task_count: keywords.length * plats.length, message: `已启动行业[${ind}]批量采集，${keywords.length} 个关键词 × ${plats.length} 平台` })
  }
  if (url === '/crawler/industry/batch' && method === 'get') {
    const id = params.id || ''
    if (id) {
      const b = MOCK_BATCHES.find(x => x.batch_id === id)
      if (!b) return json({ success: false, error: 'batch not found' }, 404)
      return json({ success: true, batch: b })
    }
    return json({ success: true, batches: MOCK_BATCHES })
  }
  if (url === '/crawler/industry/options') {
    return json({ results: {
      industries: MOCK_INDUSTRIES,
      platforms: [{ code: 'weibo', name: '微博' }, { code: 'douyin', name: '抖音' }, { code: 'xiaohongshu', name: '小红书' }, { code: 'kuaishou', name: '快手' }, { code: 'zhihu', name: '知乎' }, { code: 'tieba', name: '贴吧' }],
    } })
  }

  }



  // ---------- 商业化: 套餐/增值/优惠券 ----------
  if (url === '/plans') {
    return json({ results: PLANS, total: PLANS.length })
  }
  if (url === '/plans/addons') {
    return json({ results: ADDON_SERVICES, total: ADDON_SERVICES.length })
  }
  if (url === '/coupons') {
    return json({ results: COUPONS, total: COUPONS.length })
  }

  // ---------- 实名认证 ----------
  if (url === '/auth/realname' && method === 'get') {
    return json({ result: REALNAME_STATUS })
  }
  if (url === '/auth/realname' && method === 'post') {
    // 模拟认证: 一证一号校验
    if (body.id_card && body.id_card.length !== 18) {
      return json({ detail: '身份证号格式错误(18位)' }, 400)
    }
    return json({ result: { authenticated: true, real_name: body.real_name || '张**', face_verified: true, auth_date: daysAgo(0), message: '实名认证成功，已赠送10条当日线索' } })
  }

  // ---------- B2B 企业库 ----------
  if (url === '/biz/companies' && method === 'get') {
    let list = [...BIZ_COMPANIES]
    if (params.province) list = list.filter(c => c.province.includes(params.province))
    if (params.city) list = list.filter(c => c.city.includes(params.city))
    if (params.industry) list = list.filter(c => c.industry_l3.includes(params.industry))
    if (params.insured_min) list = list.filter(c => c.insured_count >= parseInt(params.insured_min, 10))
    if (params.insured_max) list = list.filter(c => c.insured_count <= parseInt(params.insured_max, 10))
    if (params.tender_90d) list = list.filter(c => c.tender_cnt_90d >= parseInt(params.tender_90d, 10))
    if (params.intent_min) list = list.filter(c => c.intent_score >= parseInt(params.intent_min, 10))
    if (params.q) list = list.filter(c => (c.name + c.product_tags.join('')).includes(params.q))
    return json({ results: list, total: list.length })
  }
  if (url === '/biz/companies/geo') {
    // 地图圈选: 经纬度+半径 模拟
    return json({ results: BIZ_COMPANIES.slice(0, 5), total: 5, hint: '模拟圈选: ' + (params.lng || '') + ',' + (params.lat || '') + ' 半径' + (params.radius || 10) + 'km' })
  }
  if (/^\/biz\/companies\/\d+$/.test(url) && method === 'get') {
    const id = parseInt(url.split('/')[3], 10)
    const c = BIZ_COMPANIES.find(x => x.id === id)
    if (!c) return json({ detail: '企业不存在' }, 404)
    return json({ result: { ...c, events: [
      { event_type: 'tender', event_date: c.last_tender_date || daysAgo(10), detail: '中标公告发布', source_url: 'https://example.com/tender' },
      { event_type: 'recruit', event_date: c.last_recruit_date || daysAgo(20), detail: '新增招聘岗位', source_url: 'https://example.com/job' }
    ], contacts: (c.contact_count || 0) > 0 ? [{ name: c.top_contact.name, role: c.top_contact.role, role_score: c.top_contact.role_score, phone: '138****' + String(c.id).padStart(4, '0'), valid_status: 'valid', masked: true }] : [] } })
  }
  if (url === '/biz/companies/export' && method === 'post') {
    // 导出: 扣点+审计+水印
    return json({ result: { export_id: 'exp_' + Date.now(), count: (body.company_ids || []).length, cost_points: 10 * (body.company_ids || []).length, watermark: '已脱敏-演示水印', audit_logged: true } })
  }
  if (url === '/biz/templates' && method === 'get') {
    return json({ results: BIZ_TEMPLATES, total: BIZ_TEMPLATES.length })
  }
  if (url === '/biz/templates' && method === 'post') {
    const t = { id: BIZ_TEMPLATES.length + 1, name: body.name, industry: body.industry || '', conditions: JSON.stringify(body.conditions || {}), is_public: !!body.is_public, usage_count: 0 }
    BIZ_TEMPLATES.push(t)
    return json({ result: t }, 201)
  }

  // ---------- 短视频询盘/监控/账号池 ----------
  if (url === '/monitor/inquiries' && method === 'get') {
    let list = [...INQUIRIES]
    if (params.min_score) list = list.filter(i => i.intent_score >= parseFloat(params.min_score))
    if (params.status) list = list.filter(i => i.status === params.status)
    return json({ results: list, total: list.length })
  }
  if (url === '/monitor/targets' && method === 'get') {
    return json({ results: MONITOR_TARGETS, total: MONITOR_TARGETS.length })
  }
  if (url === '/monitor/targets' && method === 'post') {
    const t = { id: MONITOR_TARGETS.length + 1, target_type: body.target_type, target_id: body.target_id, platform: body.platform, title: body.title || '新监控目标', status: 'active', last_pull_time: daysAgo(0), comments_total: 0, high_intent: 0 }
    MONITOR_TARGETS.push(t)
    return json({ result: t }, 201)
  }
  if (url === '/accounts' && method === 'get') {
    return json({ results: ACCOUNTS, total: ACCOUNTS.length })
  }
  if (url === '/accounts' && method === 'post') {
    const a = ACCOUNTS.find(x => x.id === parseInt(body.id, 10))
    if (a) { a.status = body.status || a.status; a.last_error = body.status === 'active' ? '' : (a.last_error || '手动调整') }
    return json({ result: a })
  }
  if (url === '/trigger/rules' && method === 'get') {
    return json({ results: [
      { id: 1, name: '高意向自动私信', cond_intent_min: 0.70, cond_fan: '50-5000', action_type: 'send_dm', round: 1, enabled: true },
      { id: 2, name: '中意向回评', cond_intent_min: 0.60, cond_fan: '100-10000', action_type: 'reply_comment', round: 2, enabled: true }
    ], total: 2 })
  }

  // ---------- 开发者特权 ----------
  if (url === '/dev/options' && method === 'get') {
    return json({ result: DEV_OPTIONS })
  }


  // ---------- ??销体系 ----------
  if (url === '/promotion/my' && method === 'get') {
    // 当前用户推广员信息（演示固定返回??三）
    const me = PROMOTION_DATA.promoters[0]
    const myComms = PROMOTION_DATA.commissions[me.name] || []
    const paidSum = myComms.filter(c => c.status === 'paid').reduce((s, c) => s + c.amount, 0)
    const pendingSum = myComms.filter(c => c.status === 'pending').reduce((s, c) => s + c.amount, 0)
    return json({
      promoter: me,
      stats: { total_commission: Math.round((paidSum + pendingSum) * 100) / 100, withdrawable: Math.round(paidSum * 100) / 100, customers: me.customers }
    })
  }
  if (url === '/promotion/apply' && method === 'post') {
    return json({ detail: '??请成功，已生成邀?码 INV888', promoter: PROMOTION_DATA.promoters[0] }, 201)
  }
  if (url === '/promotion/commissions' && method === 'get') {
    const rows = []
    Object.entries(PROMOTION_DATA.commissions).forEach(([name, list]) => {
      list.forEach(c => rows.push({ promoter: name, ...c }))
    })
    return json({ results: rows, total: rows.length })
  }
    if (url === '/promotion/withdraw' && method === 'post') {
    const wd = { id: 'wd_' + Date.now(), user: body.user || '??三', amount: body.amount, channel: body.channel || 'wechat', status: 'pending', payout_id: '', request_time: daysAgo(0) }
    PROMOTION_DATA.withdrawals.push(wd)
    return json({ detail: '提?申?已提交，?待?核', withdrawalId: wd.id }, 201)
  }
  if (url === '/promotion/register' && method === 'post') {
    // 0.01??体验包?册（经推?海报）
    const promo = body.promoter || ''
    const poster = PROMOTION_DATA.promoters.find(p => p.name === promo || p.invite_code === promo)
    if (!poster) return json({ detail: '无?的推?海报' }, 400)
    const order = { id: 'ord_' + Date.now(), user: body.username || 'new_user', plan: 'trial', amount: 0.01, channel: body.channel || 'wechat', status: 'paid', created_at: daysAgo(0) }
    PROMOTION_DATA.orders.push(order)
    poster.customers += 1
    return json({
      success: true,
      message: '注册成功，已开通 0.01 元体验包',
      orderId: order.id,
      token: 'mock-trial-token-' + Date.now(),
      user: { id: 100 + poster.customers, username: body.username || 'new_user', plan: 'trial' }
    }, 201)
  }

  // ---------- ??者?后台 ----------
  
  // ---------- 行业词库 ----------
  if (url === '/keywords/industry-library' && method === 'get') {
    const industry = params.industry || ''
    if (industry) {
      const lib = INDUSTRY_LIBRARY[industry]
      if (!lib) return json({ detail: '未知行业: ' + industry }, 404)
      const allNeg = [...lib.negativeWords, ...GLOBAL_NEGATIVE_WORDS]
      return json({ result: { industry, mainWords: lib.mainWords, longTailWords: lib.longTailWords, negativeWords: lib.negativeWords, globalNegativeWords: GLOBAL_NEGATIVE_WORDS, allNegativeWords: [...new Set(allNeg)] } })
    }
    return json({ result: { industries: Object.keys(INDUSTRY_LIBRARY), globalNegativeWords: GLOBAL_NEGATIVE_WORDS } })
  }
  if (url === '/keywords/industry-apply' && method === 'post') {
    const industry = body.industry || ''
    const lib = INDUSTRY_LIBRARY[industry]
    if (!lib) return json({ detail: '请提供有效的行业名' }, 400)
    const words = [...lib.mainWords, ...lib.longTailWords]
    let created = 0, skipped = 0
    words.forEach(w => {
      if (KEYWORDS.some(k => k.word === w)) { skipped++ } else {
        KEYWORDS.push({ id: KEYWORDS.length + 1, word: w, group_id: null, group_name: '行业词库-' + industry, negative_words: [...new Set([...lib.negativeWords, ...GLOBAL_NEGATIVE_WORDS])].join(','), hot_score: 80, enabled: true, hit_count: 0, created_at: daysAgo(0) })
        created++
      }
    })
    return json({ result: { industry, created, skipped, group: { id: null, name: '行业词库-' + industry } } })
  }


  // 提?审核（?款：返回分?流水? payout_id）
  if (/^\/admin\/withdrawal\/[\w-]+$/.test(url) && method === 'post') {
    const wid = url.split('/')[3]
    const wd = PROMOTION_DATA.withdrawals.find(w => w.id === wid)
    if (!wd) return json({ detail: '提?不存在' }, 404)
    const action = body.status || 'approved'
    if (action === 'approved') {
      wd.status = 'approved'
      wd.payout_id = 'po_' + Date.now()
      wd.processed_time = daysAgo(0)
      return json({ detail: '已打款', payout_id: wd.payout_id, provider: 'yungouos' })
    }
    wd.status = 'rejected'
    wd.remark = body.remark || ''
    return json({ detail: '已更新: rejected' })
  }

if (url === '/admin/platform' && method === 'get') {
    const f = PROMOTION_DATA.financeReports
    return json({
      users: PROMOTION_DATA.users,
      orders: PROMOTION_DATA.orders,
      commissions: PROMOTION_DATA.commissions,
      withdrawals: PROMOTION_DATA.withdrawals,
      promoters: PROMOTION_DATA.promoters,
      userReports: PROMOTION_DATA.userReports,
      financeReports: f
    })
  }
  if (url.startsWith('/admin/promoter/') && url.endsWith('/freeze') && method === 'post') {
    const pid = parseInt(url.split('/')[3], 10)
    const p = PROMOTION_DATA.promoters.find(x => x.id === pid)
    if (!p) return json({ detail: '推?员不存在' }, 404)
    p.status = 'frozen'
    p.freeze_reason = body.reason || '违?操作'
    return json({ detail: '推?员已?结：' + p.name })
  }
  
  if (url === '/promotion/pay' && method === 'post') {
    const oid = body.orderId || ''
    const order = PROMOTION_DATA.orders.find(x => x.id === oid)
    if (!order) return json({ detail: '订单不存在' }, 404)
    order.status = 'paid'
    return json({ detail: '支付成功，体验包已开通', orderId: oid })
  }

if (url === '/admin/withdrawals' && method === 'get') {
    return json({ results: PROMOTION_DATA.withdrawals })
  }
  if (url.startsWith('/admin/withdrawal/') && method === 'post') {
    const wid = url.split('/')[3]
    const wd = PROMOTION_DATA.withdrawals.find(x => x.id === wid)
    if (!wd) return json({ detail: '提?不存在' }, 404)
    wd.status = body.status || 'approved'
    return json({ detail: '已更新：' + wd.status })
  }

  // 未匹配
  return json({ detail: `Mock 未实现: ${method.toUpperCase()} ${url}` }, 404)
}

export default { route }
