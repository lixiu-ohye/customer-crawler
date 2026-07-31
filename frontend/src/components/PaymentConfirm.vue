<template>
  <!-- 支付前合规告知弹窗（信息共享 + 支付说明） -->
  <el-dialog v-model="visible" title="支付确认" width="460px" append-to-body :close-on-click-modal="false">
    <div class="pay-box">
      <div class="pay-amount">{{ amountText }}</div>
      <div class="pay-item">{{ title }}</div>
      <el-alert type="info" :closable="false" class="mt12" title="支付前告知（信息共享与合规说明）">
        <p class="pay-notice">1. 您的注册信息（用户名、注册时间、IP 归属）将共享给您的<b>推广员</b>，用于客户登记报表与佣金结算；平台对推广员可见的数据做脱敏处理。</p>
        <p class="pay-notice">2. 支付通过微信 / 支付宝官方渠道完成，平台<b>不存储</b>您的支付密码、银行卡号等敏感信息。</p>
        <p class="pay-notice">3. 订单与支付记录将纳入平台运营日志，留存备查，用于财务对账与合规审计。</p>
        <p class="pay-notice">4. 套餐服务为虚拟数字产品，支付成功后不支持无理由退款；7 天未付费用户的采集额度将自动减半。</p>
      </el-alert>
      <el-checkbox v-model="accepted" class="mt12">我已阅读并同意信息共享与支付说明</el-checkbox>
    </div>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :disabled="!accepted" @click="confirm">确认支付</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '订单支付' },
  amountText: { type: String, default: '¥0.00' }
})
const emit = defineEmits(['update:modelValue', 'confirm'])

const visible = ref(props.modelValue)
const accepted = ref(false)

watch(() => props.modelValue, v => {
  visible.value = v
  if (v) accepted.value = false
})
watch(visible, v => emit('update:modelValue', v))

const confirm = () => {
  accepted.value = false
  visible.value = false
  emit('confirm')
}
</script>

<style scoped>
.pay-box { text-align: center; }
.pay-amount { font-size: 32px; font-weight: 700; color: #F56C6C; }
.pay-item { color: #606266; margin: 8px 0 4px; }
.pay-notice { font-size: 12px; color: #606266; line-height: 1.7; text-align: left; margin: 6px 0 0; }
.mt12 { margin-top: 12px; }
</style>
