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
      <el-divider content-position="left">行业地域导航 · 自动联想 · 客户线索</el-divider>
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


      <div class="lead-section-title">📋 客户线索（按行业 · 地域 · 领域 · 场景筛选 · 高意向优先）</div>
      <div class="flex" style="gap: 8px; flex-wrap: wrap; margin-bottom: 12px">
        <el-select v-model="leadIndustry" filterable placeholder="线索行业" style="width: 180px" clearable @change="loadLeads">
          <el-option v-for="ind in navIndustries" :key="ind.id" :label="ind.name" :value="ind.name" />
        </el-select>
        <el-select v-model="leadRegion" filterable placeholder="线索地域" style="width: 140px" clearable @change="loadLeads">
          <el-option v-for="city in cities" :key="city" :label="city" :value="city" />
        </el-select>
        <el-select v-model="leadField" filterable placeholder="细分领域" style="width: 160px" clearable @change="onLeadFieldChange">
          <el-option v-for="f in leadFields" :key="f" :label="f" :value="f" />
        </el-select>
        <el-select v-model="leadScenario" filterable placeholder="问题场景" style="width: 160px" clearable @change="loadLeads">
          <el-option v-for="s in leadScenarios" :key="s" :label="s" :value="s" />
        </el-select>
        <el-select v-model="leadIntent" filterable placeholder="意向分 ≥" style="width: 120px" clearable @change="loadLeads">
          <el-option v-for="v in [60, 70, 80, 90]" :key="v" :label="v + ' 分以上'" :value="v" />
        </el-select>
        <el-button type="primary" plain @click="loadLeads">查询线索</el-button>
        <el-button @click="resetLeads">重置</el-button>
      </div>
      <el-alert v-if="leadFields.length" :title="leadHint" type="info" :closable="false" show-icon style="margin-bottom: 12px" />
      <el-table :data="pagedLeads" v-loading="leadsLoading" stripe class="mt16" @selection-change="onLeadSelect">
        <el-table-column type="selection" width="44" />
        <el-table-column prop="industry" label="行业" width="130">
          <template #default="{ row }"><el-tag size="small" type="primary" effect="plain">{{ row.industry }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="region" label="地域" width="90" />
        <el-table-column prop="field" label="细分领域" width="120" />
        <el-table-column prop="scenario" label="问题场景" width="130" />
        <el-table-column prop="need" label="客户需求" min-width="180" show-overflow-tooltip />
        <el-table-column prop="contact" label="联系人" width="90" />
        <el-table-column prop="phone" label="联系方式" width="120" />
        <el-table-column prop="intent" label="意向分" width="90">
          <template #default="{ row }">
            <el-tag :type="row.intent >= 90 ? 'danger' : row.intent >= 80 ? 'warning' : 'info'" size="small">{{ row.intent }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openLeadDetail(row)">详情</el-button>
            <el-button size="small" type="primary" plain :disabled="row.status !== '待跟进'" @click="claimLead(row)">领取</el-button>
          </template>
        </el-table-column>
        <div class="flex" style="gap: 8px; margin: 10px 0; align-items: center">
          <el-button size="small" type="success" plain :disabled="!selectedLeads.length" @click="batchClaim">批量领取（{{ selectedLeads.length }}）</el-button>
          <span style="font-size: 12px; color: #909399">已领取 {{ claimedLeads.length }} 条 · 共 {{ leads.length }} 条</span>
        </div>
        <el-pagination
          v-model:current-page="leadPage"
          :page-size="leadPageSize"
          :total="leads.length"
          layout="prev, pager, next, total"
          small
          background
          style="justify-content: flex-end; margin-top: 8px"
        />
      </el-table>
      <div v-if="!leads.length && !leadsLoading" style="text-align:center; color:#909399; padding: 24px 0">
        暂无匹配线索，试试调整筛选条件或选择法律行业查看深度线索
      </div>

      <!-- 线索详情弹窗 -->
      <el-dialog v-model="leadDetailVisible" title="线索详情" width="520px" append-to-body>
        <template v-if="currentLead">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="行业">{{ currentLead.industry }}</el-descriptions-item>
            <el-descriptions-item label="地域">{{ currentLead.region }}</el-descriptions-item>
            <el-descriptions-item label="细分领域">{{ currentLead.field || '-' }}</el-descriptions-item>
            <el-descriptions-item label="问题场景">{{ currentLead.scenario || '-' }}</el-descriptions-item>
            <el-descriptions-item label="联系人">{{ currentLead.contact }}</el-descriptions-item>
            <el-descriptions-item label="联系方式">{{ currentLead.phone }}</el-descriptions-item>
            <el-descriptions-item label="意向分">
              <el-tag :type="currentLead.intent >= 90 ? 'danger' : currentLead.intent >= 80 ? 'warning' : 'info'" size="small">{{ currentLead.intent }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="currentLead.status === '已领取' ? 'success' : 'primary'" size="small">{{ currentLead.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="抓取时间" :span="2">{{ currentLead.created_at }}</el-descriptions-item>
            <el-descriptions-item label="客户需求" :span="2">{{ currentLead.need }}</el-descriptions-item>
            <el-descriptions-item label="标签" :span="2">
              <el-tag v-for="t in (currentLead.tags || [])" :key="t" size="small" type="info" effect="plain" class="mr4">{{ t }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </template>
        <template #footer>
          <el-button @click="leadDetailVisible = false">关闭</el-button>
          <el-button type="primary" plain :disabled="currentLead && currentLead.status !== '待跟进'" @click="claimLead(currentLead); leadDetailVisible = false">
            领取此线索
          </el-button>
        </template>
      </el-dialog>

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
import { ref, reactive, computed, onMounted } from 'vue'
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


const applying = ref(false)


// 客户线索（13 行业 drill-down）
const leads = ref([])
const leadsLoading = ref(false)
const leadIndustry = ref('')
const leadRegion = ref('')
const leadField = ref('')
const leadScenario = ref('')
const leadIntent = ref(null)
const leadFields = ref([])
const leadScenarios = ref([])
const leadHint = ref('')
const claimedLeads = ref([])
const selectedLeads = ref([])
const leadPage = ref(1)
const leadPageSize = ref(10)
const leadDetailVisible = ref(false)
const currentLead = ref(null)
const pagedLeads = computed(() => {
  const start = (leadPage.value - 1) * leadPageSize.value
  return leads.value.slice(start, start + leadPageSize.value)
})

// 根据行业加载细分领域（drill-down）
const loadLeadTree = async () => {
  leadField.value = ''
  leadScenario.value = ''
  leadFields.value = []
  leadScenarios.value = []
  leadHint.value = ''
  if (!leadIndustry.value) { loadLeads(); return }
  try {
    const data = await api.get('/misc/industry-tree', { params: { industry: leadIndustry.value } })
    const tree = data.results.tree || {}
    const fields = []
    Object.keys(tree).forEach(main => {
      Object.keys(tree[main].fields || {}).forEach(f => { if (!fields.includes(f)) fields.push(f) })
    })
    leadFields.value = fields
    leadHint.value = leadIndustry.value === '法律行业'
      ? '法律行业深度导航：' + fields.length + ' 个细分领域可选，点选领域后可继续选择问题场景'
      : '已加载「' + leadIndustry.value + '」行业词库领域，可进一步筛选'
  } catch (e) {
    leadFields.value = []
  }
}

const onLeadFieldChange = async () => {
  leadScenario.value = ''
  leadScenarios.value = []
  if (!leadIndustry.value || !leadField.value) { loadLeads(); return }
  try {
    const data = await api.get('/misc/industry-tree', { params: { industry: leadIndustry.value } })
    const tree = data.results.tree || {}
    const scenarios = []
    Object.keys(tree).forEach(main => {
      const f = (tree[main].fields || {})[leadField.value]
      if (f) Object.keys(f.scenarios || {}).forEach(s => { if (!scenarios.includes(s)) scenarios.push(s) })
    })
    leadScenarios.value = scenarios
  } catch (e) {
    leadScenarios.value = []
  }
  loadLeads()
}

const loadLeads = async () => {
  leadsLoading.value = true
  try {
    const params = {}
    if (leadIndustry.value) params.industry = leadIndustry.value
    if (leadRegion.value) params.region = leadRegion.value
    if (leadField.value) params.field = leadField.value
    if (leadScenario.value) params.scenario = leadScenario.value
    if (leadIntent.value) params.intent = leadIntent.value
    const data = await api.get('/misc/industry-leads', { params })
    leads.value = data.results || []
    leadPage.value = 1
  } finally {
    leadsLoading.value = false
  }
}

const resetLeads = () => {
  leadIndustry.value = ''
  leadRegion.value = ''
  leadField.value = ''
  leadScenario.value = ''
  leadIntent.value = null
  leadFields.value = []
  leadScenarios.value = []
  loadLeads()
}

const claimLead = async row => {
  if (claimedLeads.value.includes(row.id)) {
    ElMessage.warning('该线索已领取')
    return
  }
  claimedLeads.value.push(row.id)
  row.status = '已领取'
  ElMessage.success('领取成功！线索已加入线索库')
}

const openLeadDetail = row => {
  currentLead.value = row
  leadDetailVisible.value = true
}

const onLeadSelect = rows => {
  selectedLeads.value = rows
}

const batchClaim = () => {
  if (!selectedLeads.value.length) {
    ElMessage.warning('请先勾选线索')
    return
  }
  let n = 0
  selectedLeads.value.forEach(row => {
    if (!claimedLeads.value.includes(row.id) && row.status === '待跟进') {
      claimedLeads.value.push(row.id)
      row.status = '已领取'
      n++
    }
  })
  if (n) ElMessage.success('批量领取成功，共 ' + n + ' 条')
  else ElMessage.warning('所选线索均已领取')
}

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
  loadLeads()
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

.lead-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 14px 0 10px;
  padding-left: 10px;
  border-left: 3px solid #409EFF;
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
