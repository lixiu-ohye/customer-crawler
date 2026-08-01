<template>
  <div class="login-page">
    <div class="login-card">
      <!-- ===== 品牌区（新版设计） ===== -->
      <div class="brand">
        <div class="logo" aria-hidden="true"><span>📊</span></div>
        <div class="brand-text">
          <h1>客户大数据智能获客平台</h1>
          <small>精准 · 高效 · 合规</small>
        </div>
      </div>

      <el-tabs v-model="tab" class="mt16">
        <!-- ========= 登录面板 ========= -->
        <el-tab-pane label="登录" name="login">
          <el-form :model="form" @keyup.enter="submit">
            <el-form-item>
              <el-input v-model="form.username" placeholder="用户名" size="large" :prefix-icon="User" autocomplete="username" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password :prefix-icon="Lock" autocomplete="current-password" />
            </el-form-item>
            <!-- 图形验证码（点击刷新） -->
            <el-form-item>
              <div class="captcha-row">
                <el-input v-model="form.captcha" placeholder="输入验证码" size="large" maxlength="4" autocomplete="off" />
                <div class="captcha-box" role="img" aria-label="验证码，点击刷新" title="点击刷新" @click="refreshCaptcha">{{ captchaCode }}</div>
              </div>
            </el-form-item>
            <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="submit">登 录</el-button>
            <div class="form-footer">
              <a class="link" @click.prevent="forgotPwd">忘记密码？</a>
              <span class="gray">还没有账号？ <a class="link" @click.prevent="tab = 'register'">立即注册</a></span>
            </div>
          </el-form>
          <!-- 演示账号提示（醒目） -->
          <div class="demo-note" role="note">
            <span class="icon">🔐</span>
            <div><strong>演示账号</strong>：admin / admin123456<br />
              <span class="warn">⚠️ 生产环境请勿使用演示账号，建议及时修改密码。</span></div>
          </div>
        </el-tab-pane>

        <!-- ========= 注册面板 ========= -->
        <el-tab-pane label="注册" name="register">
          <el-form :model="form" @keyup.enter="submit">
            <el-form-item>
              <el-input v-model="form.username" placeholder="用户名（至少4个字符）" size="large" :prefix-icon="User" autocomplete="username" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.email" placeholder="邮箱（可选）" size="large" :prefix-icon="Message" autocomplete="email" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.password" type="password" placeholder="密码（至少6位）" size="large" show-password :prefix-icon="Lock" autocomplete="new-password" />
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
            <div class="form-footer center">
              <span class="gray">已有账号？ <a class="link" @click.prevent="tab = 'login'">去登录</a></span>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <!-- ===== 合规与版权页脚（新版设计） ===== -->
      <div class="compliance">
        <div>
          <span>📄 <a class="link" @click.prevent="showComplianceInfo">《合规与免责声明》</a></span>
          <span class="dot">·</span>
          <span>数据 <strong>30天</strong> 自动清理（物理删除）</span>
        </div>
        <div class="footer-copy">© 2026 客户大数据智能获客平台 · 粤ICP备XXXXXXXX号</div>
      </div>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const tab = ref('login')
const loading = ref(false)
const form = reactive({ username: '', password: '', email: '', promoter: '', captcha: '' })

// ===== 图形验证码（排除易混淆字符，点击刷新） =====
const CAPTCHA_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
const captchaCode = ref('')
function refreshCaptcha() {
  let code = ''
  for (let i = 0; i < 4; i++) {
    code += CAPTCHA_CHARS.charAt(Math.floor(Math.random() * CAPTCHA_CHARS.length))
  }
  captchaCode.value = code
  form.captcha = ''
}
function checkCaptcha() {
  if (!form.captcha) {
    ElMessage.warning('请输入验证码')
    return false
  }
  if (form.captcha.trim().toUpperCase() !== captchaCode.value) {
    ElMessage.warning('验证码错误，请重新输入')
    refreshCaptcha()
    return false
  }
  return true
}

// 忘记密码（演示）
function forgotPwd() {
  ElMessage.info('📧 重置链接已发送至您的绑定邮箱（演示功能）')
}

// 合规页脚说明（演示弹窗）
function showComplianceInfo() {
  ElMessageBox.alert(
    '1. 数据收集：仅收集您主动提供的用户名、邮箱、手机号等信息。\n' +
    '2. 数据使用：用于平台身份验证及个性化服务推荐。\n' +
    '3. 数据存储：加密存储于云端服务器，保留期限为 30 天。\n' +
    '4. 数据删除：满 30 天后执行物理删除，不可恢复。\n' +
    '5. 用户权利：您可随时联系 support@example.com 查询或删除您的数据。',
    '【合规与免责声明】',
    { confirmButtonText: '我已了解', type: 'warning' }
  )
}

// 0.01 元体验包
const useTrial = ref(false)
const showTrialPay = ref(false)
const payAccepted = ref(false)
const paying = ref(false)

// 合规签署状态
const showCompliance = ref(false)
const accepted = ref(false)
const pendingAuth = ref(null)

// 防暴力破解：登录尝试次数限制（前端演示）
let loginAttempts = 0
const MAX_ATTEMPTS = 5

onMounted(() => {
  refreshCaptcha()
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
  // 登录需校验图形验证码
  if (tab.value === 'login' && !checkCaptcha()) {
    return
  }
  // 防暴力破解（登录）
  if (tab.value === 'login' && loginAttempts >= MAX_ATTEMPTS) {
    ElMessage.warning('⛔ 登录尝试次数过多，请稍后再试')
    return
  }
  if (tab.value === 'register' && form.username.length < 4) {
    ElMessage.warning('用户名至少 4 个字符')
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
    // 拦截器已提示；登录失败计入尝试次数并刷新验证码
    if (tab.value === 'login') {
      loginAttempts++
      refreshCaptcha()
    }
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
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, #f5f7fa 0%, #e9edf5 100%);
  padding: 20px;
}
.login-card {
  width: 460px;
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12), 0 8px 24px rgba(0, 0, 0, 0.05);
  padding: 32px 30px 24px;
  transition: all 0.3s ease;
}
/* ===== 品牌区 ===== */
.brand { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.logo {
  width: 44px; height: 44px;
  background-image: radial-gradient(circle at 30% 30%, #6a9ff5, #1a4fbf);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 22px;
  flex-shrink: 0;
  box-shadow: 0 4px 8px rgba(42, 109, 244, 0.3);
}
.logo span { transform: rotate(-8deg); }
.brand-text h1 { font-size: 19px; font-weight: 600; color: #1e293b; letter-spacing: 0.3px; margin: 0; }
.brand-text small { font-weight: 400; font-size: 13px; color: #64748b; }
/* ===== 验证码 ===== */
.captcha-row { display: flex; gap: 12px; align-items: center; width: 100%; }
.captcha-row .el-input { flex: 1; }
.captcha-box {
  flex-shrink: 0;
  width: 104px; height: 40px;
  background: #f0f4fc;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-family: "Courier New", monospace;
  font-weight: 700; font-size: 20px; letter-spacing: 4px;
  color: #1e293b; cursor: pointer; user-select: none;
  border: 1.5px dashed #b8c9e0;
  transition: background 0.2s;
}
.captcha-box:hover { background: #e6edf8; }
.captcha-box:active { transform: scale(0.96); }
/* ===== 按钮 ===== */
.submit-btn { width: 100%; margin-top: 4px; }
/* ===== 辅助链接 ===== */
.form-footer {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 14px; font-size: 13px;
}
.form-footer.center { justify-content: center; }
.link { color: #2a6df4; text-decoration: none; font-weight: 500; cursor: pointer; }
.link:hover { text-decoration: underline; }
.gray { color: #94a3b8; }
/* ===== 演示账号提示 ===== */
.demo-note {
  background: #fef9e7;
  border-left: 4px solid #f59e0b;
  padding: 12px 14px;
  border-radius: 10px;
  font-size: 13px;
  color: #92400e;
  margin-top: 18px;
  display: flex; align-items: flex-start; gap: 8px;
  line-height: 1.5;
}
.demo-note .icon { font-size: 18px; flex-shrink: 0; }
.demo-note strong { font-weight: 600; }
.demo-note .warn { font-size: 12px; }
/* ===== 合规页脚 ===== */
.compliance {
  margin-top: 24px;
  border-top: 1px solid #e9edf2;
  padding-top: 16px;
  font-size: 12px;
  color: #64748b;
  text-align: center;
  line-height: 1.8;
}
.compliance .dot { margin: 0 8px; color: #c0c8d4; }
.compliance strong { color: #475569; }
.footer-copy { margin-top: 4px; font-size: 11px; color: #94a3b8; }
/* ===== 弹窗通用 ===== */
.compliance-box { max-height: 380px; overflow-y: auto; }
.mb12 { margin-bottom: 12px; }
.mt12 { margin-top: 12px; }
.mt16 { margin-top: 16px; }
.rules { line-height: 1.9; color: #303133; font-size: 13px; }
.rules p { margin: 0 0 6px; }
.pay-box { text-align: center; }
.pay-amount { font-size: 32px; font-weight: 700; color: #F56C6C; }
.pay-item { color: #606266; margin: 8px 0 4px; }
.pay-notice { font-size: 12px; color: #606266; line-height: 1.7; text-align: left; margin: 6px 0 0; }
</style>
