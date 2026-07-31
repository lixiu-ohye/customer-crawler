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
              <el-tag type="success">{{ plan.plan_type === 'free' ? '免费版' : plan.plan_type === 'pro' ? '专业版' : '旗舰版' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="线索配额">{{ plan.quota_used }}/{{ plan.quota_total }}</el-descriptions-item>
            <el-descriptions-item label="到期时间">{{ plan.expire_at || '永久' }}</el-descriptions-item>
            <el-descriptions-item label="任务并发">{{ plan.concurrent_tasks }}</el-descriptions-item>
            <el-descriptions-item label="每日采集上限">{{ plan.daily_crawl_limit }}</el-descriptions-item>
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

    <el-dialog v-model="upgradeVisible" title="升级套餐" width="560px">
      <el-table :data="plans" highlight-current-row @current-change="r => selectedPlan = r">
        <el-table-column prop="name" label="套餐" width="100" />
        <el-table-column prop="quota" label="线索配额" width="120" />
        <el-table-column prop="concurrent" label="并发任务" width="100" />
        <el-table-column prop="price" label="价格" width="100" />
        <el-table-column prop="desc" label="说明" />
      </el-table>
      <template #footer>
        <el-button @click="upgradeVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!selectedPlan" @click="doUpgrade">确认升级</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const profile = reactive({ username: '', nickname: '', email: '', phone: '' })
const plan = reactive({ plan_type: 'free', quota_used: 0, quota_total: 1000, expire_at: '', concurrent_tasks: 1, daily_crawl_limit: 100, api_access: false })
const logs = ref([])
const saving = ref(false)
const upgradeVisible = ref(false)
const selectedPlan = ref(null)
const plans = [
  { name: '专业版', quota: 10000, concurrent: 5, price: '¥199/月', desc: '适合中小企业', value: 'pro' },
  { name: '旗舰版', quota: 50000, concurrent: 20, price: '¥599/月', desc: '适合批量获客团队', value: 'premium' }
]

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

const upgrade = () => {
  selectedPlan.value = null
  upgradeVisible.value = true
}

const doUpgrade = async () => {
  await ElMessageBox.confirm(`确认升级到${selectedPlan.value.name}？`, '提示', { type: 'info' })
  await api.post('/auth/plan', { plan_type: selectedPlan.value.value })
  ElMessage.success('升级成功')
  upgradeVisible.value = false
  load()
}

onMounted(load)
</script>

<style scoped>
.mt16 { margin-top: 16px; }
.mb16 { margin-bottom: 16px; }
</style>
