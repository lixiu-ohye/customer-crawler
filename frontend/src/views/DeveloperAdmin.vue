<template>
  <div class="dev-admin">
    <!-- 财务总览 -->
    <el-row :gutter="16" class="mb12">
      <el-col :span="6" v-for="card in financeCards" :key="card.label">
        <el-card shadow="never">
          <div class="fin-card">
            <div class="fin-label">{{ card.label }}</div>
            <div class="fin-value" :style="{ color: card.color }">￥{{ card.value }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-tabs v-model="tab" class="mt8">
      <!-- 全量用户 -->
      <el-tab-pane label="全量用户" name="users">
        <el-table :data="data.users" border size="small">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label="用户名" width="110" />
          <el-table-column prop="name" label="推广员" width="90" />
          <el-table-column prop="plan" label="套餐" width="90" />
          <el-table-column prop="identity" label="实名" width="70">
            <template #default="{ row }">
              <el-tag :type="row.identity === 'verified' ? 'success' : 'info'" size="small">
                {{ row.identity === 'verified' ? '已实名' : '未实名' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="contact" label="联系方式" min-width="120" show-overflow-tooltip />
          <el-table-column prop="device_ip" label="设备IP" width="130" />
          <el-table-column prop="registered_at" label="注册时间" width="150" />
          <el-table-column label="操作" width="90">
            <template #default="{ row }">
              <el-button v-if="row.is_promoter" type="danger" link size="small"
                @click="freezePromoter(row)">冻结</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 订单 -->
      <el-tab-pane label="订单" name="orders">
        <el-table :data="data.orders" border size="small">
          <el-table-column prop="id" label="订单号" width="170" />
          <el-table-column prop="user" label="用户" width="90" />
          <el-table-column prop="plan" label="套餐" width="90" />
          <el-table-column prop="amount" label="金额" width="80">
            <template #default="{ row }">￥{{ row.amount }}</template>
          </el-table-column>
          <el-table-column prop="channel" label="渠道" width="80" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'paid' ? 'success' : row.status === 'refunded' ? 'danger' : 'info'" size="small">
                {{ { paid: '已支付', refunded: '已退款', pending: '待支付' }[row.status] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="150" />
        </el-table>
      </el-tab-pane>

      <!-- 佣金 -->
      <el-tab-pane label="佣金" name="commissions">
        <el-table :data="commissionRows" border size="small">
          <el-table-column prop="promoter" label="推广员" width="100" />
          <el-table-column prop="order_id" label="订单" width="170" />
          <el-table-column prop="amount" label="佣金" width="90">
            <template #default="{ row }">￥{{ row.amount }}</template>
          </el-table-column>
          <el-table-column prop="rate" label="比例" width="70">
            <template #default="{ row }">{{ (row.rate * 100).toFixed(0) }}%</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'paid' ? 'success' : 'warning'" size="small">
                {{ row.status === 'paid' ? '已结算' : '待结算' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="150" />
        </el-table>
      </el-tab-pane>

      <!-- 提现 -->
      <el-tab-pane label="提现" name="withdrawals">
        <el-table :data="data.withdrawals" border size="small">
          <el-table-column prop="id" label="编号" width="170" />
          <el-table-column prop="user" label="用户" width="100" />
          <el-table-column prop="amount" label="金额" width="90">
            <template #default="{ row }">￥{{ row.amount }}</template>
          </el-table-column>
          <el-table-column prop="channel" label="渠道" width="90" />
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'approved' ? 'success' : row.status === 'rejected' ? 'danger' : 'warning'" size="small">
                {{ { pending: '待审核', approved: '已打款', rejected: '已驳回' }[row.status] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="request_time" label="申请时间" width="150" />
        </el-table>
      </el-tab-pane>

      <!-- 客户登记报表 -->
      <el-tab-pane label="客户登记" name="reports">
        <el-table :data="data.userReports" border size="small">
          <el-table-column prop="userId" label="用户ID" width="80" />
          <el-table-column prop="promoter" label="推广员" width="90" />
          <el-table-column prop="identitySubject" label="实名主体" width="100" />
          <el-table-column prop="planStatus" label="套餐" width="90" />
          <el-table-column prop="customerContact" label="联系方式" min-width="120" show-overflow-tooltip />
          <el-table-column prop="deviceIP" label="设备IP" width="130" />
          <el-table-column prop="registrationTime" label="注册时间" width="160" />
          <el-table-column prop="paymentChannel" label="支付渠道" width="90" />
        </el-table>
      </el-tab-pane>

      <!-- 收支对账 -->
      <el-tab-pane label="收支对账" name="recon">
        <el-table :data="reconRows" border size="small">
          <el-table-column prop="channel" label="渠道" width="110" />
          <el-table-column prop="paid" label="实收" width="100">
            <template #default="{ row }">￥{{ row.paid }}</template>
          </el-table-column>
          <el-table-column prop="refunded" label="退款" width="100">
            <template #default="{ row }">￥{{ row.refunded }}</template>
          </el-table-column>
          <el-table-column prop="balance" label="净额" width="100">
            <template #default="{ row }">
              <b>￥{{ row.balance }}</b>
            </template>
          </el-table-column>
          <el-table-column prop="commission" label="分销支出" width="100">
            <template #default="{ row }">￥{{ row.commission }}</template>
          </el-table-column>
          <el-table-column prop="net" label="平台净利" width="110">
            <template #default="{ row }">
              <el-tag type="success" size="small">￥{{ row.net }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 推广员管理 -->
      <el-tab-pane label="推广员" name="promoters">
        <el-table :data="data.promoters" border size="small">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="name" label="推广员" width="110" />
          <el-table-column prop="invite_code" label="邀请码" width="110" />
          <el-table-column prop="rate" label="返佣比例" width="90">
            <template #default="{ row }">{{ (row.rate * 100).toFixed(0) }}%</template>
          </el-table-column>
          <el-table-column prop="customers" label="推广人数" width="90" />
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'frozen' ? 'danger' : 'success'" size="small">
                {{ row.status === 'frozen' ? '已冻结' : '正常' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="freeze_reason" label="冻结原因" min-width="120" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <div class="mt16 action-bar">
      <el-button type="primary" @click="refresh">刷新数据</el-button>
      <el-button @click="exportJson">导出 JSON</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const tab = ref('users')
const data = ref({ users: [], orders: [], commissions: {}, withdrawals: [], promoters: [], userReports: [], financeReports: {} })

const financeCards = computed(() => {
  const f = data.value.financeReports || {}
  return [
    { label: '总营收', value: f.totalIncome || 0, color: '#409EFF' },
    { label: '渠道代理费', value: f.channelAgentFeeIncome || 0, color: '#67C23A' },
    { label: '分销支出', value: f.commissionExpense || 0, color: '#E6A23C' },
    { label: '平台净利', value: (f.totalIncome || 0) - (f.commissionExpense || 0), color: '#F56C6C' }
  ]
})

const commissionRows = computed(() => {
  const map = data.value.commissions || {}
  const rows = []
  Object.entries(map).forEach(([promoter, list]) => {
    ;(list || []).forEach(c => rows.push({ promoter, ...c }))
  })
  return rows
})

const reconRows = computed(() => {
  const r = data.value.financeReports?.wechatAlipayReconciliation || {}
  const wechat = r.wechat || {}
  const alipay = r.alipay || {}
  const totalCommission = data.value.financeReports?.commissionExpense || 0
  return [
    { channel: '微信支付', paid: wechat.paid || 0, refunded: wechat.refunded || 0, balance: wechat.balance || 0, commission: totalCommission / 2, net: (wechat.balance || 0) - totalCommission / 2 },
    { channel: '支付宝', paid: alipay.paid || 0, refunded: alipay.refunded || 0, balance: alipay.balance || 0, commission: totalCommission / 2, net: (alipay.balance || 0) - totalCommission / 2 }
  ]
})

onMounted(refresh)

async function refresh() {
  try {
    const res = await api.get('/admin/platform')
    data.value = res || {}
    ElMessage.success('数据已刷新')
  } catch (e) {
    ElMessage.error('加载开发者后台数据失败')
  }
}

const freezePromoter = async (row) => {
  const { value } = await ElMessageBox.prompt('请输入冻结原因', `冻结推广员 ${row.name}`, {
    inputPlaceholder: '例如：刷单行为'
  })
  try {
    const res = await api.post(`/admin/promoter/${row.id}/freeze`, { reason: value })
    ElMessage.success(res.detail || '已冻结')
    refresh()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '冻结失败')
  }
}

const exportJson = () => {
  const blob = new Blob([JSON.stringify(data.value, null, 2)], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `platform_data_${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(a.href)
}
</script>

<style scoped>
.dev-admin { padding: 4px; }
.fin-card { text-align: center; }
.fin-label { font-size: 13px; color: #909399; }
.fin-value { font-size: 24px; font-weight: 700; margin-top: 6px; }
.mb12 { margin-bottom: 12px; }
.mt8 { margin-top: 8px; }
.mt16 { margin-top: 16px; }
.action-bar { display: flex; gap: 8px; }
</style>
