<template>
  <div class="official-api">
    <el-card shadow="never" class="mb16">
      <div class="card-header">
        <div>
          <h3 class="title">官方开放 API 合规采集</h3>
          <p class="desc">仅使用各平台官方开放 API / 公开接口采集公开信息，不采集手机号/微信号/私信/真实姓名等个人敏感信息</p>
        </div>
        <el-tag type="success" effect="dark">合规模式</el-tag>
      </div>
      <div class="compliance-tags">
        <el-tag size="small" type="info">不自动私信</el-tag>
        <el-tag size="small" type="info">不批量评论</el-tag>
        <el-tag size="small" type="info">不破解风控</el-tag>
        <el-tag size="small" type="warning">数据 30 天自动清理</el-tag>
        <el-tag size="small" type="danger">全程留痕审计</el-tag>
      </div>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="10">
        <el-card shadow="never" class="mb16">
          <template #header>
            <span>采集参数</span>
          </template>
          <el-form label-width="80px">
            <el-form-item label="平台">
              <el-select v-model="form.platform" style="width: 100%">
                <el-option v-for="p in platforms" :key="p.platform" :label="p.name + (p.mode === 'demo' ? ' (演示)' : '')" :value="p.platform" />
              </el-select>
            </el-form-item>
            <el-form-item label="关键词">
              <el-input v-model="form.keyword" placeholder="如：装修、法律咨询、全屋定制" clearable />
            </el-form-item>
            <el-form-item label="数量">
              <el-input-number v-model="form.limit" :min="1" :max="50" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="doSearch">
                <el-icon style="margin-right: 4px"><Search /></el-icon>开始采集
              </el-button>
              <el-button @click="doBatch">批量多平台</el-button>
            </el-form-item>
          </el-form>
          <el-alert type="info" :closable="false" class="mt8">
            <template #title>
              <template v-if="currentPlatformConfigured">
                当前平台已配置官方凭证，将以<strong>官方 API 模式</strong>采集（<el-tag size="small" type="success">official_api</el-tag>）
              </template>
              <template v-else>
                当前为<strong>演示模式</strong>（demo），未配置平台官方 API 凭证。接入真实凭证后自动切换为官方接口采集。
              </template>
            </template>
          </el-alert>
        </el-card>

        <el-card shadow="never" class="mb16">
          <template #header>
            <div class="card-header">
              <span>平台凭证配置</span>
              <el-tag v-if="credSaving" size="small" type="warning">保存中…</el-tag>
            </div>
          </template>
          <el-table :data="platforms" size="small">
            <el-table-column label="平台" width="90">
              <template #default="{ row }">
                {{ row.name }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag size="small" :type="row.is_configured ? 'success' : 'info'">
                  {{ row.is_configured ? '官方API' : '演示' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="凭证">
              <template #default="{ row }">
                <el-input
                  v-if="credForm.platform === row.platform"
                  v-model="credForm.token"
                  size="small"
                  placeholder="粘贴 App Key / Token"
                  clearable
                />
                <span v-else class="cred-hint">{{ row.cred_hint || '未配置' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140" align="right">
              <template #default="{ row }">
                <el-button v-if="credForm.platform !== row.platform" size="small" text type="primary" @click="startCredEdit(row)">
                  配置
                </el-button>
                <template v-else>
                  <el-button size="small" type="primary" @click="saveCred(row)">保存</el-button>
                  <el-button size="small" text @click="credForm.platform = ''">取消</el-button>
                </template>
                <el-button
                  v-if="row.is_configured && credForm.platform !== row.platform"
                  size="small"
                  text
                  type="danger"
                  @click="clearCred(row)"
                >清除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card shadow="never">
          <template #header>
            <span>审计日志（留痕）</span>
          </template>
          <el-table :data="auditLogs" size="small" max-height="260">
            <el-table-column prop="ts" label="时间" width="150" />
            <el-table-column prop="platform_name" label="平台" width="80" />
            <el-table-column prop="keyword" label="关键词" />
            <el-table-column prop="result_count" label="条数" width="60" align="center" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>采集结果（公开信息）</span>
              <el-tag v-if="searchInfo.mode" size="small" type="success">{{ searchInfo.mode }} 模式</el-tag>
            </div>
          </template>
          <el-empty v-if="!results.length && !loading" description="输入关键词开始采集" />
          <div v-loading="loading">
            <el-table v-if="results.length" :data="results" size="small">
              <el-table-column prop="platform_name" label="平台" width="90">
                <template #default="{ row }">
                  <el-tag size="small" effect="plain">{{ row.platform_name }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="title" label="标题 / 内容" min-width="200" show-overflow-tooltip />
              <el-table-column prop="author.nickname" label="作者" width="100" show-overflow-tooltip />
              <el-table-column prop="region" label="地区" width="70" />
              <el-table-column prop="like_count" label="点赞" width="70" align="center" />
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import api from '../api'

const platforms = ref([])
const results = ref([])
const auditLogs = ref([])
const loading = ref(false)
const searchInfo = reactive({ mode: '' })
const credForm = reactive({ platform: '', token: '' })
const credSaving = ref(false)

const currentPlatformConfigured = computed(() => {
  const p = platforms.value.find(x => x.platform === form.platform)
  return !!(p && p.is_configured)
})

const form = reactive({
  platform: 'douyin',
  keyword: '装修公司',
  limit: 5
})

const loadPlatforms = async () => {
  const res = await api.get('/crawler/official/platforms')
  platforms.value = res.results || []
  if (platforms.value.length) form.platform = platforms.value[0].platform
  loadCredStatus()
}

const loadCredStatus = async () => {
  try {
    const res = await api.get('/crawler/official/credentials')
    const status = res.results || {}
    platforms.value = (platforms.value || []).map(p => {
      const st = status[p.platform] || {}
      return {
        ...p,
        is_configured: !!st.source && st.source !== 'none',
        cred_hint: st.source === 'redis' ? '已配置 (热生效)' : (st.source === 'settings/env' ? 'settings 配置' : '')
      }
    })
  } catch (e) {
    // 凭证接口不可用时静默 (演示环境)
  }
}

const startCredEdit = (row) => {
  credForm.platform = row.platform
  credForm.token = ''
}

const saveCred = async (row) => {
  if (!credForm.token.trim()) return ElMessage.warning('请输入凭证')
  credSaving.value = true
  try {
    const key = row.platform === 'douyin' ? 'client_key' : (row.platform === 'xiaohongshu' ? 'app_id' : (row.platform === 'kuaishou' ? 'app_key' : 'token'))
    const secretKey = row.platform === 'douyin' ? 'client_secret' : (row.platform === 'xiaohongshu' || row.platform === 'kuaishou' ? 'app_secret' : null)
    const credentials = { [key]: credForm.token.trim() }
    if (secretKey) credentials[secretKey] = 'configured_via_ui'
    const res = await api.post('/crawler/official/credentials', {
      platform: row.platform,
      credentials
    })
    if (res.ok) {
      ElMessage.success(`「${row.name}」已切换为官方 API 模式`)
      credForm.platform = ''
      loadPlatforms()
    } else {
      ElMessage.error(res.detail || '保存失败')
    }
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    credSaving.value = false
  }
}

const clearCred = async (row) => {
  try {
    const res = await api.delete('/crawler/official/credentials', {
      params: { platform: row.platform }
    })
    if (res.ok) {
      ElMessage.success(`「${row.name}」已清除凭证，回退演示模式`)
      loadPlatforms()
    }
  } catch (e) {
    ElMessage.error(e.message || '清除失败')
  }
}

const loadAudit = async () => {
  const res = await api.get('/crawler/official/audit')
  auditLogs.value = (res.results || []).map(l => ({
    ...l,
    platform_name: ({ douyin: '抖音', xiaohongshu: '小红书', kuaishou: '快手', weibo: '微博', zhihu: '知乎', tieba: '贴吧' })[l.platform] || l.platform
  }))
}

const doSearch = async () => {
  if (!form.keyword.trim()) return ElMessage.warning('请输入关键词')
  loading.value = true
  try {
    const res = await api.get('/crawler/official/search', {
      params: { platform: form.platform, keyword: form.keyword.trim(), limit: form.limit }
    })
    results.value = res.results || []
    searchInfo.mode = res.mode || ''
    ElMessage.success(`采集完成，共 ${results.value.length} 条公开线索`)
    loadAudit()
  } catch (e) {
    ElMessage.error(e.message || '采集失败')
  } finally {
    loading.value = false
  }
}

const doBatch = async () => {
  if (!form.keyword.trim()) return ElMessage.warning('请输入关键词')
  loading.value = true
  try {
    const platformsToSearch = platforms.value.slice(0, 6)
    const res = await api.post('/crawler/official/search', {
      searches: platformsToSearch.map(p => ({ platform: p.platform, keyword: form.keyword.trim(), limit: 3 }))
    })
    const all = (res.results || []).flatMap(item => item.results || [])
    results.value = all
    searchInfo.mode = 'batch'
    ElMessage.success(`批量采集完成，共 ${all.length} 条公开线索`)
    loadAudit()
  } catch (e) {
    ElMessage.error(e.message || '批量采集失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPlatforms()
  loadAudit()
})
</script>

<style scoped>
.official-api { min-height: calc(100vh - 140px); }
.mb16 { margin-bottom: 16px; }
.mt8 { margin-top: 8px; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.title { margin: 0; font-size: 16px; font-weight: 600; }
.desc { margin: 4px 0 0; font-size: 12px; color: #909399; }
.compliance-tags { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
.cred-hint { font-size: 12px; color: #909399; }
</style>
