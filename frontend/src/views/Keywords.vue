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

      <!-- 行业地域导航 · 12 行业获客词库 -->
      <el-divider content-position="left">行业地域导航 · 自动联想</el-divider>
      <div class="flex" style="gap: 8px; flex-wrap: wrap; margin-bottom: 12px">
        <el-select v-model="navIndustry" filterable placeholder="选择行业" style="width: 220px" @change="loadNav">
          <el-option v-for="ind in navIndustries" :key="ind.id" :label="ind.name" :value="ind.name" />
        </el-select>
        <el-select v-model="navCity" filterable placeholder="选择城市" style="width: 160px" @change="loadNav">
          <el-option v-for="city in cities" :key="city" :label="city" :value="city" />
        </el-select>
        <el-tag v-for="kw in navKeywords" :key="kw" closable @close="addFromNav(kw)" style="cursor: pointer">{{ kw }}</el-tag>
        <span v-if="navKeywords.length" style="font-size: 12px; color: #909399">点击标签即可添加关键词</span>
      </div>

      <!-- 12 行业导航卡片 -->
      <div class="industry-grid">
        <div v-for="ind in navIndustries" :key="ind.id" class="industry-card" @click="openIndustry(ind)">
          <div class="industry-card-head">
            <h4>{{ ind.name }}</h4>
            <el-tag v-if="isFollowed(ind.id)" type="success" size="small" effect="plain">已关注</el-tag>
          </div>
          <p class="industry-desc">{{ ind.description }}</p>
          <div class="keywords-preview">
            <el-tag v-for="kw in (ind.preview || []).slice(0, 4)" :key="kw" size="small" type="info" effect="plain" class="mr4">{{ kw }}</el-tag>
          </div>
        </div>
      </div>

      <!-- 行业词库弹窗 -->
      <el-dialog v-model="industryModal" :title="selectedIndustry ? selectedIndustry.name + ' · 获客词库' : '获客词库'" width="640px">
        <template v-if="selectedIndustry">
          <p class="industry-desc" style="margin-bottom: 12px">{{ selectedIndustry.description }}</p>
          <div class="lib-row">
            <span class="lib-label">主词</span>
            <el-tag v-for="w in modalMainWords" :key="w" type="primary" class="mr4 mb4" closable @close="addLibWord(w)">{{ w }}</el-tag>
          </div>
          <div class="lib-row">
            <span class="lib-label">长尾词</span>
            <el-tag v-for="w in modalLongTailWords" :key="w" type="success" class="mr4 mb4" closable @close="addLibWord(w)">{{ w }}</el-tag>
          </div>
          <div class="lib-row">
            <span class="lib-label">行业否定词</span>
            <el-tag v-for="w in modalNegativeWords" :key="w" type="info" class="mr4 mb4">{{ w }}</el-tag>
          </div>
          <div class="lib-row" v-if="modalGlobalNegative.length">
            <span class="lib-label">全局否定词</span>
            <el-tag v-for="w in modalGlobalNegative" :key="w" type="danger" effect="plain" class="mr4 mb4">{{ w }}</el-tag>
          </div>
        </template>
        <template #footer>
          <el-button v-if="selectedIndustry" type="warning" :loading="applying" @click="applyIndustry(selectedIndustry.name)">
            一键导入全部词
          </el-button>
          <el-button v-if="selectedIndustry && !isFollowed(selectedIndustry.id)" type="primary" @click="followIndustry(selectedIndustry.id)">
            关注此行业
          </el-button>
          <el-button v-if="selectedIndustry && isFollowed(selectedIndustry.id)" type="danger" plain @click="unfollowIndustry(selectedIndustry.id)">
            取消关注
          </el-button>
          <el-button @click="industryModal = false">关闭</el-button>
        </template>
      </el-dialog>

      <!-- 行业词库（12 大行业） -->
      <el-divider content-position="left">行业词库 · 12 大行业精选词（一键导入）</el-divider>
      <div class="flex" style="gap: 8px; flex-wrap: wrap; margin-bottom: 12px">
        <el-select v-model="libIndustry" filterable placeholder="选择行业词库" style="width: 220px" @change="loadLibrary">
          <el-option v-for="ind in libIndustries" :key="ind" :label="ind" :value="ind" />
        </el-select>
        <el-button v-if="libIndustry" type="warning" :loading="applying" @click="applyLibrary">
          一键导入「{{ libIndustry }}」
        </el-button>
        <span v-if="libIndustry" style="font-size: 12px; color: #909399">
          共 {{ libMainWords.length + libLongTailWords.length }} 词 · 自动分组「行业词库-{{ libIndustry }}」
        </span>
      </div>
      <div v-if="libIndustry" class="lib-box">
        <div class="lib-row">
          <span class="lib-label">主词</span>
          <el-tag v-for="w in libMainWords" :key="w" type="primary" class="mr4 mb4" closable @close="addLibWord(w)">{{ w }}</el-tag>
        </div>
        <div class="lib-row">
          <span class="lib-label">长尾词</span>
          <el-tag v-for="w in libLongTailWords" :key="w" type="success" class="mr4 mb4" closable @close="addLibWord(w)">{{ w }}</el-tag>
        </div>
        <div class="lib-row">
          <span class="lib-label">行业否定词</span>
          <el-tag v-for="w in libNegativeWords" :key="w" type="info" class="mr4 mb4">{{ w }}</el-tag>
        </div>
        <div class="lib-row" v-if="libGlobalNegative.length">
          <span class="lib-label">全局否定词</span>
          <el-tag v-for="w in libGlobalNegative" :key="w" type="danger" effect="plain" class="mr4 mb4">{{ w }}</el-tag>
        </div>
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

// 行业导航（12 行业获客词库）
const navIndustries = ref([])
const cities = ref([])
const navIndustry = ref('')
const navCity = ref('')
const navKeywords = ref([])
const industryModal = ref(false)
const selectedIndustry = ref(null)
const modalMainWords = ref([])
const modalLongTailWords = ref([])
const modalNegativeWords = ref([])
const modalGlobalNegative = ref([])
const followedIndustries = ref([])

// 行业词库
const libIndustries = ref([])
const libIndustry = ref('')
const libMainWords = ref([])
const libLongTailWords = ref([])
const libNegativeWords = ref([])
const libGlobalNegative = ref([])
const applying = ref(false)

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
  navIndustries.value = data.results.industries || []
  cities.value = data.results.cities || []
  loadFollowed()
}

const loadNav = () => {
  if (!navIndustry.value) return
  api.get('/misc/industry-nav', { params: { industry: navIndustry.value, city: navCity.value } })
    .then(d => { navKeywords.value = d.results.keywords || [] })
}

// ---------- 12 行业卡片 ----------
const openIndustry = async ind => {
  selectedIndustry.value = ind
  industryModal.value = true
  modalMainWords.value = []
  modalLongTailWords.value = []
  modalNegativeWords.value = []
  modalGlobalNegative.value = []
  try {
    const data = await api.get('/misc/industry-nav', { params: { industry: ind.name } })
    modalMainWords.value = data.results.mainWords || []
    modalLongTailWords.value = data.results.longTailWords || []
    modalNegativeWords.value = data.results.negativeWords || []
    modalGlobalNegative.value = data.results.globalNegativeWords || []
  } catch (e) {
    // 行业词库接口失败时用卡片 preview
    modalMainWords.value = ind.preview || []
  }
}

const applyIndustry = async name => {
  applying.value = true
  try {
    const data = await api.post('/keywords/industry-apply', { industry: name })
    ElMessage.success(`已导入 ${data.result.created} 个词（跳过 ${data.result.skipped} 个重复）`)
    load()
    loadGroups()
  } finally {
    applying.value = false
  }
}

const isFollowed = id => followedIndustries.value.some(x => x.id === id)

const loadFollowed = async () => {
  try {
    const data = await api.get('/promoter/industries')
    followedIndustries.value = data.results.industries || []
  } catch (e) {
    followedIndustries.value = []
  }
}

const followIndustry = async id => {
  const ids = [...followedIndustries.value.map(x => x.id), id]
  await api.post('/promoter/industries', { industryIds: ids })
  ElMessage.success('关注成功')
  loadFollowed()
}

const unfollowIndustry = async id => {
  const ids = followedIndustries.value.filter(x => x.id !== id).map(x => x.id)
  await api.post('/promoter/industries', { industryIds: ids })
  ElMessage.success('已取消关注')
  loadFollowed()
}

const addFromNav = async kw => {
  await api.post('/keywords/', { word: kw })
  ElMessage.success(`已添加「${kw}」`)
  load()
}

// ---------- 行业词库 ----------
const loadLibraryList = async () => {
  try {
    const data = await api.get('/keywords/industry-library')
    libIndustries.value = data.result.industries
  } catch (e) {
    libIndustries.value = []
  }
}

const loadLibrary = async () => {
  if (!libIndustry.value) return
  const data = await api.get('/keywords/industry-library', { params: { industry: libIndustry.value } })
  libMainWords.value = data.result.mainWords || []
  libLongTailWords.value = data.result.longTailWords || []
  libNegativeWords.value = data.result.negativeWords || []
  libGlobalNegative.value = data.result.globalNegativeWords || []
}

const addLibWord = async w => {
  await api.post('/keywords/', { word: w, negative_words: libNegativeWords.value.join(',') })
  ElMessage.success(`已添加「${w}」`)
  load()
}

const applyLibrary = async () => {
  if (!libIndustry.value) return
  applying.value = true
  try {
    const data = await api.post('/keywords/industry-apply', { industry: libIndustry.value })
    ElMessage.success(`已导入 ${data.result.created} 个词（跳过 ${data.result.skipped} 个重复）`)
    load()
    loadGroups()
  } finally {
    applying.value = false
  }
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
  loadLibraryList()
})
</script>

<style scoped>
.mr4 { margin-right: 4px; }
.mb4 { margin-bottom: 4px; }
.lib-box {
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  background: #fafafa;
}
.lib-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.lib-label {
  flex: 0 0 90px;
  font-size: 13px;
  color: #606266;
  font-weight: 600;
  padding-top: 4px;
}

.industry-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.industry-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
}
.industry-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
  border-color: #409eff;
}
.industry-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.industry-card-head h4 {
  margin: 0;
  font-size: 15px;
  color: #303133;
}
.industry-desc {
  margin: 0 0 8px;
  font-size: 12px;
  color: #909399;
}
.keywords-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
</style>
