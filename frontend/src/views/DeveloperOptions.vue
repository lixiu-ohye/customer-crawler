<template>
  <div class="dev-page">
    <!-- 开发者身份横幅 -->
    <el-card class="dev-banner" shadow="never">
      <div class="banner-inner">
        <el-icon class="banner-icon" :size="40"><Cpu /></el-icon>
        <div>
          <div class="banner-title">
            开发者专属特权
            <el-tag type="danger" effect="dark" size="small" class="ml8">永久免费</el-tag>
          </div>
          <div class="banner-sub">
            账号 <b>admin</b> 为开发者账号，享有本系统全部功能的永久免费使用与管理权限，不参与任何套餐计费与额度限制。
          </div>
        </div>
      </div>
    </el-card>

    <!-- 特权清单 -->
    <el-card shadow="never" class="mt16">
      <template #header>
        <div class="card-title"><el-icon><Star /></el-icon> 开发者特权清单</div>
      </template>
      <el-row :gutter="16">
        <el-col :span="8" v-for="p in privileges" :key="p.code" class="mb12">
          <div class="priv-item">
            <el-tag type="success" effect="light" size="small">{{ p.name }}</el-tag>
            <div class="priv-desc">{{ p.desc }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 功能状态 -->
    <el-card shadow="never" class="mt16">
      <template #header>
        <div class="card-title"><el-icon><Monitor /></el-icon> 当前状态</div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="开发者身份">{{ devInfo.is_developer ? '已激活' : '未激活' }}</el-descriptions-item>
        <el-descriptions-item label="套餐限制">全部豁免</el-descriptions-item>
        <el-descriptions-item label="实名要求">豁免（开发调试）</el-descriptions-item>
        <el-descriptions-item label="每日额度">无限</el-descriptions-item>
        <el-descriptions-item label="并发任务">无上限</el-descriptions-item>
        <el-descriptions-item label="导出限制">无限制</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 数据管理 -->
    <el-card shadow="never" class="mt16">
      <template #header>
        <div class="card-title"><el-icon><DataAnalysis /></el-icon> 开发者数据管理</div>
      </template>
      <el-alert type="info" :closable="false" show-icon
        title="演示环境说明" description="当前为 GitHub Pages 静态演示模式，数据为 Mock 演示数据。完整采集/管理功能需本地 Django 后端（127.0.0.1:8080）。" class="mb12" />
      <el-button type="danger" plain @click="onClearMock">重置演示数据</el-button>
      <el-button type="primary" plain @click="onReload">刷新页面</el-button>
      <el-button type="warning" plain @click="onGotoSystem">前往系统管理</el-button>
    </el-card>

    <!-- 权限矩阵 -->
    <el-card shadow="never" class="mt16">
      <template #header>
        <div class="card-title"><el-icon><Lock /></el-icon> 实名认证 & 防薅规则（演示配置）</div>
      </template>
      <el-table :data="rules" border size="small">
        <el-table-column prop="rule" label="规则" min-width="180" />
        <el-table-column prop="desc" label="说明" min-width="300" />
        <el-table-column prop="apply" label="对开发者" width="110">
          <template #default><el-tag type="success" size="small">豁免</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Cpu, Star, Monitor, DataAnalysis, Lock } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const devInfo = ref({ is_developer: false, privileges: [] })
const privileges = ref([])

const rules = [
  { rule: '实名认证强制', desc: '未实名仅可浏览，采集/AI/导出/增值购买锁死', apply: '豁免' },
  { rule: '一证一号', desc: '1张身份证仅认证1个账号', apply: '豁免' },
  { rule: '每日额度 0 点重置', desc: '线索/AI额度每日重置，无法绕过', apply: '豁免' },
  { rule: 'IP/设备管控', desc: '单IP24h最多2账号，多开拦截', apply: '豁免' },
  { rule: '静默降权', desc: '连续7天无付费额度减半，14天关闭采集', apply: '豁免' },
  { rule: '线索 30 天清理', desc: '仅付费套餐支持锁定备份', apply: '豁免' }
]

onMounted(async () => {
  try {
    const res = await api.get('/dev/options')
    devInfo.value = res.result || {}
    privileges.value = (res.result?.privileges || []).map(p => ({
      code: p.code, name: p.name, desc: p.desc
    }))
  } catch (e) {
    // 兜底：即使接口失败也展示
    privileges.value = [
      { code: 'unlimited', name: '无限采集', desc: '不消耗任何额度，并发无上限' },
      { code: 'unlimited_ai', name: '无限AI', desc: 'AI摘要/话术不限次数' },
      { code: 'dev_menu', name: '开发者菜单', desc: '专属开发者选项入口' }
    ]
  }
})

const onClearMock = async () => {
  await ElMessageBox.confirm('确定重置全部演示数据？此操作仅影响本地 Mock 数据。', '重置确认', { type: 'warning' })
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  ElMessage.success('演示数据已重置，请重新登录')
  router.push('/login')
}

const onReload = () => window.location.reload()
const onGotoSystem = () => router.push('/system')
</script>

<style scoped>
.dev-page { padding: 4px; }
.dev-banner { background: linear-gradient(135deg, #1f2d3d 0%, #2b3a4d 100%); border: none; }
.banner-inner { display: flex; align-items: center; gap: 16px; color: #fff; }
.banner-icon { color: #409EFF; }
.banner-title { font-size: 18px; font-weight: 600; }
.banner-sub { margin-top: 6px; color: #a6adb4; font-size: 13px; }
.ml8 { margin-left: 8px; }
.mt16 { margin-top: 16px; }
.mb12 { margin-bottom: 12px; }
.card-title { display: flex; align-items: center; gap: 6px; font-weight: 600; }
.priv-item { background: #f5f7fa; border: 1px solid #ebeef5; border-radius: 8px; padding: 12px; height: 100%; }
.priv-desc { margin-top: 8px; font-size: 12px; color: #909399; }
</style>
