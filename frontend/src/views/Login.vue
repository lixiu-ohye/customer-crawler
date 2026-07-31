<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="login-title">客户大数据智能获客平台</h2>
      <el-tabs v-model="tab" class="mt16">
        <el-tab-pane label="登录" name="login">
          <el-form :model="form" @keyup.enter="submit">
            <el-form-item>
              <el-input v-model="form.username" placeholder="用户名" size="large" :prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password :prefix-icon="Lock" />
            </el-form-item>
            <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="submit">登 录</el-button>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form :model="form" @keyup.enter="submit">
            <el-form-item>
              <el-input v-model="form.username" placeholder="用户名" size="large" :prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.email" placeholder="邮箱（可选）" size="large" :prefix-icon="Message" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.password" type="password" placeholder="密码（至少6位）" size="large" show-password :prefix-icon="Lock" />
            </el-form-item>
            <!-- 0.01 元体验资格包：经推广海报 / 悬浮气泡进入自动携带推广码 -->
            <el-form-item>
              <el-checkbox v-model="useTrial" border>
                0.01 元体验资格包（赠送基础获客权益，仅限新用户）
              </el-checkbox>
            </el-form-item>
            <el-form-item v-if="useTrial">
              <el-input v-model="form.promoter" placeholder="推广邀请码（选填，来自推广海报）" size="large" :prefix-icon="Promotion" />
            </el-form-item>
            <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="submit">注 册</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <div class="tip">演示账号：admin / admin123456</div>
      <div class="compliance-tip">登录即代表同意《合规与免责声明》：仅限合法商业调研，禁采集隐私、禁私信群发，数据 30 天自动清理</div>
    </div>

    <!-- 登录后合规签署弹窗：同意后才进入系统 -->
    <el-dialog v-model="showCompliance" title="合规使用须知" width="640px" :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false" append-to-body>
      <div class="compliance-box">
        <el-alert type="warning" :closable="false" class="mb12" title="请在使用平台前仔细阅读以下合规须知" />
        <div class="rules">
          <p>1. 本平台仅采集互联网<b>公开信息</b>，仅限用于合法的商业调研、客户服务与市场分析。</p>
          <p>2. 禁止采集手机号、微信号、私信记录、真实姓名等个人隐私信息；禁止自动私信、批量评论、批量加好友、群发引流。</p>
          <p>3. 禁止破解验证码、伪造设备指纹、绕过平台风控等破坏性行为；禁止将数据出售或转售给第三方。</p>
          <p>4. 平台对数据执行 <b>30 天自动清理</b>机制，全程记录操作日志与采集日志，留存备查。</p>
          <p>5. 请遵守《中华人民共和国网络安全法》《中华人民共和国个人信息保护法》《中华人民共和国数据安全法》及相关平台服务协议。</p>
          <p>6. 因用户违规使用本平台导致的法律责任，由用户自行承担。</p>
        </div>
      </div>
      <template #footer>
        <el-checkbox v-model="accepted">我已阅读并同意以上全部条款</el-checkbox>
        <el-button type="primary" :disabled="!accepted" @click="confirmCompliance">同意并进入系统</el-button>
      </template>
    </el-dialog>

    <!-- 0.01 元体验包支付弹窗（支付前合规告知：信息共享 + 用途说明） -->
    <el-dialog v-model="showTrialPay" title="支付确认" width="440px" append-to-body>
      <div class="pay-box">
        <div class="pay-amount">¥0.01</div>
        <div class="pay-item">体验资格包 · 新用户专享</div>
        <el-alert type="info" :closable="false" class="mt12" title="支付前告知（信息共享说明）">
          <p class="pay-notice">1. 您的注册信息（用户名、注册时间、IP）将共享给您的<b>推广员</b>，用于客户登记报表与佣金结算。</p>
          <p class="pay-notice">2. 支付通过微信/支付宝官方渠道完成，平台不存储您的支付密码与银行卡信息。</p>
          <p class="pay-notice">3. 本体验包为一次性付费资格，不自动续费；7 天内未升级套餐，采集额度减半。</p>
        </el-alert>
        <el-checkbox v-model="payAccepted" class="mt12">我已阅读并同意信息共享与支付说明</el-checkbox>
      </div>
      <template #footer>
        <el-button @click="showTrialPay = false">暂不购买</el-button>
        <el-button type="primary" :disabled="!payAccepted" :loading="paying" @click="confirmTrialPay">
          微信支付 ¥0.01
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Lock, Message, Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const tab = ref('login')
const loading = ref(false)
const form = reactive({ username: '', password: '', email: '', promoter: '' })

// 0.01 元体验包
const useTrial = ref(false)
const showTrialPay = ref(false)
const payAccepted = ref(false)
const paying = ref(false)

// 合规签署状态
const showCompliance = ref(false)
const accepted = ref(false)
const pendingAuth = ref(null)

onMounted(() => {
  // 从推广海报 / 悬浮气泡进入（URL 带 invite 参数）：自动勾选体验包并填入推广码
  const invite = route.query.invite || ''
  if (invite) {
    useTrial.value = true
    form.promoter = invite
  }
  // 已登录用户重新访问：若未签署过合规，先弹签署框
  if (auth.isLoggedIn && localStorage.getItem('disclaimerAccepted') !== '1') {
    showCompliance.value = true
  }
})

const submit = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  if (tab.value === 'register' && useTrial.value && !form.promoter) {
    ElMessage.warning('请填写推广邀请码（来自推广海报或悬浮气泡）')
    return
  }
  loading.value = true
  try {
    if (tab.value === 'login') {
      await auth.login(form.username, form.password)
      ElMessage.success('登录成功')
    } else if (useTrial.value) {
      // 0.01 元体验包注册：先注册账号，再弹支付确认
      await auth.register(form.username, form.password, form.email, form.promoter)
      ElMessage.success('注册成功')
      payAccepted.value = false
      showTrialPay.value = true
      return
    } else {
      await auth.register(form.username, form.password, form.email)
      ElMessage.success('注册成功')
    }
    // 若已签署过合规，直接进入系统；否则弹签署框，同意后才进入
    if (localStorage.getItem('disclaimerAccepted') === '1') {
      router.push('/dashboard')
    } else {
      pendingAuth.value = { username: form.username }
      accepted.value = false
      showCompliance.value = true
    }
  } catch (e) {
    // 拦截器已提示
  } finally {
    loading.value = false
  }
}

const confirmTrialPay = async () => {
  paying.value = true
  try {
    const res = await api.post('/promotion/pay', { orderId: localStorage.getItem('trialOrderId') || '' })
    ElMessage.success(res.detail || '支付成功，体验包已开通')
    showTrialPay.value = false
    router.push('/dashboard')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '支付失败，请重试')
  } finally {
    paying.value = false
  }
}

const confirmCompliance = () => {
  localStorage.setItem('disclaimerAccepted', '1')
  showCompliance.value = false
  ElMessage.success('已签署合规声明，欢迎进入平台')
  router.push('/dashboard')
}
</script>

<style scoped>
.login-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1f2d3d 0%, #2b4a6f 50%, #409EFF 100%); }
.login-card { width: 420px; background: #fff; border-radius: 12px; padding: 40px 36px; box-shadow: 0 12px 40px rgba(0,0,0,.25); }
.login-title { text-align: center; font-size: 20px; color: #303133; }
.submit-btn { width: 100%; }
.tip { margin-top: 16px; text-align: center; font-size: 12px; color: #909399; }
.compliance-tip { margin-top: 8px; text-align: center; font-size: 11px; color: #b0b3b8; }
.compliance-box { max-height: 380px; overflow-y: auto; }
.mb12 { margin-bottom: 12px; }
.mt12 { margin-top: 12px; }
.rules { line-height: 1.9; color: #303133; font-size: 13px; }
.rules p { margin: 0 0 6px; }
.pay-box { text-align: center; }
.pay-amount { font-size: 32px; font-weight: 700; color: #F56C6C; }
.pay-item { color: #606266; margin: 8px 0 4px; }
.pay-notice { font-size: 12px; color: #606266; line-height: 1.7; text-align: left; margin: 6px 0 0; }
</style>
