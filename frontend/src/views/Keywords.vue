<template>
  <div>
    <div class="page-card">
      <div class="flex-between mb16">
        <div class="flex" style="gap: 8px">
          <el-input v-model="search" placeholder="搜索关键词" clearable style="width: 200px" @keyup.enter="load" />
          <el-select v-model="groupFilter" placeholder="全部分组" clearable style="width: 140px" @change="load">
            <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
          <el-button type="primary" @click="load">查询</el-button>
        </div>
        <div class="flex" style="gap: 8px">
          <el-button type="primary" @click="openExpand">AI 拓词</el-button>
          <el-button type="success" @click="openAdd">新增关键词</el-button>
        </div>
      </div>

      <!-- 行业地点导航 -->
      <el-divider content-position="left">行业地点导航 · 自动联想</el-divider>
      <div class="flex" style="gap: 8px; flex-wrap: wrap">
        <el-select v-model="navIndustry" filterable placeholder="选择行业" style="width: 200px" @change="loadNav">
          <el-option v-for="ind in industries" :key="ind" :label="ind" :value="ind" />
        </el-select>
        <el-select v-model="navCity" filterable placeholder="选择城市" style="width: 160px" @change="loadNav">
          <el-option v-for="city in cities" :key="city" :label="city" :value="city" />
        </el-select>
        <el-tag v-for="kw in navKeywords" :key="kw" closable @close="addFromNav(kw)" style="cursor: pointer">{{ kw }}</el-tag>
        <span v-if="navKeywords.length" style="font-size: 12px; color: #909399">点击标签添加为关键词</span>
      </div>

      <el-table :data="list" v-loading="loading" class="mt16" stripe>
        <el-table-column prop="word" label="关键词" min-width="140" />
        <el-table-column prop="group_name" label="分组" width="100">
          <template #default="{ row }">{{ row.group_name || '未分组' }}</template>
        </el-table-column>
        <el-table-column prop="negative_words" label="否定词" min-width="160">
          <template #default="{ row }">
            <el-tag v-for="w in (row.negative_words || '').split(',').filter(Boolean)" :key="w" size="small" type="info" class="mr4">{{ w }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hit_count" label="命中数" width="90" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/编辑 -->
    <el-dialog v-model="dialogVisible" :title="editing ? '编辑关键词' : '新增关键词'" width="480px">
      <el-form label-width="80px">
        <el-form-item label="关键词" required>
          <el-input v-model="form.word" placeholder="如：装修、全屋定制" />
        </el-form-item>
        <el-form-item label="分组">
          <el-select v-model="form.group" clearable placeholder="选择分组" style="width: 100%">
            <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="否定词">
          <el-input v-model="form.negative_words" placeholder="逗号分隔，如：不需要,避雷,广告" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <!-- AI 拓词 -->
    <el-dialog v-model="expandVisible" title="AI 智能拓词" width="520px">
      <el-form label-width="80px">
        <el-form-item label="种子词" required>
          <el-input v-model="expandForm.seed" placeholder="如：装修" />
        </el-form-item>
        <el-form-item label="行业">
          <el-select v-model="expandForm.industry" filterable placeholder="选择行业" style="width: 100%">
            <el-option v-for="ind in industries" :key="ind" :label="ind" :value="ind" />
          </el-select>
        </el-form-item>
        <el-form-item label="城市">
          <el-select v-model="expandForm.city" filterable placeholder="选择城市（可空）" style="width: 100%">
            <el-option v-for="city in cities" :key="city" :label="city" :value="city" />
          </el-select>
        </el-form-item>
      </el-form>
      <div v-if="expanded.length" class="mt16">
        <div class="mb16" style="font-size: 13px; color: #909399">拓词结果（点击添加）:</div>
        <el-tag v-for="w in expanded" :key="w" closable @close="addExpanded(w)" class="mb4 mr4" style="cursor: pointer">{{ w }}</el-tag>
      </div>
      <template #footer>
        <el-button @click="expandVisible = false">关闭</el-button>
        <el-button type="primary" :loading="expanding" @click="doExpand">开始拓词</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const list = ref([])
const groups = ref([])
const loading = ref(false)
const search = ref('')
const groupFilter = ref(null)
const dialogVisible = ref(false)
const editing = ref(null)
const form = reactive({ word: '', group: null, negative_words: '' })

// 行业导航
const industries = ref([])
const cities = ref([])
const navIndustry = ref('')
const navCity = ref('')
const navKeywords = ref([])

// AI 拓词
const expandVisible = ref(false)
const expanding = ref(false)
const expanded = ref([])
const expandForm = reactive({ seed: '', industry: '', city: '' })

const load = async () => {
  loading.value = true
  try {
    const params = {}
    if (search.value) params.q = search.value
    if (groupFilter.value) params.group = groupFilter.value
    const data = await api.get('/keywords/', { params })
    list.value = data.results
  } finally {
    loading.value = false
  }
}

const loadGroups = async () => {
  const data = await api.get('/keywords/groups')
  groups.value = data.results
}

const loadNavData = async () => {
  const data = await api.get('/misc/industry-nav')
  industries.value = data.results.industries
  cities.value = data.results.cities
}

const loadNav = () => {
  if (!navIndustry.value) return
  api.get('/misc/industry-nav', { params: { industry: navIndustry.value, city: navCity.value } })
    .then(d => { navKeywords.value = d.results.keywords })
}

const addFromNav = async kw => {
  await api.post('/keywords/', { word: kw })
  ElMessage.success(`已添加「${kw}」`)
  load()
}

const openAdd = () => {
  editing.value = null
  Object.assign(form, { word: '', group: null, negative_words: '' })
  dialogVisible.value = true
}

const openEdit = row => {
  editing.value = row
  Object.assign(form, { word: row.word, group: row.group, negative_words: row.negative_words })
  dialogVisible.value = true
}

const save = async () => {
  if (!form.word) {
    ElMessage.warning('请填写关键词')
    return
  }
  if (editing.value) {
    await api.put(`/keywords/${editing.value.id}`, form)
    ElMessage.success('已更新')
  } else {
    await api.post('/keywords/', form)
    ElMessage.success('已添加')
  }
  dialogVisible.value = false
  load()
}

const remove = async row => {
  await ElMessageBox.confirm(`确定删除关键词「${row.word}」？`, '提示', { type: 'warning' })
  await api.delete(`/keywords/${row.id}`)
  ElMessage.success('已删除')
  load()
}

const openExpand = () => {
  expandForm.seed = ''
  expandForm.industry = ''
  expandForm.city = ''
  expanded.value = []
  expandVisible.value = true
}

const doExpand = async () => {
  if (!expandForm.seed) {
    ElMessage.warning('请填写种子词')
    return
  }
  expanding.value = true
  try {
    const data = await api.post('/keywords/expand', expandForm)
    expanded.value = data.expanded
    ElMessage.success(`拓词完成，共 ${data.created} 个新词`)
    load()
  } finally {
    expanding.value = false
  }
}

const addExpanded = async w => {
  await api.post('/keywords/', { word: w })
  ElMessage.success(`已添加「${w}」`)
  load()
}

onMounted(() => {
  load()
  loadGroups()
  loadNavData()
})
</script>

<style scoped>
.mr4 { margin-right: 4px; }
.mb4 { margin-bottom: 4px; }
</style>
