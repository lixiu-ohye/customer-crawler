<template>
  <div class="real-leads">
    <div class="page-header">
      <h2>真实数据线索库</h2>
      <p class="sub">来自 MediaCrawler 扫码采集的真实平台数据（已脱敏、合规导入）</p>
      <div class="actions">
        <el-autocomplete
          v-model="keyword"
          :fetch-suggestions="querySuggestions"
          placeholder="搜索关键词（如：牙齿、装修）"
          clearable
          style="width: 220px; margin-right: 10px"
          @select="load"
          @keyup.enter="load"
        >
          <template #prefix><span class="search-icon">🔍</span></template>
        </el-autocomplete>
        <el-select v-model="industry" placeholder="行业筛选" clearable filterable style="width: 160px; margin-right: 10px">
          <el-option v-for="ind in INDUSTRY_OPTIONS" :key="ind" :label="ind" :value="ind" />
        </el-select>
        <el-select v-model="platform" placeholder="平台筛选" clearable style="width: 130px; margin-right: 10px">
          <el-option label="抖音" value="douyin" />
          <el-option label="微博" value="weibo" />
          <el-option label="贴吧" value="tieba" />
          <el-option label="小红书" value="xiaohongshu" />
          <el-option label="快手" value="kuaishou" />
          <el-option label="知乎" value="zhihu" />
        </el-select>
        <el-select v-model="custFilter" placeholder="客户筛选" clearable style="width: 140px; margin-right: 10px">
          <el-option label="✅ 仅看客户" value="customer" />
          <el-option label="❌ 仅看非客户" value="not_customer" />
          <el-option label="⏳ 未分类" value="unclassified" />
        </el-select>
        <el-button type="primary" :loading="importing" @click="doImport">导入数据</el-button>
        <el-button :loading="loading" @click="load">刷新</el-button>
      </div>
      <div class="stat-row" style="margin-top: 10px">
        <el-tag type="info" size="small">共 {{ total }} 条真实数据</el-tag>
        <el-tag type="danger" size="small">客户 {{ customerCount }} 条</el-tag>
        <el-tag type="success" size="small" v-if="industry">行业：{{ industry }}</el-tag>
        <span class="sub" style="margin-left: 8px">客户 = GLM 判定有真实需求、非营销号、有跟进价值</span>
      </div>
    </div>

    <el-alert
      v-if="lastResult"
      :title="lastResult"
      type="success"
      show-icon
      closable
      style="margin-bottom: 14px"
    />

    <el-table :data="rows" v-loading="loading" border stripe class="lead-table">
      <el-table-column type="index" label="#" width="50" />
      <el-table-column prop="intent_score" label="意向分" width="75" sortable>
        <template #default="{ row }">
          <el-tag :type="scoreType(row.intent_score)" size="small">{{ row.intent_score }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="客户" width="85">
        <template #default="{ row }">
          <el-tag v-if="row.is_customer === true" type="danger" size="small">客户</el-tag>
          <el-tag v-else-if="row.is_customer === false" type="info" size="small">非客户</el-tag>
          <el-tag v-else type="warning" size="small">待定</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="行业" width="130" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.industry || '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="platform_name" label="平台" width="80" />
      <el-table-column prop="content" label="内容" min-width="260" show-overflow-tooltip />
      <el-table-column prop="author" label="作者" width="90" show-overflow-tooltip />
      <el-table-column label="互动" width="90" sortable :sort-by="row => row.like_count + row.comment_count + row.share_count">
        <template #default="{ row }">
          <span class="interact">{{ (row.like_count || 0) + (row.comment_count || 0) + (row.share_count || 0) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="region" label="地区" width="80" show-overflow-tooltip />
      <el-table-column prop="publish_time" label="发布时间" width="150" />
      <el-table-column label="原文" width="70">
        <template #default="{ row }">
          <el-link type="primary" :href="row.url" target="_blank" underline="never">查看</el-link>
        </template>
      </el-table-column>
      <el-table-column label="跟进" width="150">
        <template #default="{ row }">
          <el-tag v-if="row.crm_status === 'follow'" type="primary" size="small">跟进中</el-tag>
          <el-tag v-else-if="row.crm_status === 'deal'" type="success" size="small">已成交</el-tag>
          <el-tag v-else-if="row.crm_status === 'sea'" type="warning" size="small">公海中</el-tag>
          <el-tag v-else-if="row.crm_status === 'abandon'" type="info" size="small">已放弃</el-tag>
          <el-tag v-else type="default" size="small">未跟进</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button v-if="row.crm_status !== 'follow'" size="small" type="primary" plain @click="crmSet(row, 'follow')">跟进</el-button>
          <el-button v-if="row.crm_status === 'follow'" size="small" type="success" plain @click="crmSet(row, 'deal')">成交</el-button>
          <el-button v-if="row.crm_status !== 'sea'" size="small" type="warning" plain @click="crmSet(row, 'sea')">转公海</el-button>
          <el-button v-if="row.crm_status === 'sea'" size="small" @click="crmSet(row, 'new')">回收</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt12">
      <el-button size="small" :loading="seaLoading" @click="loadSea">公海回收站</el-button>
      <span class="sub" style="margin-left: 8px">公海 = 超过跟进时限自动回收的线索，可重新领取</span>
    </div>

    <el-empty v-if="!loading && rows.length === 0" description="暂无真实数据，请先运行采集任务并导入" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const rows = ref([])
const total = ref(0)
const loading = ref(false)
const importing = ref(false)
const keyword = ref('')
const industry = ref('宠物行业')
const platform = ref('')
const custFilter = ref('customer')
const lastResult = ref('')

const INDUSTRY_OPTIONS = ['装修家居', '法律行业', '美业医美', '本地生活家政服务', '汽车服务行业', '教育培训', '宠物行业', '房产同城服务', '婚庆摄影', '口腔健康理疗', '工程建材行业', '互联网服务商', '企业B端财税商务服务']

const scoreType = s => (s >= 60 ? 'danger' : s >= 40 ? 'warning' : 'info')
const intentText = l => ({ high: '高意向', medium: '中意向', low: '低意向', none: '无意向' }[l] || l)
const customerCount = computed(() => rows.value.filter(r => r.is_customer === true).length)

// 搜索联想：从当前已加载数据生成建议
const querySuggestions = (query, cb) => {
  const q = (query || '').trim().toLowerCase()
  if (!q) return cb([])
  const seen = new Set()
  const list = []
  rows.value.forEach(r => {
    const fields = [r.title, r.content, r.needs, r.industry].filter(Boolean)
    fields.forEach(f => {
      const s = String(f).trim()
      if (s.toLowerCase().includes(q) && !seen.has(s) && list.length < 8) {
        seen.add(s)
        list.push({ value: s.length > 40 ? s.slice(0, 40) + '…' : s })
      }
    })
  })
  cb(list)
}

const load = async () => {
  loading.value = true
  try {
    const params = {}
    if (keyword.value) params.keyword = keyword.value
    if (industry.value) params.industry = industry.value
    if (platform.value) params.platform = platform.value
    const r = await api.get('/crawler/realleads', { params: { ...params, limit: 200 } })
    let list = r.results || []
    // 客户筛选在前端做（mock 与真实后端字段一致）
    if (custFilter.value === 'customer') list = list.filter(x => x.is_customer === true)
    else if (custFilter.value === 'not_customer') list = list.filter(x => x.is_customer === false)
    else if (custFilter.value === 'unclassified') list = list.filter(x => x.is_customer === null || x.is_customer === undefined)
    rows.value = list
    total.value = r.total || list.length
  } catch (e) {
    ElMessage.error('加载真实数据失败：' + (e.message || e))
  } finally {
    loading.value = false
  }
}

const doImport = async () => {
  if (!keyword.value || !keyword.value.trim()) {
    ElMessage.warning('请先填写采集关键词（如：装修、法律咨询、全屋定制）')
    importing.value = false
    return
  }
  try {
    const r = await api.post('/crawler/mediacrawler/import', { keyword: keyword.value })
    lastResult.value = r.message || `导入完成：新增 ${r.imported} 条，跳过重复 ${r.skipped_dup} 条`
    ElMessage.success(lastResult.value)
    load()
  } catch (e) {
    ElMessage.error('导入失败：' + (e.message || e))
  } finally {
    importing.value = false
  }
}

// ---------- CRM 跟进 ----------
const seaLoading = ref(false)
const crmSet = async (row, status) => {
  try {
    await api.post('/crm/status', { id: row.id, status })
    const map = { follow: '已标记跟进中', deal: '已标记成交 🎉', sea: '已转入公海', new: '已回收', abandon: '已放弃' }
    ElMessage.success(map[status] || '已更新')
    load()
  } catch (e) {
    ElMessage.error('更新失败：' + (e.message || e))
  }
}

const loadSea = async () => {
  seaLoading.value = true
  try {
    const r = await api.get('/crm/sea', { params: { limit: 50 } })
    const list = r.results || []
    if (!list.length) {
      ElMessage.info('公海暂无线索')
      return
    }
    ElMessageBox.confirm(
      `公海现有 ${list.length} 条线索，点击「回收」可重新领取第一条。`,
      '公海回收站', { type: 'info', confirmButtonText: '回收第一条', cancelButtonText: '关闭' }
    ).then(async () => {
      await api.post('/crm/sea', { id: list[0].id })
      ElMessage.success('已回收一条线索')
      load()
    }).catch(() => {})
  } catch (e) {
    ElMessage.error('公海加载失败：' + (e.message || e))
  } finally {
    seaLoading.value = false
  }
}

onMounted(() => {
  // 支持全局搜索跳转参数（关键词 / 行业）
  if (route.query.kw) keyword.value = String(route.query.kw)
  if (route.query.industry) industry.value = String(route.query.industry)
  load()
})

// 监听 mock 层真实数据加载完成事件，触发刷新
const onRealDataReady = () => { load() }
window.addEventListener('mock:realDataReady', onRealDataReady)
onUnmounted(() => { window.removeEventListener('mock:realDataReady', onRealDataReady) })
</script>

<style scoped>
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px; }
.sub { color: #909399; font-size: 13px; margin: 0 0 12px; }
.actions { display: flex; align-items: center; flex-wrap: wrap; gap: 0; }
.stat-row { display: flex; align-items: center; gap: 8px; }
.intent-high { color: #f56c6c; font-weight: 600; }
.intent-medium { color: #e6a23c; }
.intent-low { color: #909399; }
.interact { font-weight: 600; color: #606266; }
.search-icon { font-size: 13px; }
.lead-table :deep(.el-table__body-wrapper) { overflow-x: auto; }
.mt12 { margin-top: 12px; }
</style>
