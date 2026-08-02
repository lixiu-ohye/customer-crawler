<template>
  <div>
    <div class="page-card">
      <div class="flex-between">
        <div class="flex" style="gap: 8px; flex-wrap: wrap">
          <el-input v-model="filters.keyword" placeholder="搜索关键词" clearable style="width: 160px" @keyup.enter="load" />
          <el-select v-model="filters.platform" placeholder="平台" clearable style="width: 110px" @change="load">
            <el-option v-for="(v, k) in platformMap" :key="k" :label="v" :value="k" />
          </el-select>
          <el-select v-model="filters.industry" placeholder="行业" clearable filterable style="width: 150px" @change="onIndustryChange">
            <el-option v-for="ind in industries" :key="ind" :label="ind" :value="ind" />
          </el-select>
          <el-select v-model="filters.scene" placeholder="场景/领域" clearable filterable style="width: 140px" @change="load">
            <el-option v-for="s in scenes" :key="s" :label="s" :value="s" />
          </el-select>
          <el-select v-model="filters.region" placeholder="地域" clearable filterable style="width: 120px" @change="load">
            <el-option v-for="r in regions" :key="r" :label="r" :value="r" />
          </el-select>
          <el-select v-model="filters.intent" placeholder="意向" clearable style="width: 110px" @change="load">
            <el-option v-for="(v, k) in intentMap" :key="k" :label="v" :value="k" />
          </el-select>
          <el-checkbox v-model="filters.real" label="仅真实数据" @change="load" />
          <el-button type="primary" @click="load">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </div>
        <el-button type="success" :loading="exporting" @click="exportXlsx">导出 Excel</el-button>
      </div>

      <el-table :data="list" v-loading="loading" class="mt16" stripe>
        <el-table-column prop="title" label="标题/正文" min-width="220" show-overflow-tooltip />
        <el-table-column prop="author" label="作者" width="100" />
        <el-table-column label="平台" width="90">
          <template #default="{ row }"><el-tag size="small">{{ platformMap[row.platform] || row.platform }}</el-tag></template>
        </el-table-column>
        <el-table-column label="意向分" width="120" sortable prop="intent_score">
          <template #default="{ row }">
            <el-progress :percentage="row.intent_score" :stroke-width="8" :color="scoreColor(row.intent_score)" />
          </template>
        </el-table-column>
        <el-table-column label="意向" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="intentTagType(row.intent_label)">{{ intentMap[row.intent_label] || row.intent_label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="行业" width="110">
          <template #default="{ row }"><span class="tag-text">{{ industryOf(row) }}</span></template>
        </el-table-column>
        <el-table-column prop="demand" label="场景/领域" width="100" />
        <el-table-column prop="region" label="地域" width="90" />
        <el-table-column label="来源" width="90">
          <template #default="{ row }">
            <el-tag v-if="isReal(row)" size="small" type="success">真实数据</el-tag>
            <el-tag v-else size="small" type="info">演示</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="原文链接" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link v-if="row.url" type="primary" :href="row.url" target="_blank">{{ row.url.slice(0, 26) }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="入库时间" width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row)">详情</el-button>
            <el-button size="small" type="warning" plain @click="blacklist(row)">拉黑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="flex-between mt16">
        <span style="color: #909399; font-size: 13px">共 {{ total }} 条</span>
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="load"
        />
      </div>
    </div>

    <el-dialog v-model="detailVisible" title="线索详情" width="640px">
      <template v-if="current">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="作者">{{ current.author }}</el-descriptions-item>
          <el-descriptions-item label="平台">{{ platformMap[current.platform] }}</el-descriptions-item>
          <el-descriptions-item label="意向分">{{ current.intent_score }}（{{ intentMap[current.intent_label] }}）</el-descriptions-item>
          <el-descriptions-item label="地域">{{ current.region }}</el-descriptions-item>
          <el-descriptions-item label="场景/领域">{{ current.demand }}</el-descriptions-item>
          <el-descriptions-item label="入库时间">{{ current.created_at }}</el-descriptions-item>
        </el-descriptions>
        <div class="detail-content">
          <div class="detail-label">正文内容</div>
          <p>{{ current.summary || current.content }}</p>
        </div>
        <div v-if="current.tags && current.tags.length" class="detail-content">
          <div class="detail-label">标签</div>
          <el-tag v-for="t in current.tags" :key="t" size="small" style="margin-right: 6px">{{ t }}</el-tag>
        </div>
        <div class="detail-content">
          <div class="detail-label">备注</div>
          <el-input v-model="current.note" placeholder="填写备注..." @change="saveNote(current)" />
        </div>
        <el-button v-if="current.url" type="primary" link :href="current.url" target="_blank" class="mt16">查看原文 →</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const exporting = ref(false)
const page = ref(1)
const pageSize = 20
const detailVisible = ref(false)
const current = ref(null)
const industries = ref([])
const scenes = ref([])
const regions = ref([])
const filters = reactive({ keyword: '', platform: '', intent: '', region: '', industry: '', scene: '', real: false })

const platformMap = { douyin: '抖音', xiaohongshu: '小红书', kuaishou: '快手', weibo: '微博', zhihu: '知乎', tieba: '贴吧' }
const intentMap = { high: '高意向', medium: '中意向', low: '低意向', none: '无意向' }

const scoreColor = s => (s >= 60 ? '#67C23A' : s >= 30 ? '#E6A23C' : '#F56C6C')
const intentTagType = l => ({ high: 'danger', medium: 'warning', low: 'info', none: 'info' }[l] || 'info')
const isReal = row => (row.tags || []).some(t => t === '真实数据')
const industryOf = row => (row.tags || []).find(t => t !== '微博' && t !== '真实数据' && t !== row.demand && t !== row.region) || ''

const load = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize, ...filters }
    Object.keys(params).forEach(k => !params[k] && params[k] !== false && delete params[k])
    if (params.real) params.real = '1'
    else delete params.real
    const data = await api.get('/leads/', { params })
    list.value = data.results
    total.value = data.total
    industries.value = data.industries || industries.value
    scenes.value = data.scenes || scenes.value
    regions.value = data.regions || regions.value
  } catch (e) {
    ElMessage.error('加载线索失败：' + (e.message || e))
  } finally {
    loading.value = false
  }
}

const onIndustryChange = () => {
  // 行业改变时，把场景联动清空（行业已覆盖场景）
  filters.scene = ''
  load()
}

const reset = () => {
  Object.assign(filters, { keyword: '', platform: '', intent: '', region: '', industry: '', scene: '', real: false })
  page.value = 1
  load()
}

const openDetail = row => {
  current.value = row
  detailVisible.value = true
}

const saveNote = async row => {
  await api.put(`/leads/${row.id}`, { note: row.note })
  ElMessage.success('备注已保存')
}

const blacklist = async row => {
  await ElMessageBox.confirm(`确定拉黑「${row.title.slice(0, 20)}」？拉黑后将不再出现在查询中。`, '拉黑确认', { type: 'warning' })
  await api.put(`/leads/${row.id}`, { is_blacklisted: true })
  ElMessage.success('已拉黑')
  load()
}

const exportXlsx = async () => {
  exporting.value = true
  try {
    const params = { ...filters }
    Object.keys(params).forEach(k => !params[k] && params[k] !== false && delete params[k])
    if (params.real) params.real = '1'
    else delete params.real
    const resp = await api.get('/leads/export', { params, responseType: 'blob' })
    const blob = new Blob([resp], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `客户线索_${new Date().toISOString().slice(0, 10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.detail-content { margin-top: 16px; }
.detail-label { font-size: 13px; color: #909399; margin-bottom: 8px; font-weight: 600; }
.mt16 { margin-top: 16px; }
.tag-text { color: #409eff; font-size: 13px; }
</style>
