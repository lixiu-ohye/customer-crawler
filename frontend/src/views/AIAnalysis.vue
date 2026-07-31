<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="10">
        <div class="page-card">
          <div class="page-title">单条线索分析</div>
          <el-select v-model="leadId" filterable placeholder="选择线索ID" style="width: 100%" class="mb16">
            <el-option v-for="l in leads" :key="l.id" :label="`#${l.id} ${(l.title || '').slice(0, 30)}`" :value="l.id" />
          </el-select>
          <el-button type="primary" :disabled="!leadId" :loading="analyzing" @click="analyze">开始分析</el-button>

          <template v-if="analysis">
            <el-divider />
            <div class="analyze-block">
              <div class="analyze-label">📌 需求摘要</div>
              <p>{{ analysis.summary }}</p>
            </div>
            <div class="analyze-block">
              <div class="analyze-label">😀 语义筛查</div>
              <el-tag :type="analysis.sentiment.keep ? 'success' : 'danger'" size="small">
                {{ analysis.sentiment.keep ? '保留' : '过滤' }}
              </el-tag>
              <span style="margin-left: 8px; font-size: 13px">{{ analysis.sentiment.reason }}</span>
            </div>
            <div class="analyze-block">
              <div class="analyze-label">💬 触达话术</div>
              <p class="script-text">{{ analysis.script.full }}</p>
              <el-button size="small" @click="copyScript(analysis.script.full)">复制话术</el-button>
            </div>
          </template>
        </div>
      </el-col>

      <el-col :span="14">
        <div class="page-card">
          <div class="flex-between mb16">
            <div class="page-title" style="margin-bottom: 0">批量重筛</div>
          </div>
          <el-form inline>
            <el-form-item label="最低分">
              <el-input-number v-model="rescreenForm.min_score" :min="0" :max="100" />
            </el-form-item>
            <el-form-item label="最多处理">
              <el-input-number v-model="rescreenForm.max_count" :min="10" :max="5000" :step="50" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="rescreening" @click="doRescreen">开始重筛</el-button>
            </el-form-item>
          </el-form>
          <el-alert type="warning" :closable="false"
            title="批量重筛将按最新算法重新为所有线索打分，低于最低分的线索将被标记为已过滤。此操作会覆盖原有分数。" />

          <el-divider />
          <div class="flex-between">
            <div class="analyze-label">📋 线索列表（点击分析）</div>
            <el-button size="small" @click="loadLeads">刷新</el-button>
          </div>
          <el-table :data="leads" size="small" max-height="420" highlight-current-row @current-change="r => leadId = r?.id">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
            <el-table-column prop="intent_score" label="意向分" width="80" />
            <el-table-column prop="region" label="地域" width="90" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const leads = ref([])
const leadId = ref(null)
const analysis = ref(null)
const analyzing = ref(false)
const rescreening = ref(false)
const rescreenForm = reactive({ min_score: 40, max_count: 500 })

const loadLeads = async () => {
  const data = await api.get('/leads/', { params: { page_size: 50 } })
  leads.value = data.results
}

const analyze = async () => {
  if (!leadId.value) return
  analyzing.value = true
  try {
    const data = await api.get(`/analysis/lead/${leadId.value}`)
    analysis.value = data.result
  } finally {
    analyzing.value = false
  }
}

const doRescreen = async () => {
  rescreening.value = true
  try {
    const data = await api.post('/analysis/rescreen', rescreenForm)
    ElMessage.success(`重筛完成，共处理 ${data.result.updated} 条线索`)
    loadLeads()
  } finally {
    rescreening.value = false
  }
}

const copyScript = async text => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('话术已复制')
  } catch {
    ElMessage.warning('复制失败，请手动选择复制')
  }
}

onMounted(loadLeads)
</script>

<style scoped>
.mb16 { margin-bottom: 16px; }
.analyze-block { margin-bottom: 16px; }
.analyze-label { font-size: 13px; font-weight: 600; color: #606266; margin-bottom: 8px; }
.script-text { background: #f5f7fa; padding: 12px; border-radius: 6px; line-height: 1.7; font-size: 13px; color: #303133; }
</style>
