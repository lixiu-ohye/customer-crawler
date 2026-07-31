# 行业痛点解决方案管理系统

将各行业获客痛点（误采同行/游客/博主/自学党、无效关键词、风控拦截、线索重复、合规风险等）转化为可落地的程序化解决方案。

## 模块架构

| 模块 | 职责 | 解决痛点 |
|------|------|----------|
| `PainPointSolutionSystem` | 主系统，聚合 8 大模块 + 12 行业词库 | 统一入口 |
| `TaskManager` | 采集任务管理：动态限速/重试/会话池/平台检测 | 平台风控拦截 |
| `KeywordManager` | 关键词管理：行业词库/词效检测/批量导入 | 无效关键词浪费额度 |
| `AIManager` | 行业意向打分/黑名单过滤/分场景话术 | 误采同行博主、意向误判 |
| `LeadManager` | 线索管理：双重去重/合并/批量操作/分配/锁定 | 线索重复、多人争抢 |
| `ExportManager` | 导出：异步/模板自定义/套餐分级额度 | 导出滥用 |
| `ComplianceManager` | 合规：功能锁定/错误标准化/弹窗控制 | 违规操作、数据泄露 |
| `IndustryManager` | 行业特定解决方案 | 各行业专属痛点 |
| `SystemManager` | 系统管理：定时清理/性能监控/一键初始化 | 数据膨胀、资源过载 |

## 12 大行业词库

装修家居、本地生活家政、汽车服务、美业医美、教育培训、企业B端财税商务、房产同城、婚庆摄影、口腔/健康理疗、工程建材、宠物、互联网服务商（代运营/软件开发）

每行业含：主词（4-6 个）+ 长尾词（6-8 个）+ 否定词（7-10 个），另有 15 个通用全局否定词（攻略/干货/教程/视频/博主/测评/避坑/加盟/招商/批发/货源/培训/招聘/图纸下载）。

## 使用示例

```javascript
const { painPointSystem, TaskManager, AIManager, LeadManager, ExportManager, ComplianceManager } = require('./painPointSolutionSystem');

// 初始化
painPointSystem.systemManager.initializeSystem();

// 创建任务并应用行业词库
const taskManager = new TaskManager();
const taskId = 'task_123';
taskManager.createTask(taskId, '小红书', ['装修', '防水补漏']);
painPointSystem.applyIndustryKeywordsToTask(taskId, '装修家居');

// 执行 + 失败重试
taskManager.executeTask(taskId)
  .then(console.log)
  .catch(err => { console.error(err.message); taskManager.retryTask(taskId); });

// AI 意向打分
const aiManager = new AIManager();
console.log(aiManager.calculateLeadScore('装修家居', '家里装修大概多少钱，预算10万'));

// AI 话术（地域变量填充）
console.log(aiManager.generateCopywriting('装修家居', '咨询报价', '北京'));

// 线索去重
const leadManager = new LeadManager();
leadManager.addLead('lead_456', { userId: 'user_789', content: '家里装修大概多少钱' });

// 合规弹窗
const complianceManager = new ComplianceManager();
if (complianceManager.shouldShowCompliancePopup('user_789', 'data_sharing')) {
  const popupId = complianceManager.showCompliancePopup('user_789', 'data_sharing');
  complianceManager.confirmCompliancePopup(popupId);
}
```

## 与 customer-crawler 系统集成点

1. **12 行业词库** → 已存在于 `scripts/init.sql` 行业导航（IndustryType 12 行业），可将 mainWords/longTailWords/negativeWords 落为 keywords 表 seed 数据
2. **TaskManager 限速/重试/会话池** → 对应后端 `tasks` app（CrawlTask 已有 pages/progress/retry 字段），可补 UA 轮换与动态限速逻辑
3. **AIManager 打分** → 对应双链路 `service-intent`（关键词预筛 + LLM 评分），行业权重模型可直接映射
4. **LeadManager 去重/合并** → 对应 `leads` app（Lead 模型已有 item_id 幂等字段），补 user_id+content 双重去重
5. **ComplianceManager** → 对应已有合规红线（禁手机号/禁私信/30 天清理），错误标准化提示可接入前端

## 合规声明

- 动态限速/会话池仅用于降低合规请求频率，禁止破解平台风控
- 线索数据 30 天自动清理，全程留痕
- 生产环境仅限自有账号合法运营
