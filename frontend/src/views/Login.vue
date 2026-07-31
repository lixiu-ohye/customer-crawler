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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const tab = ref('login')
const loading = ref(false)
const form = reactive({ username: '', password: '', email: '' })

// 合规签署状态
const showCompliance = ref(false)
const accepted = ref(false)
const pendingAuth = ref(null) // 登录成功后待进入系统的凭据

onMounted(() => {
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
  loading.value = true
  try {
    if (tab.value === 'login') {
      await auth.login(form.username, form.password)
    } else {
      await auth.register(form.username, form.password, form.email)
    }
    ElMessage.success(tab.value === 'login' ? '登录成功' : '注册成功')
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

const confirmCompliance = () => {
  localStorage.setItem('disclaimerAccepted', '1')
  showCompliance.value = false
  ElMessage.success('已签署合规声明，欢迎进入平台')
  router.push('/dashboard')
}
</script>

<style scoped>
.login-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1f2d3d 0%, #2b4a6f 50%, #409EFF 100%); }
.login-card { width: 400px; background: #fff; border-radius: 12px; padding: 40px 36px; box-shadow: 0 12px 40px rgba(0,0,0,.25); }
.login-title { text-align: center; font-size: 20px; color: #303133; }
.submit-btn { width: 100%; }
.tip { margin-top: 16px; text-align: center; font-size: 12px; color: #909399; }
.compliance-tip { margin-top: 8px; text-align: center; font-size: 11px; color: #b0b3b8; }
.compliance-box { max-height: 380px; overflow-y: auto; }
.mb12 { margin-bottom: 12px; }
.rules { line-height: 1.9; color: #303133; font-size: 13px; }
.rules p { margin: 0 0 6px; }
</style>
