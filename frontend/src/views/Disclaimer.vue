<template>
  <div class="page-card">
    <div class="page-title">合规与免责声明</div>
    <el-alert type="warning" :closable="false" class="mb16"
      title="本平台仅用于合法合规的商业调研与客户开发，禁止用于骚扰、诈骗、侵犯隐私等违法用途。" />
    <div class="disclaimer-box">
      <p v-for="(line, i) in lines" :key="i" class="disclaimer-line">{{ line }}</p>
    </div>
    <div class="mt16">
      <el-checkbox v-model="accepted">我已仔细阅读并同意以上声明全部内容</el-checkbox>
    </div>
    <el-button type="primary" class="mt16" :disabled="!accepted" @click="confirm">确认并同意</el-button>
    <span v-if="alreadyAccepted" style="margin-left: 12px; color: #67C23A; font-size: 13px">✓ 已同意</span>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const accepted = ref(false)
const alreadyAccepted = ref(localStorage.getItem('disclaimerAccepted') === '1')

const lines = computed(() => {
  const text = `本平台提供的客户大数据采集与分析服务，旨在帮助用户合法合规地开展市场调研与客户开发工作。
使用本平台前，请您仔细阅读并理解以下条款：

一、合法性声明
1. 本平台采集的数据来源于互联网公开信息，仅限用于合法的商业调研、客户服务与市场分析用途。
2. 用户承诺：不得将本平台数据用于骚扰、诈骗、侵犯个人隐私、不正当竞争或其他任何违法违规活动。
3. 涉及个人信息的数据，用户应遵守《中华人民共和国个人信息保护法》《中华人民共和国数据安全法》及《中华人民共和国网络安全法》等相关法律法规。

二、使用限制
1. 禁止利用本平台对任何平台进行恶意攻击、高频抓取、绕过风控等破坏性行为。
2. 禁止将线索数据出售、转售或提供给任何第三方用于非法用途。
3. 用户应合理控制采集频率，尊重各平台的服务协议与 robots 协议。

三、数据合规
1. 本平台对采集的数据执行 30 天自动清理机制，到期数据将自动删除。
2. 本平台记录全部操作日志与采集日志，留存备查。
3. 用户应对自身账号下的所有操作行为负责。

四、免责声明
1. 因用户违规使用本平台导致的法律责任，由用户自行承担。
2. 本平台不保证数据的完整性、准确性或时效性，数据仅供参考。
3. 本平台不对因使用数据产生的任何直接或间接损失承担责任。

五、其他
1. 本声明解释权归本平台所有，平台有权根据法律法规变化适时更新本声明。
2. 继续使用本平台即视为您已阅读并同意本声明的全部内容。`
  return text.split('\n')
})

const confirm = () => {
  localStorage.setItem('disclaimerAccepted', '1')
  alreadyAccepted.value = true
  ElMessage.success('已确认同意，感谢您的配合')
}
</script>

<style scoped>
.disclaimer-box { background: #f5f7fa; border: 1px solid #ebeef5; border-radius: 8px; padding: 20px; max-height: 480px; overflow-y: auto; }
.disclaimer-line { line-height: 1.8; color: #303133; font-size: 14px; }
.mt16 { margin-top: 16px; }
.mb16 { margin-bottom: 16px; }
</style>
