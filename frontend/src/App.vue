<template>
  <router-view />
  <!-- 兜底合规弹窗：仅当已登录且从未签署时弹出（正常情况下登录流程已引导签署） -->
  <el-dialog v-model="showDialog" title="合规使用须知" width="640px" :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false" append-to-body>
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
      <el-button type="primary" :disabled="!accepted" @click="confirm">同意并进入平台</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const showDialog = ref(false)
const accepted = ref(false)

onMounted(() => {
  // 仅已登录且未签署过时弹出；登录页会引导签署，此处为兜底
  if (auth.isLoggedIn && localStorage.getItem('disclaimerAccepted') !== '1') {
    showDialog.value = true
  }
})

const confirm = () => {
  localStorage.setItem('disclaimerAccepted', '1')
  showDialog.value = false
}
</script>

<style scoped>
.compliance-box { max-height: 380px; overflow-y: auto; }
.mb12 { margin-bottom: 12px; }
.rules { line-height: 1.9; color: #303133; font-size: 13px; }
.rules p { margin: 0 0 6px; }
</style>
