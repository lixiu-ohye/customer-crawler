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
        <el-menu-item index="/leads"><el-icon><User /></el-icon><span>线索库</span></el-menu-item>
        <el-menu-item index="/heatmap"><el-icon><MapLocation /></el-icon><span>地图热力图</span></el-menu-item>
        <el-menu-item index="/analysis"><el-icon><MagicStick /></el-icon><span>AI 分析</span></el-menu-item>
        <el-menu-item index="/member"><el-icon><Wallet /></el-icon><span>会员中心</span></el-menu-item>
        <el-menu-item index="/disclaimer"><el-icon><Document /></el-icon><span>合规声明</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-title">{{ $route.meta.title || '' }}</div>
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
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

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
.header-title { font-size: 16px; font-weight: 600; color: #303133; }
.user-name { display: flex; align-items: center; gap: 6px; cursor: pointer; color: #606266; }
.avatar { background: #409EFF; color: #fff; font-size: 14px; }
.mr8 { margin-right: 8px; }
.main { padding: 16px; background: #f0f2f5; }
</style>
