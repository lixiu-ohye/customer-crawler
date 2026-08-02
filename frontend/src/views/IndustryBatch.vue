<template>
  <div class="industry-batch">
    <!-- 头部说明 -->
    <el-card class="mb16" shadow="never">
      <div class="batch-head">
        <div>
          <h3 class="title">行业关键词批量自动采集</h3>
          <p class="desc">从 12 大行业词库自动提取主词 + 长尾词 → 批量启动爬虫 → 完成后自动导入客户线索库（高意向优先）</p>
        </div>
        <el-button type="primary" :icon="VideoPlay" @click="openStart">启动批量采集</el-button>
      </div>
    </el-card>

    <!-- 批量任务列表 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-head">
          <span>批量采集任务</span>
          <el-button size="small" :icon="Refresh" @click="loadBatches">刷新</el-button>
        </div>
      </template>

      <el-empty v-if="!batches.length" description="暂无批量采集任务，点击右上角启动" />

      <el-table v-else :data="batches" stripe>
        <el-table-column prop="batch_id" label="批次" width="100" />
        <el-table-column prop="industry" label="行业" width="160" />
        <el-table-column label="平台" width="120">
          <template #default="{ row }">
            <el-tag v-for="p in row.platforms" :key="p" size="small" class="mr4">{{ p }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" min-width="200">
          <template #default="{ row }">
            <el-progress
              :percentage="row.total_keywords ? Math.round(row.completed_keywords / row.total_keywords * 100) : 0"
              :status="row.status === 'completed' ? 'success' : (row.status === 'running' ? '' : 'exception')"
            />
            <span class="progress-txt">{{ row.completed_keywords }}/{{ row.total_keywords }} 关键词</span>
          </template>
        </el-table-column>
        <el-table-column prop="imported_count" label="已入库线索" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : (row.status === 'running' ? 'warning' : 'info')" size="small">
              {{ row.status === 'completed' ? '已完成' : (row.status === 'running' ? '采集中' : row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ row.created_at }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 启动对话框 -->
    <el-dialog v-model="startVisible" title="启动行业批量采集" width="520px">
      <el-form label-width="90px">
        <el-form-item label="选择行业" required>
          <el-select v-model="form.industry" placeholder="选择行业" filterable style="width: 100%">
            <el-option
              v-for="ind in options.industries"
              :key="ind.name"
              :label="`${ind.name}（${ind.word_count} 词）`"
              :value="ind.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="采集平台" required>
          <el-select v-model="form.platforms" multiple placeholder="选择平台" style="width: 100%">
            <el-option v-for="p in options.platforms" :key="p.code" :label="p.name" :value="p.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词数">
          <el-slider v-model="form.max_keywords" :min="1" :max="15" show-input />
        </el-form-item>
        <el-form-item>
          <el-alert type="info" :closable="false" show-icon>
            <p>采集需平台扫码登录（微博/抖音等）。任务完成后自动导入线索库并按意向分排序。</p>
          </el-alert>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="startVisible = false">取消</el-button>
        <el-button type="primary" :loading="starting" @click="startBatch">启动采集</el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailVisible" :title="`批次 ${detail.batch_id || ''} 详情`" size="560px">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="行业">{{ detail.industry }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ detail.status }}</el-descriptions-item>
        <el-descriptions-item label="关键词数">{{ detail.total_keywords }}</el-descriptions-item>
        <el-descriptions-item label="已入库">{{ detail.imported_count }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="detail.sub_tasks || []" size="small" stripe class="mt16">
        <el-table-column prop="keyword" label="关键词" min-width="110" />
        <el-table-column prop="platform" label="平台" width="90" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : (row.status === 'failed' ? 'danger' : 'warning')" size="small">
              {{ row.status === 'completed' ? '完成' : (row.status === 'failed' ? '失败' : (row.status === 'running' ? '采集中' : '等待')) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="result_count" label="采集数" width="70" />
        <el-table-column prop="import_result" label="入库" width="70" />
      </el-table>
      <div v-if="detail.error" class="err-txt mt8">{{ detail.error }}</div>
    </el-drawer>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, VideoPlay } from '@element-plus/icons-vue'
import api from '../api'

const batches = ref([])
const startVisible = ref(false)
const detailVisible = ref(false)
const starting = ref(false)
const detail = ref({})

const form = reactive({ industry: '', platforms: ['weibo'], max_keywords: 8 })
const options = reactive({ industries: [], platforms: [] })

async function loadBatches() {
  try {
    const { data } = await api.get('/crawler/industry/batch')
    batches.value = data.batches || []
  } catch (e) {
    // mock 或后端不可用时静默
    batches.value = []
  }
}

async function loadOptions() {
  try {
    const { data } = await api.get('/crawler/industry/options')
    options.industries = data.results?.industries || []
    options.platforms = data.results?.platforms || []
  } catch (e) {
    // fallback 演示
    options.industries = [
      { name: '法律行业', word_count: 20 },
      { name: '装修家居', word_count: 13 },
      { name: '企业B端财税商务服务', word_count: 9 },
      { name: '教育培训', word_count: 11 },
    ]
    options.platforms = [
      { code: 'weibo', name: '微博' }, { code: 'douyin', name: '抖音' },
      { code: 'xiaohongshu', name: '小红书' }, { code: 'zhihu', name: '知乎' },
    ]
  }
}

function openStart() {
  form.industry = options.industries[0]?.name || ''
  form.platforms = ['weibo']
  startVisible.value = true
}

async function startBatch() {
  if (!form.industry) { ElMessage.warning('请选择行业'); return }
  if (!form.platforms.length) { ElMessage.warning('请选择平台'); return }
  starting.value = true
  try {
    const { data } = await api.post('/crawler/industry/batch', {
      industry: form.industry,
      platforms: form.platforms,
      max_keywords: form.max_keywords,
    })
    ElMessage.success(data.message || '已启动批量采集')
    startVisible.value = false
    loadBatches()
    // 轮询刷新
    startPolling()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '启动失败')
  } finally {
    starting.value = false
  }
}

function openDetail(row) {
  detail.value = row
  detailVisible.value = true
}

let pollTimer = null
function startPolling() {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(loadBatches, 5000)
  // 10 分钟后停止轮询
  setTimeout(() => { if (pollTimer) { clearInterval(pollTimer); pollTimer = null } }, 600000)
}

onMounted(() => {
  loadBatches()
  loadOptions()
})
</script>

<style scoped>
.mb16 { margin-bottom: 16px; }
.mr4 { margin-right: 4px; }
.mt16 { margin-top: 16px; }
.mt8 { margin-top: 8px; }
.title { margin: 0 0 6px; font-size: 18px; }
.desc { margin: 0; color: #909399; font-size: 13px; line-height: 1.6; }
.batch-head { display: flex; justify-content: space-between; align-items: center; }
.card-head { display: flex; justify-content: space-between; align-items: center; }
.progress-txt { font-size: 12px; color: #909399; margin-left: 8px; }
.err-txt { color: #f56c6c; font-size: 12px; }
</style>
