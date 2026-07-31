/**
 * 行业痛点解决方案管理系统
 * 将各行业获客痛点转化为可落地的程序化解决方案
 *
 * 模块：TaskManager / KeywordManager / AIManager / LeadManager /
 *       ExportManager / ComplianceManager / IndustryManager / SystemManager
 */

/**
 * 行业痛点解决方案管理系统（主系统）
 */
class PainPointSolutionSystem {
  constructor() {
    // 初始化各模块
    this.taskManager = new TaskManager();
    this.keywordManager = new KeywordManager();
    this.aiManager = new AIManager();
    this.leadManager = new LeadManager();
    this.exportManager = new ExportManager();
    this.complianceManager = new ComplianceManager();
    this.industryManager = new IndustryManager();
    this.systemManager = new SystemManager();

    // 初始化行业词库
    this.industryKeywords = this.initializeIndustryKeywords();
  }

  // 初始化行业词库
  initializeIndustryKeywords() {
    return {
      '装修家居': {
        mainWords: ['装修', '旧房翻新', '防水补漏', '全屋定制', '门窗定制'],
        longTailWords: [
          '家里装修大概多少钱', '老房子翻新方案', '卫生间漏水怎么修',
          '阳台封窗哪家好', '全屋定制报价', '新房装修流程',
          '厨房改造', '墙面渗水维修'
        ],
        negativeWords: ['教程', '培训', '加盟', '招商', '厂家批发', '材料批发', '招聘', '设计图纸免费', '自媒体', '博主分享']
      },
      '本地生活家政服务': {
        mainWords: ['家政保洁', '开荒保洁', '除甲醛', '家电清洗', '搬家', '月嫂'],
        longTailWords: [
          '新房开荒保洁价格', '甲醛治理有用吗', '空调清洗多少钱',
          '搬家公司推荐', '月嫂价格', '深度保洁',
          '下水道疏通', '保姆怎么找'
        ],
        negativeWords: ['工具批发', '设备售卖', '培训课程', '加盟', '教学', '视频教程', '摆摊', '货源']
      },
      '汽车服务行业': {
        mainWords: ['二手车', '汽车维修', '汽车贴膜', '车险', '租车'],
        longTailWords: [
          '本地二手私家车出售', '汽车保养价格', '车窗贴膜多少钱',
          '车险哪家划算', '短期租车', '事故车维修',
          '新能源维修'
        ],
        negativeWords: ['车评', '测评', '博主', '批发配件', '汽配工厂', '教学', '改装教程', '赛事']
      },
      '美业医美': {
        mainWords: ['祛斑祛痘', '植发', '美甲美睫', '皮肤管理', '整形'],
        longTailWords: [
          '脸上色斑怎么去除', '祛痘机构推荐', '植发大概费用',
          '纹眉价格', '产后瘦身', '双眼皮咨询'
        ],
        negativeWords: ['教程', '自学', '工具批发', '培训学校', '加盟', '博主测评', '避坑视频', '货源']
      },
      '教育培训': {
        mainWords: ['早教', '公考培训', '学历提升', '技能培训', '托管班'],
        longTailWords: [
          '成人自考怎么报名', '考公培训机构推荐', '幼儿托管收费',
          '会计培训班', '专升本途径'
        ],
        negativeWords: ['资料免费下载', '网课资源', '题库', '教师招聘', '加盟办学', '课件分享']
      },
      '企业B端财税商务服务': {
        mainWords: ['注册公司', '代理记账', '商标注册', '资质办理'],
        longTailWords: [
          '开公司流程', '小规模记账多少钱', '商标申请流程',
          '建筑资质办理', '公司注销手续'
        ],
        negativeWords: ['教程自学', '模板下载', '招商加盟', '创业讲座', '课程培训', '电子书']
      },
      '房产同城服务': {
        mainWords: ['二手房', '租房', '新房', '商铺出租'],
        longTailWords: [
          '本地两居室租房', '二手房首付多少', '商铺租金多少钱',
          '刚需新房推荐'
        ],
        negativeWords: ['房产分析', '楼市预测', '投资讲座', '自媒体看房博主', '买房科普视频']
      },
      '婚庆摄影': {
        mainWords: ['婚纱摄影', '婚礼策划', '婚庆布置', '跟妆'],
        longTailWords: [
          '婚纱照多少钱', '小型婚礼方案', '婚礼跟妆推荐',
          '生日派对布置'
        ],
        negativeWords: ['道具批发', '教程自学', '素材模板', '摄影师接单平台', '教学课程']
      },
      '口腔/健康理疗': {
        mainWords: ['牙科', '牙齿矫正', '体检', '康复理疗', '中医推拿'],
        longTailWords: [
          '隐形矫正价格', '洗牙多少钱', '牙周治疗',
          '中老年体检套餐', '腰间盘理疗'
        ],
        negativeWords: ['医学科普', '论文', '自学', '药品批发', '养生视频博主']
      },
      '工程建材行业': {
        mainWords: ['建材', '工装施工', '厂房搭建', '工程机械租赁'],
        longTailWords: [
          '办公室装修报价', '工地工程机械出租', '装修建材采购',
          '厂房改造施工'
        ],
        negativeWords: ['工厂货源', '厂家直销', '招商', '展会资讯', '行业新闻', '批发价格表']
      },
      '宠物行业': {
        mainWords: ['宠物美容', '宠物医院', '宠物寄养', '猫狗售卖'],
        longTailWords: [
          '猫咪疫苗价格', '狗狗寄养多少钱', '宠物皮肤病治疗',
          '纯种小猫多少钱'
        ],
        negativeWords: ['饲养教程', '宠物测评', '用品批发', '进货渠道', '繁育教学']
      },
      '互联网服务商（代运营/软件开发）': {
        mainWords: ['小程序开发', '短视频代运营', '抖店运营', '网站搭建'],
        longTailWords: [
          '商家小程序怎么做', '抖音店铺代运营费用', '企业官网搭建',
          '千川投放咨询'
        ],
        negativeWords: ['免费源码', '自学教程', '素材下载', '课程培训', '教学直播', '模板免费领']
      },
      '通用全局否定词': [
        '攻略', '干货', '教程', '视频', '博主', '测评', '避坑',
        '加盟', '招商', '批发', '货源', '培训', '招聘', '图纸下载'
      ]
    };
  }

  // 应用行业词库到任务
  applyIndustryKeywordsToTask(taskId, industry) {
    const keywords = this.industryKeywords[industry];
    if (!keywords) return false;

    // 添加主词和长尾词
    this.keywordManager.addKeywords(taskId, [...keywords.mainWords, ...keywords.longTailWords]);

    // 添加否定词
    this.keywordManager.addNegativeKeywords(taskId, [...keywords.negativeWords, ...this.industryKeywords['通用全局否定词']]);

    return true;
  }
}

/**
 * 采集任务管理模块
 */
class TaskManager {
  constructor() {
    this.tasks = new Map();
    this.platformSpeedLimits = {
      '小红书': { baseDelay: 5000, randomRange: 3000 },
      '贴吧': { baseDelay: 2000, randomRange: 1000 }
    };
    this.retryMechanism = {
      maxRetries: 3,
      retryDelays: [1000, 3000, 5000]
    };
    this.sessionPool = this.initializeSessionPool();
  }

  // 初始化会话池
  initializeSessionPool() {
    const uaList = [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ];

    const headersList = [
      { 'User-Agent': uaList[0], 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' },
      { 'User-Agent': uaList[1], 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' }
    ];

    return {
      uaList,
      headersList,
      currentIndex: 0,
      getNextSession: function() {
        const session = {
          ua: this.uaList[this.currentIndex % this.uaList.length],
          headers: this.headersList[this.currentIndex % this.headersList.length]
        };
        this.currentIndex++;
        return session;
      }
    };
  }

  // 创建采集任务
  createTask(taskId, platform, keywords) {
    const task = {
      id: taskId,
      platform,
      keywords,
      status: 'created',
      speedLimit: this.platformSpeedLimits[platform] || { baseDelay: 3000, randomRange: 1000 },
      session: this.sessionPool.getNextSession(),
      retryCount: 0,
      lastError: null
    };

    this.tasks.set(taskId, task);
    return task;
  }

  // 执行采集任务
  async executeTask(taskId) {
    const task = this.tasks.get(taskId);
    if (!task) throw new Error('任务不存在');

    // 检查平台状态
    if (!this.checkPlatformAccess(task.platform)) {
      throw new Error('平台访问受限');
    }

    // 动态限速
    const delay = task.speedLimit.baseDelay +
      Math.random() * task.speedLimit.randomRange;

    // 模拟采集过程
    console.log(`开始采集任务 ${taskId}，平台: ${task.platform}, 延时: ${delay}ms`);

    // 模拟可能的错误
    if (Math.random() < 0.1) {
      throw new Error('风控拦截');
    }

    // 模拟成功
    return { success: true, data: `模拟采集数据 ${taskId}` };
  }

  // 检查平台访问权限
  checkPlatformAccess(platform) {
    // 模拟平台访问检查
    return true;
  }

  // 重试任务
  async retryTask(taskId) {
    const task = this.tasks.get(taskId);
    if (!task) throw new Error('任务不存在');

    if (task.retryCount >= this.retryMechanism.maxRetries) {
      throw new Error('超过最大重试次数');
    }

    task.retryCount++;
    const delay = this.retryMechanism.retryDelays[task.retryCount - 1];

    setTimeout(async () => {
      try {
        await this.executeTask(taskId);
      } catch (error) {
        task.lastError = error.message;
        console.error(`任务 ${taskId} 重试失败: ${error.message}`);
      }
    }, delay);
  }

  // 清理任务
  cleanupTask(taskId) {
    this.tasks.delete(taskId);
  }
}

/**
 * 关键词管理模块
 */
class KeywordManager {
  constructor() {
    this.keywords = new Map();
    this.keywordEffectiveness = new Map();
  }

  // 添加关键词
  addKeywords(taskId, words) {
    if (!this.keywords.has(taskId)) {
      this.keywords.set(taskId, []);
    }

    this.keywords.get(taskId).push(...words);
    console.log(`任务 ${taskId} 添加关键词: ${words.join(', ')}`);
  }

  // 添加否定词
  addNegativeKeywords(taskId, words) {
    // 实际项目中应存储为否定词
    console.log(`任务 ${taskId} 添加否定词: ${words.join(', ')}`);
  }

  // 词效检测
  detectKeywordEffectiveness(taskId) {
    const taskKeywords = this.keywords.get(taskId) || [];
    const ineffectiveKeywords = [];

    // 模拟检测无效关键词
    taskKeywords.forEach(keyword => {
      if (Math.random() < 0.2) {
        ineffectiveKeywords.push(keyword);
      }
    });

    if (ineffectiveKeywords.length > 0) {
      console.warn(`任务 ${taskId} 检测到无效关键词: ${ineffectiveKeywords.join(', ')}`);
    }

    return ineffectiveKeywords;
  }

  // 批量导入关键词
  importKeywords(taskId, file) {
    // 模拟分片上传处理
    console.log(`任务 ${taskId} 开始导入关键词文件`);

    // 模拟处理完成
    setTimeout(() => {
      console.log(`任务 ${taskId} 关键词导入完成`);
    }, 1000);
  }
}

/**
 * AI管理模块
 */
class AIManager {
  constructor() {
    this.industryModels = {
      '装修家居': { leadScoreWeight: { keyword: 0.6, content: 0.4 } },
      '美业医美': { leadScoreWeight: { keyword: 0.5, content: 0.5 } }
    };
    this.industryBlacklists = {
      '装修家居': ['设计师', '效果图', '案例分享'],
      '美业医美': ['医学科普', '护肤知识', '产品测评']
    };
    this.templateLibraries = {
      '咨询报价': {
        '装修家居': '您好，请问您需要装修哪部分？我可以为您提供详细报价。',
        '美业医美': '您好，请问您对哪个项目感兴趣？我们可以为您安排专业咨询。'
      },
      '对比产品': {
        '装修家居': '您好，我们提供多种装修方案，您更倾向于哪种风格？',
        '美业医美': '您好，我们有多款产品，您可以根据需求选择最适合的。'
      }
    };
  }

  // 行业意向打分
  calculateLeadScore(industry, content) {
    const model = this.industryModels[industry];
    if (!model) return 0.5; // 默认分数

    // 模拟打分逻辑
    let score = 0;

    // 检查行业黑名单
    const blacklist = this.industryBlacklists[industry] || [];
    const hasBlacklist = blacklist.some(word => content.includes(word));
    if (hasBlacklist) return 0.1; // 黑名单内容低分

    // 模拟打分计算
    score = Math.random() * 0.8 + 0.2;

    return Math.min(Math.max(score, 0), 1);
  }

  // 生成AI话术
  generateCopywriting(industry, scenario, location = '') {
    const template = this.templateLibraries[scenario]?.[industry] ||
      '您好，有什么可以帮您的？';

    // 填充地域变量
    if (location) {
      return template.replace('城市', location);
    }

    return template;
  }

  // 修正线索意向标签
  adjustLeadLabel(leadId, newLabel) {
    console.log(`修正线索 ${leadId} 意向标签为: ${newLabel}`);
  }
}

/**
 * 线索管理模块
 */
class LeadManager {
  constructor() {
    this.leads = new Map();
    this.deduplicationRules = {
      byUserId: true,
      byContent: true
    };
  }

  // 添加线索
  addLead(leadId, data) {
    // 去重检查
    if (this.checkDuplicate(data)) {
      console.log(`线索 ${leadId} 与已有线索重复`);
      return false;
    }

    const lead = {
      id: leadId,
      data,
      createdAt: new Date(),
      status: 'new',
      tags: [],
      followUps: [],
      locked: false
    };

    this.leads.set(leadId, lead);
    return true;
  }

  // 检查重复线索
  checkDuplicate(leadData) {
    const leads = Array.from(this.leads.values());

    if (this.deduplicationRules.byUserId && leadData.userId) {
      const duplicate = leads.find(lead =>
        lead.data.userId === leadData.userId
      );
      if (duplicate) return true;
    }

    if (this.deduplicationRules.byContent && leadData.content) {
      const duplicate = leads.find(lead =>
        lead.data.content === leadData.content
      );
      if (duplicate) return true;
    }

    return false;
  }

  // 合并重复线索
  mergeDuplicateLeads(targetId, sourceIds) {
    const target = this.leads.get(targetId);
    if (!target) return false;

    sourceIds.forEach(id => {
      const source = this.leads.get(id);
      if (source) {
        // 合并跟进记录
        target.followUps.push(...source.followUps);
        // 合并标签
        target.tags = [...new Set([...target.tags, ...source.tags])];
        // 删除源线索
        this.leads.delete(id);
      }
    });

    console.log(`合并线索: ${sourceIds.join(', ')} -> ${targetId}`);
    return true;
  }

  // 批量操作线索
  batchOperationLeads(leadIds, operation, params = {}) {
    leadIds.forEach(id => {
      const lead = this.leads.get(id);
      if (!lead) return;

      switch (operation) {
        case 'blacklist':
          lead.tags.push('blacklist');
          break;
        case 'favorite':
          lead.tags.push('favorite');
          break;
        case 'changeStatus':
          lead.status = params.status || 'unknown';
          break;
        case 'addNegativeKeyword':
          lead.tags.push(`negative:${params.keyword}`);
          break;
      }
    });

    console.log(`批量操作 ${leadIds.length} 条线索: ${operation}`);
  }

  // 分配线索给员工
  assignLead(leadId, employeeId) {
    const lead = this.leads.get(leadId);
    if (!lead) return false;

    lead.assignedTo = employeeId;
    lead.status = 'assigned';
    console.log(`线索 ${leadId} 分配给员工 ${employeeId}`);
    return true;
  }

  // 锁定线索
  lockLead(leadId) {
    const lead = this.leads.get(leadId);
    if (!lead) return false;

    lead.locked = true;
    console.log(`线索 ${leadId} 已锁定`);
    return true;
  }

  // 解锁线索
  unlockLead(leadId) {
    const lead = this.leads.get(leadId);
    if (!lead) return false;

    lead.locked = false;
    console.log(`线索 ${leadId} 已解锁`);
    return true;
  }
}

/**
 * 导出管理模块
 */
class ExportManager {
  constructor() {
    this.exportLimits = {
      free: 50,
      premium: 1000,
      enterprise: 10000
    };
    this.exportTemplates = [
      { id: 'basic', name: '基础信息', fields: ['name', 'phone', 'industry'] },
      { id: 'detailed', name: '详细信息', fields: ['name', 'phone', 'email', 'company', 'industry', 'notes'] }
    ];
  }

  // 导出线索
  exportLeads(leadIds, templateId = 'basic', format = 'excel') {
    const template = this.exportTemplates.find(t => t.id === templateId);
    if (!template) throw new Error('导出模板不存在');

    console.log(`开始导出 ${leadIds.length} 条线索，模板: ${template.name}，格式: ${format}`);

    // 模拟异步导出
    return new Promise((resolve) => {
      setTimeout(() => {
        const exportData = {
          id: `export_${Date.now()}`,
          leads: leadIds,
          template,
          format,
          downloadUrl: `/downloads/export_${Date.now()}.${format}`,
          status: 'completed'
        };

        console.log(`导出完成: ${exportData.downloadUrl}`);
        resolve(exportData);
      }, 2000);
    });
  }

  // 获取导出限制
  getExportLimit(userType) {
    return this.exportLimits[userType] || 50;
  }

  // 自定义导出模板
  createExportTemplate(templateId, name, fields) {
    const template = {
      id: templateId,
      name,
      fields,
      createdAt: new Date()
    };

    this.exportTemplates.push(template);
    console.log(`创建导出模板: ${name}`);
    return template;
  }
}

/**
 * 合规管理模块
 */
class ComplianceManager {
  constructor() {
    this.featureLocks = new Map();
    this.errorMessages = {
      '风控拦截': '检测到平台风控限制，请降低采集频率或更换关键词',
      '网络失败': '网络连接失败，请检查网络设置',
      '关键词无效': '关键词无效，请检查输入',
      '内存过载': '系统内存不足，请减少并发任务数'
    };
    this.compliancePopups = new Map();
  }

  // 锁定功能
  lockFeature(userId, feature) {
    if (!this.featureLocks.has(userId)) {
      this.featureLocks.set(userId, new Set());
    }

    this.featureLocks.get(userId).add(feature);
    console.log(`用户 ${userId} 功能 ${feature} 已锁定`);
  }

  // 解锁功能
  unlockFeature(userId, feature) {
    const locks = this.featureLocks.get(userId);
    if (locks) {
      locks.delete(feature);
      console.log(`用户 ${userId} 功能 ${feature} 已解锁`);
    }
  }

  // 检查功能权限
  checkFeatureAccess(userId, feature) {
    const locks = this.featureLocks.get(userId);
    return !locks || !locks.has(feature);
  }

  // 获取错误提示
  getErrorMessage(errorType) {
    return this.errorMessages[errorType] || '未知错误';
  }

  // 获取修复方案
  getFixSolution(errorType) {
    const solutions = {
      '风控拦截': '降低采集频率或更换关键词',
      '网络失败': '检查网络设置或稍后重试',
      '关键词无效': '修改关键词或使用系统推荐词',
      '内存过载': '减少并发任务数或清理缓存'
    };

    return solutions[errorType] || '请联系客服';
  }

  // 合规弹窗确认
  showCompliancePopup(userId, type) {
    const popupId = `${userId}_${type}_${Date.now()}`;
    this.compliancePopups.set(popupId, {
      userId,
      type,
      shown: true,
      confirmed: false
    });

    console.log(`显示合规弹窗: ${type} 给用户 ${userId}`);
    return popupId;
  }

  // 确认合规弹窗
  confirmCompliancePopup(popupId) {
    const popup = this.compliancePopups.get(popupId);
    if (popup) {
      popup.confirmed = true;
      console.log(`用户 ${popup.userId} 确认合规弹窗: ${popup.type}`);
    }
  }

  // 检查是否需要显示合规弹窗
  shouldShowCompliancePopup(userId, type) {
    // 检查本地缓存
    const cacheKey = `compliance_${userId}_${type}`;
    const cacheValue = localStorage.getItem(cacheKey);

    if (cacheValue === 'confirmed') {
      return false;
    }

    return true;
  }
}

/**
 * 行业管理模块
 */
class IndustryManager {
  constructor() {
    this.industrySpecificSolutions = {
      '本地生活': {
        filterTourists: true,
        residenceDetection: true
      },
      'B端财税/工程': {
        filterBloggers: true,
        blacklistWords: ['科普', '资讯', '教程']
      },
      '美业/教育': {
        distinguishInquiry: true,
        aiIntentAnalysis: true
      },
      '代运营/软件开发': {
        filterSelfLearners: true,
        negativeWords: ['源码', '教程', '自学']
      }
    };
  }

  // 应用行业特定解决方案
  applyIndustrySolution(industry, task) {
    const solution = this.industrySpecificSolutions[industry];
    if (!solution) return;

    console.log(`应用行业 ${industry} 特定解决方案`);

    // 应用行业特定过滤规则
    if (solution.filterTourists) {
      task.filters = task.filters || [];
      task.filters.push('isTourist');
    }

    if (solution.filterBloggers) {
      task.filters = task.filters || [];
      task.filters.push('isBlogger');
    }

    // 添加行业特定否定词
    if (solution.negativeWords) {
      task.negativeWords = task.negativeWords || [];
      task.negativeWords.push(...solution.negativeWords);
    }
  }

  // 获取行业词库
  getIndustryKeywords(industry) {
    return painPointSystem.industryKeywords[industry] || null;
  }
}

/**
 * 系统管理模块
 */
class SystemManager {
  constructor() {
    this.scheduledCleanup = null;
    this.versionUpdates = [];
    this.performanceAlerts = [];
  }

  // 定时清理数据
  scheduleDataCleanup() {
    // 每天凌晨清理过期数据
    this.scheduledCleanup = setInterval(() => {
      this.cleanupExpiredData();
      this.optimizeDatabase();
    }, 24 * 60 * 60 * 1000);

    console.log('已启动定时数据清理任务');
  }

  // 清理过期数据
  cleanupExpiredData() {
    console.log('开始清理过期数据...');
    // 模拟清理30天前的数据
    console.log('已清理30天前的过期数据');
  }

  // 数据库优化
  optimizeDatabase() {
    console.log('开始数据库优化...');
    // 模拟数据库优化
    console.log('数据库优化完成');
  }

  // 检查系统性能
  checkSystemPerformance() {
    const memoryUsage = process.memoryUsage();
    const cpuUsage = Math.random() * 100; // 模拟CPU使用率

    if (memoryUsage.heapUsed > 500 * 1024 * 1024 || cpuUsage > 80) {
      this.performanceAlerts.push({
        timestamp: new Date(),
        type: 'resource_overload',
        message: `系统资源紧张: 内存${(memoryUsage.heapUsed/1024/1024).toFixed(2)}MB, CPU${cpuUsage.toFixed(2)}%`
      });

      console.warn('系统资源紧张，建议降低并发任务数');
    }
  }

  // 处理版本更新
  handleVersionUpdate() {
    console.log('检测到新版本，开始更新...');
    // 模拟版本更新
    console.log('版本更新完成');
  }

  // 一键初始化系统
  initializeSystem() {
    console.log('开始系统初始化...');

    // 创建数据表
    this.createDatabaseTables();

    // 配置Redis
    this.configureRedis();

    // 加载行业词库
    this.loadIndustryKeywords();

    // 启动定时任务
    this.scheduleDataCleanup();

    console.log('系统初始化完成');
  }

  // 创建数据表
  createDatabaseTables() {
    console.log('创建数据表...');
    // 模拟创建表
    console.log('数据表创建完成');
  }

  // 配置Redis
  configureRedis() {
    console.log('配置Redis...');
    // 模拟Redis配置
    console.log('Redis配置完成');
  }

  // 加载行业词库
  loadIndustryKeywords() {
    console.log('加载行业词库...');
    // 已在主系统加载
    console.log('行业词库加载完成');
  }
}

// 初始化系统
const painPointSystem = new PainPointSolutionSystem();

// 导出模块
module.exports = {
  PainPointSolutionSystem,
  TaskManager,
  KeywordManager,
  AIManager,
  LeadManager,
  ExportManager,
  ComplianceManager,
  IndustryManager,
  SystemManager,
  painPointSystem
};
