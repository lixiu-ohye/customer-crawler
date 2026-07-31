<template>
  <div>
    <div class="page-card">
      <div class="flex-between">
        <div class="flex" style="gap: 8px; flex-wrap: wrap">
          <el-input v-model="filters.keyword" placeholder="搜索关键词" clearable style="width: 160px" @keyup.enter="load" />
          <el-select v-model="filters.platform" placeholder="全部平台" clearable style="width: 120px" @change="load">
            <el-option v-for="(v, k) in platformMap" :key="k" :label="v" :value="k" />
          </el-select>
          <el-select v-model="filters.intent" placeholder="全部意向" clearable style="width: 120px" @change="load">
            <el-option v-for="(v, k) in intentMap" :key="k" :label="v" :value="k" />
          </el-select>
          <el-select v-model="filters.region" placeholder="全部地域" clearable filterable style="width: 140px" @change="load">
            <el-option v-for="r in regions" :key="r" :label="r" :value="r" />
          </el-select>
          <el-button type="primary" @click="load">筛选</el-button>
          <el-button @click="reset">重置</el-button>
        </div>
        <el-button type="success" :loading="exporting" @click="exportXlsx">导出 Excel</el-button>
      </div>

      <el-table :data="list" v-loading="loading" class="mt16" stripe>
        <el-table-column prop="title" label="标题/内容" min-width="220" show-overflow-tooltip />
        <el-table-column prop="author" label="作者" width="110" />
        <el-table-column label="平台" width="90">
          <template #default="{ row }"><el-tag size="small">{{ platformMap[row.platform] || row.platform }}</el-tag></template>
        </el-table-column>
        <el-table-column label="意向分" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.intent_score" :stroke-width="8" :color="scoreColor(row.intent_score)" />
          </template>
        </el-table-column>
        <el-table-column prop="region" label="地域" width="100" />
        <el-table-column prop="demand" label="需求标签" width="110" />
        <el-table-column prop="url" label="原文链接" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link v-if="row.url" type="primary" :href="row.url" target="_blank">{{ row.url.slice(0, 30) }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="采集时间" width="160" />
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
          <el-descriptions-item label="意向分">{{ current.intent_score }}</el-descriptions-item>
          <el-descriptions-item label="地域">{{ current.region }}</el-descriptions-item>
          <el-descriptions-item label="需求标签">{{ current.demand }}</el-descriptions-item>
          <el-descriptions-item label="采集时间">{{ current.created_at }}</el-descriptions-item>
        </el-descriptions>
        <div class="detail-content">
          <div class="detail-label">内容摘要</div>
          <p>{{ current.summary || current.content }}</p>
        </div>
        <div class="detail-content">
          <div class="detail-label">备注</div>
          <el-input v-model="current.note" placeholder="添加备注..." @change="saveNote(current)" />
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
const regions = ref([])
const filters = reactive({ keyword: '', platform: '', intent: '', region: '' })

const platformMap = { douyin: '抖音', xiaohongshu: '小红书', kuaishou: '快手', weibo: '微博', zhihu: '知乎', tieba: '贴吧' }
const intentMap = { high: '高意向', medium: '中意向', low: '低意向', none: '无意向' }

const scoreColor = s => (s >= 60 ? '#67C23A' : s >= 30 ? '#E6A23C' : '#F56C6C')

const load = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize, ...filters }
    Object.keys(params).forEach(k => !params[k] && delete params[k])
    const data = await api.get('/leads/', { params })
    list.value = data.results
    total.value = data.total
    regions.value = data.regions || regions.value
  } finally {
    loading.value = false
  }
}

const reset = () => {
  Object.assign(filters, { keyword: '', platform: '', intent: '', region: '' })
  page.value = 1
  load()
}

const openDetail = row => {
  current.value = row
  detailVisible.value = true
}

const saveNote = async row => {
  await api.post(`/leads/${row.id}`, { action: 'note', note: row.note })
  ElMessage.success('备注已保存')
}

const blacklist = async row => {
  await ElMessageBox.confirm(`确定拉黑该线索？拉黑后不再出现在筛选中。`, '提示', { type: 'warning' })
  await api.post(`/leads/${row.id}`, { action: 'blacklist' })
  ElMessage.success('已拉黑')
  load()
}

const exportXlsx = async () => {
  exporting.value = true
  try {
    const resp = await api.get('/leads/export', { params: filters, responseType: 'blob' })
    const blob = new Blob([resp], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `线索导出_${new Date().toISOString().slice(0, 10)}.xlsx`
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
</style>
