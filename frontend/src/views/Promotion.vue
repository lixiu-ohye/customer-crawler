<template>
  <div class="promo-page">
    <div class="promo-hero">
      <h1>🎁 推广活动</h1>
      <p>成为推广员，分享海报赚佣金 · 每笔成功订单最高返 30%</p>
    </div>

    <el-row :gutter="16" class="mt16">
      <!-- 我的推广 -->
      <el-col :span="14">
        <el-card shadow="never">
          <template #header><div class="card-title">我的推广海报</div></template>
          <div v-if="!promoter" class="empty-box">
            <p>您还不是推广员</p>
            <el-button type="primary" @click="applyPromoter">申请成为推广员</el-button>
          </div>
          <div v-else>
            <div class="poster-box">
              <div class="poster">
                <div class="poster-head">客户大数据平台</div>
                <div class="poster-qr">
                  <div class="qr-code">🔳</div>
                  <div>扫码注册</div>
                </div>
                <div class="poster-code">邀请码：<b>{{ promoter.invite_code }}</b></div>
                <div class="poster-foot">推广员：{{ promoter.name }} · 返佣 {{ promoter.rate * 100 }}%</div>
              </div>
            </div>
            <div class="poster-url">
              推广链接：
              <el-input :model-value="promoUrl" readonly size="small" class="url-input">
                <template #append><el-button @click="copyUrl">复制</el-button></template>
              </el-input>
            </div>
          </div>
        </el-card>

        <el-card shadow="never" class="mt16">
          <template #header><div class="card-title">我的佣金</div></template>
          <el-descriptions :column="3" border size="small">
            <el-descriptions-item label="累计佣金">￥{{ stats.total_commission || 0 }}</el-descriptions-item>
            <el-descriptions-item label="可提现">￥{{ stats.withdrawable || 0 }}</el-descriptions-item>
            <el-descriptions-item label="推广人数">{{ stats.customers || 0 }} 人</el-descriptions-item>
          </el-descriptions>
          <el-button type="primary" class="mt12" :disabled="!(stats.withdrawable > 0)" @click="applyWithdraw">
            申请提现
          </el-button>
        </el-card>
      </el-col>

      <!-- 佣金明细 -->
      <el-col :span="10">
        <el-card shadow="never">
          <template #header><div class="card-title">佣金明细</div></template>
          <el-table :data="commissions" size="small" max-height="420">
            <el-table-column prop="order_id" label="订单" width="150" />
            <el-table-column prop="amount" label="佣金" width="80">
              <template #default="{ row }">￥{{ row.amount }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'paid' ? 'success' : 'info'" size="small">
                  {{ row.status === 'paid' ? '已结算' : '待结算' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const promoter = ref(null)
const commissions = ref([])
const stats = ref({})

const promoUrl = computed(() => {
  const base = window.location.origin + window.location.pathname
  return `${base}#/promotion?invite=${promoter.value?.invite_code || ''}`
})

onMounted(async () => {
  await loadPromoter()
  await loadCommissions()
})

const loadPromoter = async () => {
  try {
    const res = await api.get('/promotion/my')
    promoter.value = res.promoter || null
    stats.value = res.stats || {}
  } catch (e) {
    promoter.value = null
  }
}

const loadCommissions = async () => {
  try {
    const res = await api.get('/promotion/commissions')
    commissions.value = res.results || []
  } catch (e) { /* 忽略 */ }
}

const applyPromoter = async () => {
  const { value } = await ElMessageBox.prompt('请输入您的推广昵称', '申请推广员', {
    inputPlaceholder: '例如：张三'
  })
  try {
    const res = await api.post('/promotion/apply', { name: value })
    ElMessage.success(res.detail || '申请成功')
    await loadPromoter()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '申请失败')
  }
}

const applyWithdraw = async () => {
  const { value } = await ElMessageBox.prompt('请输入提现金额（元）', '申请提现', {
    inputValue: String(stats.value.withdrawable || 0)
  })
  try {
    const res = await api.post('/promotion/withdraw', { amount: parseFloat(value), channel: 'wechat' })
    ElMessage.success(res.detail || '提现申请已提交')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提现失败')
  }
}

const copyUrl = async () => {
  try {
    await navigator.clipboard.writeText(promoUrl.value)
    ElMessage.success('推广链接已复制')
  } catch (e) {
    ElMessage.warning('复制失败，请手动复制')
  }
}
</script>

<style scoped>
.promo-page { padding: 4px; }
.promo-hero { text-align: center; padding: 24px 0 8px; }
.promo-hero h1 { margin: 0 0 8px; }
.promo-hero p { color: #909399; margin: 0; }
.card-title { font-weight: 600; }
.empty-box { text-align: center; padding: 40px 0; color: #909399; }
.poster-box { display: flex; justify-content: center; padding: 12px 0; }
.poster { width: 260px; border: 1px solid #ebeef5; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,.06); }
.poster-head { background: linear-gradient(135deg, #409EFF, #36d1dc); color: #fff; text-align: center; padding: 14px; font-weight: 600; }
.poster-qr { text-align: center; padding: 18px 0 6px; }
.qr-code { font-size: 90px; line-height: 1; }
.poster-qr div:last-child { font-size: 12px; color: #909399; margin-top: 6px; }
.poster-code { text-align: center; padding: 10px; font-size: 13px; }
.poster-foot { background: #f5f7fa; text-align: center; padding: 8px; font-size: 12px; color: #909399; }
.poster-url { display: flex; align-items: center; gap: 8px; margin-top: 12px; font-size: 13px; }
.url-input { flex: 1; }
.mt16 { margin-top: 16px; }
.mt12 { margin-top: 12px; }
</style>
