<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">
        <el-icon :size="24" color="#409EFF"><DataAnalysis /></el-icon>
        <span>客户大数据平台</span>
      </div>
      <el-menu :default-active="$route.path" router background-color="#001529" text-color="#a6adb4" active-text-color="#fff">
        <el-menu-item index="/dashboard"><el-icon><Odometer /></el-icon><span>数据大盘</span></el-menu-item>
        <el-menu-item index="/keywords"><el-icon><Search /></el-icon><span>关键词管理</span></el-menu-item>
        <el-menu-item index="/tasks"><el-icon><VideoPlay /></el-icon><span>任务中心</span></el-menu-item>
        <el-menu-item index="/industry-batch"><el-icon><Aim /></el-icon><span>行业批量采集</span></el-menu-item>
        <el-menu-item index="/realleads">
        <el-icon><DataLine /></el-icon>
        <span>真实数据</span>
      </el-menu-item>
      <el-menu-item index="/official"><el-icon><Connection /></el-icon><span>官方API采集</span></el-menu-item>
        <el-menu-item index="/leads"><el-icon><User /></el-icon><span>线索库</span></el-menu-item>
        <el-menu-item index="/heatmap"><el-icon><MapLocation /></el-icon><span>地图热力图</span></el-menu-item>
        <el-menu-item index="/analysis"><el-icon><MagicStick /></el-icon><span>AI 分析</span></el-menu-item>
        <el-menu-item index="/member"><el-icon><Wallet /></el-icon><span>会员中心</span></el-menu-item>
        <el-menu-item index="/system"><el-icon><Setting /></el-icon><span>系统管理</span></el-menu-item>
      <el-menu-item v-if="isDeveloper" index="/dev"><el-icon><Cpu /></el-icon><span>开发者选项</span></el-menu-item>
      <el-menu-item v-if="isDeveloper" index="/devadmin"><el-icon><DataAnalysis /></el-icon><span>开发者总后台</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <div class="header-title">{{ $route.meta.title || '' }}</div>
          <el-autocomplete
            v-model="globalKeyword"
            :fetch-suggestions="globalSuggest"
            placeholder="全局搜索：行业 / 地域 / 关键词"
            clearable
            style="width: 280px; margin-left: 16px"
            @select="goGlobalSearch"
            @keyup.enter="goGlobalSearch"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-autocomplete>
        </div>
        <div class="flex">
          <el-tag v-if="auth.isAdmin" type="danger" size="small" effect="dark" class="mr8">管理员</el-tag>
          <el-dropdown @command="handleCommand">
            <span class="user-name">
              <el-avatar :size="28" class="avatar">{{ (auth.user?.nickname || auth.user?.username || 'U').slice(0,1).toUpperCase() }}</el-avatar>
              {{ auth.user?.nickname || auth.user?.username }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="member">会员中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
      <el-footer class="footer">
        <span>本平台仅用于合法合规的商业调研与客户开发 · 禁止骚扰、诈骗、侵犯隐私等违法用途 · 数据 30 天自动清理</span>
        <el-link type="primary" underline="never" @click="goDisclaimer">《合规与免责声明》</el-link>
      </el-footer>
    </el-container>
    <!-- 全站悬浮推广气泡 -->
    <FloatingBubble />
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { Cpu, DataAnalysis, Connection, Aim, Search } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { ref, computed } from 'vue'
import FloatingBubble from '../components/FloatingBubble.vue'

const router = useRouter()
const auth = useAuthStore()
const globalKeyword = ref('')

// 全局搜索联想：行业 + 地域
const GLOBAL_SUGGESTIONS = [
  { value: '装修家居' }, { value: '法律行业' }, { value: '美业医美' },
  { value: '本地生活家政服务' }, { value: '汽车服务行业' }, { value: '教育培训' },
  { value: '宠物行业' }, { value: '房产同城服务' }, { value: '婚庆摄影' },
  { value: '口腔健康理疗' }, { value: '工程建材行业' }, { value: '互联网服务商' },
  { value: '企业B端财税商务服务' },
  { value: '北京' }, { value: '上海' }, { value: '广州' }, { value: '深圳' },
  { value: '杭州' }, { value: '成都' }, { value: '武汉' }, { value: '南京' },
  { value: '苏州' }, { value: '西安' }, { value: '郑州' }, { value: '长沙' },
  { value: '重庆' }, { value: '天津' }, { value: '青岛' }, { value: '宁波' },
]

const globalSuggest = (query, cb) => {
  const q = (query || '').trim().toLowerCase()
  if (!q) return cb(GLOBAL_SUGGESTIONS.slice(0, 8))
  const list = GLOBAL_SUGGESTIONS.filter(s => s.value.toLowerCase().includes(q)).slice(0, 10)
  cb(list)
}

// 全局搜索跳转：去真实数据页并带参数
const goGlobalSearch = () => {
  const q = globalKeyword.value.trim()
  if (!q) return
  router.push({ path: '/realleads', query: { kw: q } })
}

// 开发者特权：admin/admin123456 账号永久免费 + 开发者选项
const isDeveloper = computed(() => {
  const u = auth.user
  return !!(u && (u.username === 'admin' || u.role_type === 'admin' || u.is_developer))
})

const goDisclaimer = () => router.push('/disclaimer')

const handleCommand = async command => {
  if (command === 'member') {
    router.push('/member')
  } else if (command === 'logout') {
    await ElMessageBox.confirm('确定退出登录吗？', '提示', { type: 'warning' })
    auth.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout { min-height: 100vh; }
.aside { background: #001529; }
.logo { height: 60px; display: flex; align-items: center; justify-content: center; gap: 8px; color: #fff; font-weight: 600; font-size: 15px; }
.aside :deep(.el-menu) { border-right: none; }
.header { background: #fff; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,.08); z-index: 1; }
.header-left { display: flex; align-items: center; }
.header-title { font-size: 16px; font-weight: 600; color: #303133; }
.user-name { display: flex; align-items: center; gap: 6px; cursor: pointer; color: #606266; }
.avatar { background: #409EFF; color: #fff; font-size: 14px; }
.mr8 { margin-right: 8px; }
.main { padding: 16px; background: #f0f2f5; }
.footer { height: 40px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #fff; color: #909399; font-size: 12px; border-top: 1px solid #ebeef5; }
</style>
