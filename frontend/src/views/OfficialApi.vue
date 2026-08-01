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
              当前为<strong>演示模式</strong>（demo），未配置平台官方 API 凭证。接入真实凭证后自动切换为官方接口采集。
            </template>
          </el-alert>
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
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import api from '../api'

const platforms = ref([])
const results = ref([])
const auditLogs = ref([])
const loading = ref(false)
const searchInfo = reactive({ mode: '' })

const form = reactive({
  platform: 'douyin',
  keyword: '装修公司',
  limit: 5
})

const loadPlatforms = async () => {
  const res = await api.get('/crawler/official/platforms')
  platforms.value = res.results || []
  if (platforms.value.length) form.platform = platforms.value[0].platform
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
</style>
