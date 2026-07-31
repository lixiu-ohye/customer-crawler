<template>
  <div>
    <div class="page-card">
      <div class="flex-between">
        <div class="flex" style="gap: 8px">
          <el-input v-model="search" placeholder="搜索任务" clearable style="width: 200px" @keyup.enter="load" />
          <el-select v-model="statusFilter" placeholder="全部状态" clearable style="width: 130px" @change="load">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
          <el-button type="primary" @click="load">查询</el-button>
        </div>
        <el-button type="primary" @click="openCreate">新建任务</el-button>
      </div>

      <el-table :data="list" v-loading="loading" class="mt16" stripe>
        <el-table-column prop="name" label="任务名称" min-width="140" />
        <el-table-column prop="keywords" label="关键词" min-width="160" show-overflow-tooltip />
        <el-table-column label="平台" width="200">
          <template #default="{ row }">
            <el-tag v-for="p in row.platforms" :key="p" size="small" class="mr4">{{ platformMap[p] || p }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType[row.status] || 'info'" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="180">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="row.status === 'failed' ? 'exception' : row.status === 'completed' ? 'success' : ''" />
          </template>
        </el-table-column>
        <el-table-column prop="message" label="信息" min-width="140" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="230" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending' || row.status === 'paused'" size="small" type="success" @click="act(row, 'start')">启动</el-button>
            <el-button v-if="row.status === 'running'" size="small" type="warning" @click="act(row, 'pause')">暂停</el-button>
            <el-button v-if="row.status === 'paused'" size="small" @click="act(row, 'resume')">继续</el-button>
            <el-button v-if="row.status === 'running'" size="small" type="danger" plain @click="act(row, 'stop')">终止</el-button>
            <el-button v-if="row.status === 'failed'" size="small" @click="act(row, 'retry')">重试</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="createVisible" title="新建采集任务" width="520px">
      <el-form label-width="80px">
        <el-form-item label="任务名称">
          <el-input v-model="createForm.name" placeholder="留空则取关键词前20字" />
        </el-form-item>
        <el-form-item label="关键词" required>
          <el-input v-model="createForm.keywords" placeholder="逗号分隔，如：装修,全屋定制" />
        </el-form-item>
        <el-form-item label="平台" required>
          <el-checkbox-group v-model="createForm.platforms">
            <el-checkbox v-for="(v, k) in platformMap" :key="k" :value="k">{{ v }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="页数">
          <el-input-number v-model="createForm.pages" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="定时">
          <el-select v-model="createForm.schedule_type" clearable placeholder="不启用定时" style="width: 100%">
            <el-option label="每天" value="daily" />
            <el-option label="每周" value="weekly" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="create">创建并启动</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const list = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')
const createVisible = ref(false)
const creating = ref(false)
const createForm = reactive({ name: '', keywords: '', platforms: [], pages: 1, schedule_type: '' })

const platformMap = { douyin: '抖音', xiaohongshu: '小红书', kuaishou: '快手', weibo: '微博', zhihu: '知乎', tieba: '贴吧' }
const statusMap = { pending: '待启动', running: '运行中', paused: '已暂停', completed: '已完成', failed: '失败', stopped: '已终止' }
const statusType = { pending: 'info', running: 'primary', paused: 'warning', completed: 'success', failed: 'danger', stopped: 'info' }

let timer = null

const load = async () => {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    if (search.value) params.q = search.value
    const data = await api.get('/tasks/', { params })
    list.value = data.results
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  Object.assign(createForm, { name: '', keywords: '', platforms: [], pages: 1, schedule_type: '' })
  createVisible.value = true
}

const create = async () => {
  if (!createForm.keywords.trim()) {
    ElMessage.warning('请填写关键词')
    return
  }
  if (!createForm.platforms.length) {
    ElMessage.warning('请选择平台')
    return
  }
  creating.value = true
  try {
    await api.post('/tasks/', createForm)
    ElMessage.success('任务已创建并启动')
    createVisible.value = false
    load()
  } finally {
    creating.value = false
  }
}

const act = async (row, action) => {
  await api.post(`/tasks/${row.id}`, { action })
  const map = { start: '已启动', pause: '已暂停', resume: '已继续', stop: '已终止', retry: '已重试' }
  ElMessage.success(map[action])
  load()
}

const remove = async row => {
  await ElMessageBox.confirm(`确定删除任务「${row.name}」？`, '提示', { type: 'warning' })
  await api.post(`/tasks/${row.id}`, { action: 'delete' })
  ElMessage.success('已删除')
  load()
}

onMounted(() => {
  load()
  timer = setInterval(load, 5000)
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.mr4 { margin-right: 4px; }
</style>
