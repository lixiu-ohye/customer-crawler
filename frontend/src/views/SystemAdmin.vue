<template>
  <div class="page-card">
    <div class="page-title">系统管理</div>
    <el-tabs v-model="activeTab">
      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="users">
        <div class="toolbar">
          <el-input v-model="userQuery" placeholder="搜索用户名/昵称" clearable style="width: 220px" @input="loadUsers" />
          <el-button type="primary" @click="openUserDialog">新增用户</el-button>
        </div>
        <el-table :data="users" border stripe v-loading="loadingUsers">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label="用户名" min-width="110" />
          <el-table-column prop="nickname" label="昵称" min-width="110" />
          <el-table-column prop="email" label="邮箱" min-width="160" />
          <el-table-column label="角色" width="100">
            <template #default="{ row }">
              <el-tag :type="row.role_type === 'admin' ? 'danger' : 'primary'" size="small">{{ row.role_type === 'admin' ? '管理员' : '普通用户' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="套餐" width="90">
            <template #default="{ row }">
              <el-tag :type="row.plan?.plan_type === 'premium' ? 'warning' : 'info'" size="small">{{ row.plan?.plan_type === 'premium' ? '高级版' : '免费版' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="注册时间" width="160" />
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="openUserDialog(row)">编辑</el-button>
              <el-button size="small" text :type="row.is_active ? 'danger' : 'success'" @click="toggleUser(row)">{{ row.is_active ? '禁用' : '启用' }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 参数配置 -->
      <el-tab-pane label="参数配置" name="params">
        <el-form label-width="180px" style="max-width: 640px" v-loading="loadingParams">
          <el-divider content-position="left">采集风控</el-divider>
          <el-form-item label="采集最小间隔(秒)">
            <el-input-number v-model="params.min_interval" :min="1" :max="60" />
          </el-form-item>
          <el-form-item label="每分钟请求上限">
            <el-input-number v-model="params.max_per_minute" :min="1" :max="120" />
          </el-form-item>
          <el-form-item label="失败重试次数">
            <el-input-number v-model="params.retry_times" :min="0" :max="10" />
          </el-form-item>
          <el-divider content-position="left">意向打分</el-divider>
          <el-form-item label="高意向阈值(分)">
            <el-input-number v-model="params.high_intent_threshold" :min="50" :max="95" />
          </el-form-item>
          <el-form-item label="数据保留天数">
            <el-input-number v-model="params.retention_days" :min="1" :max="90" />
            <span class="tip">到期自动删除（合规要求默认 30 天）</span>
          </el-form-item>
          <el-divider content-position="left">采集模式</el-divider>
          <el-form-item label="数据采集模式">
            <el-radio-group v-model="params.mode">
              <el-radio value="crawler">爬虫模式</el-radio>
              <el-radio value="api">官方 API 模式</el-radio>
              <el-radio value="mock">演示模式</el-radio>
            </el-radio-group>
            <div class="tip">爬虫模式采集公开信息；API 模式对接官方商业接口，更合规稳定</div>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveParams">保存配置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 日志管理 -->
      <el-tab-pane label="日志管理" name="logs">
        <div class="toolbar">
          <el-select v-model="logType" style="width: 140px" @change="loadLogs">
            <el-option label="全部日志" value="" />
            <el-option label="操作日志" value="operation" />
            <el-option label="采集日志" value="crawl" />
          </el-select>
          <el-button @click="loadLogs">刷新</el-button>
        </div>
        <el-table :data="logs" border stripe v-loading="loadingLogs">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column label="类型" width="90">
            <template #default="{ row }">
              <el-tag :type="row.type === 'crawl' ? 'warning' : 'primary'" size="small">{{ row.type === 'crawl' ? '采集' : '操作' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="action" label="动作" min-width="180" />
          <el-table-column prop="detail" label="详情" min-width="260" show-overflow-tooltip />
          <el-table-column prop="ip" label="IP" width="130" />
          <el-table-column prop="created_at" label="时间" width="170" />
        </el-table>
      </el-tab-pane>

      <!-- 模式切换 -->
      <el-tab-pane label="模式切换" name="mode">
        <el-descriptions :column="1" border style="max-width: 640px">
          <el-descriptions-item label="当前采集模式">
            <el-tag :type="modeTagType" size="small">{{ modeText }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="爬虫模式">
            通过公开接口采集六大平台（抖音/小红书/快手/微博/知乎/贴吧）公开内容，内置风控限速与合规过滤
          </el-descriptions-item>
          <el-descriptions-item label="官方 API 模式">
            对接平台官方商业数据接口，合规授权、数据稳定，适合企业级商用
          </el-descriptions-item>
          <el-descriptions-item label="演示模式">
            使用内置演示数据，无需后端即可体验全部功能（当前线上部署模式）
          </el-descriptions-item>
        </el-descriptions>
        <div class="mode-actions">
          <el-button type="primary" @click="switchMode('crawler')">切换到爬虫模式</el-button>
          <el-button @click="switchMode('api')">切换到 API 模式</el-button>
          <el-button @click="switchMode('mock')">切换到演示模式</el-button>
        </div>
        <el-alert type="info" :closable="false" class="mt16" title="提示：模式切换后需重新启动采集任务方可生效；线上静态演示环境始终使用演示模式。" />
      </el-tab-pane>
    </el-tabs>

    <!-- 新增/编辑用户弹窗 -->
    <el-dialog v-model="userDialogVisible" :title="userForm.id ? '编辑用户' : '新增用户'" width="480px">
      <el-form :model="userForm" label-width="80px">
        <el-form-item label="用户名" required>
          <el-input v-model="userForm.username" :disabled="!!userForm.id" placeholder="登录账号" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="userForm.nickname" placeholder="显示昵称" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" placeholder="邮箱" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="userForm.role_type" style="width: 100%">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!userForm.id" label="密码" required>
          <el-input v-model="userForm.password" type="password" show-password placeholder="初始密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const activeTab = ref('users')

// ---------- 用户管理 ----------
const users = ref([])
const loadingUsers = ref(false)
const userQuery = ref('')
const userDialogVisible = ref(false)
const userForm = ref({})

const loadUsers = async () => {
  loadingUsers.value = true
  try {
    const data = await api.get('/admin/users', { params: { q: userQuery.value } })
    users.value = data.results || data || []
  } finally {
    loadingUsers.value = false
  }
}

const openUserDialog = row => {
  userForm.value = row ? { ...row, password: '' } : { username: '', nickname: '', email: '', role_type: 'user', password: '' }
  userDialogVisible.value = true
}

const saveUser = async () => {
  if (!userForm.value.username || (!userForm.value.id && !userForm.value.password)) {
    ElMessage.warning('用户名和密码必填')
    return
  }
  if (userForm.value.id) {
    await api.put(`/admin/users/${userForm.value.id}`, userForm.value)
  } else {
    await api.post('/admin/users', userForm.value)
  }
  userDialogVisible.value = false
  ElMessage.success('保存成功')
  loadUsers()
}

const toggleUser = async row => {
  await api.post(`/admin/users/${row.id}`, { action: 'toggle' })
  ElMessage.success(row.is_active ? '已禁用' : '已启用')
  loadUsers()
}

// ---------- 参数配置 ----------
const params = ref({})
const loadingParams = ref(false)

const loadParams = async () => {
  loadingParams.value = true
  try {
    const data = await api.get('/admin/params')
    params.value = data.result || data || {}
  } finally {
    loadingParams.value = false
  }
}

const saveParams = async () => {
  await api.post('/admin/params', params.value)
  ElMessage.success('配置已保存')
}

// ---------- 日志管理 ----------
const logs = ref([])
const loadingLogs = ref(false)
const logType = ref('')

const loadLogs = async () => {
  loadingLogs.value = true
  try {
    const data = await api.get('/admin/logs', { params: { type: logType.value } })
    logs.value = data.results || data || []
  } finally {
    loadingLogs.value = false
  }
}

// ---------- 模式切换 ----------
const mode = ref('mock')
const modeText = computed(() => ({ crawler: '爬虫模式', api: '官方 API 模式', mock: '演示模式' }[mode.value] || mode.value))
const modeTagType = computed(() => ({ crawler: 'warning', api: 'success', mock: 'info' }[mode.value] || 'info'))

const loadMode = async () => {
  try {
    const data = await api.get('/admin/mode')
    mode.value = (data.result || {}).mode || 'mock'
  } catch { mode.value = 'mock' }
}

const switchMode = async m => {
  const data = await api.post('/admin/mode', { mode: m })
  mode.value = (data.result || {}).mode || m
  ElMessage.success(`已切换到${modeText.value}`)
}

onMounted(() => {
  loadUsers()
  loadParams()
  loadLogs()
  loadMode()
})
</script>

<style scoped>
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.tip { margin-left: 12px; color: #909399; font-size: 12px; }
.mode-actions { margin-top: 16px; display: flex; gap: 12px; }
.mt16 { margin-top: 16px; }
</style>
