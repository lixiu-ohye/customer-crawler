<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="10">
        <div class="page-card">
          <div class="page-title">个人资料</div>
          <el-form label-width="80px" :model="profile">
            <el-form-item label="用户名">
              <el-input v-model="profile.username" disabled />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="profile.nickname" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profile.email" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="profile.phone" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="saveProfile">保存资料</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <el-col :span="14">
        <div class="page-card">
          <div class="flex-between mb16">
            <div class="page-title" style="margin-bottom: 0">当前套餐</div>
            <el-button type="primary" size="small" @click="upgrade">升级套餐</el-button>
          </div>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="套餐">
              <el-tag type="success">{{ planName }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="线索配额">{{ plan.quota_used }}/{{ plan.quota_total }}</el-descriptions-item>
            <el-descriptions-item label="到期时间">{{ plan.expire_at || '永久' }}</el-descriptions-item>
            <el-descriptions-item label="任务并发">{{ plan.concurrent_tasks }}</el-descriptions-item>
            <el-descriptions-item label="每日采集上限">{{ plan.daily_crawl_limit }}</el-descriptions-item>
            <el-descriptions-item label="评论采集">{{ plan.allow_comments ? '已开通' : '未开通' }}</el-descriptions-item>
            <el-descriptions-item label="子账号">{{ plan.sub_accounts || 0 }} 个</el-descriptions-item>
            <el-descriptions-item label="CRM">{{ plan.crm || '未开通' }}</el-descriptions-item>
            <el-descriptions-item label="API 模式">{{ plan.api_access ? '已开通' : '未开通' }}</el-descriptions-item>
          </el-descriptions>

          <el-progress class="mt16" :percentage="quotaPercent" :stroke-width="14" color="#409EFF">
            <span>线索配额使用率</span>
          </el-progress>
        </div>

        <div class="page-card mt16">
          <div class="page-title">操作日志</div>
          <el-table :data="logs" size="small" max-height="280">
            <el-table-column prop="action" label="操作" min-width="160" />
            <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" width="160" />
          </el-table>
        </div>
      </el-col>
    </el-row>

    <el-dialog v-model="upgradeVisible" title="升级套餐" width="640px">
      <el-table :data="plans" highlight-current-row @current-change="r => selectedPlan = r">
        <el-table-column prop="name" label="套餐" width="120" />
        <el-table-column label="价格" width="110">
          <template #default="{ row }"><span>{{ row.price === 0 ? '免费' : '¥' + row.price + '/月' }}</span></template>
        </el-table-column>
        <el-table-column label="每日线索" width="100">
          <template #default="{ row }"><span>{{ row.features.daily_leads }} 条</span></template>
        </el-table-column>
        <el-table-column label="渠道" width="90">
          <template #default="{ row }"><span>{{ row.features.channels }} 个</span></template>
        </el-table-column>
        <el-table-column label="评论采集" width="90">
          <template #default="{ row }"><span>{{ row.features.allow_comments ? '支持' : '禁' }}</span></template>
        </el-table-column>
        <el-table-column label="关键词" width="90">
          <template #default="{ row }"><span>{{ row.features.keyword_limit === -1 ? '不限' : row.features.keyword_limit }}</span></template>
        </el-table-column>
        <el-table-column prop="tag" label="定位" width="90" />
      </el-table>
      <div class="mt8" style="color: #909399; font-size: 12px; line-height: 1.6">
        <div v-for="(v, k) in selectedPlan?.restrictions || {}" :key="k" style="margin-top: 2px">· {{ v }}</div>
      </div>
      <template #footer>
        <el-button @click="upgradeVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!selectedPlan || selectedPlan.id === 'free'" @click="doUpgrade">确认升级</el-button>
      </template>
    </el-dialog>

    <!-- 支付前合规告知弹窗 -->
    <PaymentConfirm v-model="payVisible" :title="'升级至' + (selectedPlan?.name || '') + '套餐'" :amount-text="selectedPlan?.price || ''" @confirm="doPay" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'
import PaymentConfirm from '../components/PaymentConfirm.vue'

const profile = reactive({ username: '', nickname: '', email: '', phone: '' })
const plan = reactive({ plan_type: 'free', quota_used: 0, quota_total: 1000, expire_at: '', concurrent_tasks: 1, daily_crawl_limit: 100, api_access: false, allow_comments: false, sub_accounts: 0, crm: false })
const logs = ref([])
const saving = ref(false)
const upgradeVisible = ref(false)
const selectedPlan = ref(null)
const payVisible = ref(false)
const plans = ref([])
const planMap = { free: '免费版', standard: '小微个体户版', enterprise: '企业团队版' }
const planName = computed(() => planMap[plan.plan_type] || plan.plan_type)

const quotaPercent = computed(() => plan.quota_total ? Math.min(100, Math.round(plan.quota_used / plan.quota_total * 100)) : 0)

const load = async () => {
  const p = await api.get('/auth/profile')
  Object.assign(profile, { username: p.username, nickname: p.nickname || '', email: p.email || '', phone: p.phone || '' })
  if (p.plan) Object.assign(plan, p.plan)
  const l = await api.get('/misc/logs')
  logs.value = l.results
}

const saveProfile = async () => {
  saving.value = true
  try {
    await api.put('/auth/profile', profile)
    ElMessage.success('资料已保存')
  } finally {
    saving.value = false
  }
}

const upgrade = async () => {
  selectedPlan.value = null
  if (!plans.value.length) {
    const d = await api.get('/plans')
    plans.value = d.results
  }
  upgradeVisible.value = true
}

const doUpgrade = async () => {
  // 先弹合规支付确认，用户同意后走 doPay
  payVisible.value = true
}

const doPay = async () => {
  await ElMessageBox.confirm(`确认支付升级到${selectedPlan.value.name}（¥${selectedPlan.value.price}/月）？`, '支付确认', { type: 'info' })
  await api.post('/auth/plan', { plan_id: selectedPlan.value.id })
  ElMessage.success('升级成功')
  upgradeVisible.value = false
  load()
}

onMounted(load)
</script>

<style scoped>
.mt16 { margin-top: 16px; }
.mb16 { margin-bottom: 16px; }
.mt8 { margin-top: 8px; }
</style>
