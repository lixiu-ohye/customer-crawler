<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="6" v-for="card in cards" :key="card.label">
        <div class="stat-card page-card">
          <div class="stat-icon" :style="{ background: card.bg }">
            <el-icon :size="26" color="#fff"><component :is="card.icon" /></el-icon>
          </div>
          <div>
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt16">
      <el-col :span="12">
        <div class="page-card">
          <div class="page-title">平台线索分布</div>
          <div ref="platformChart" style="height: 320px"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="page-card">
          <div class="page-title">意向等级分布</div>
          <div ref="intentChart" style="height: 320px"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt16">
      <el-col :span="16">
        <div class="page-card">
          <div class="flex-between mb16">
            <div class="page-title" style="margin-bottom: 0">近 7 日线索增长趋势</div>
            <el-button size="small" @click="loadDashboard">刷新</el-button>
          </div>
          <div ref="trendChart" style="height: 300px"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="page-card">
          <div class="page-title">任务状态</div>
          <div ref="taskChart" style="height: 300px"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '../api'
import { Odometer, User, Aim, VideoPlay } from '@element-plus/icons-vue'

const cards = reactive([
  { label: '累计线索', value: 0, icon: User, bg: '#409EFF' },
  { label: '高意向客户', value: 0, icon: Aim, bg: '#F56C6C' },
  { label: '平均意向分', value: 0, icon: Odometer, bg: '#E6A23C' },
  { label: '运行中任务', value: 0, icon: VideoPlay, bg: '#67C23A' }
])

const platformChart = ref(null)
const intentChart = ref(null)
const trendChart = ref(null)
const taskChart = ref(null)
let charts = []

const render = (el, option) => {
  if (!el) { console.warn('[dashboard] chart el is null, skip render'); return }
  try {
    if (typeof echarts.init !== 'function') {
      console.error('[dashboard] echarts.init is NOT a function, echarts keys:', Object.keys(echarts).slice(0, 20).join(','))
      return
    }
    const chart = echarts.init(el)
    charts.push(chart)
    chart.setOption(option)
    console.log('[dashboard] chart rendered OK, size:', el.clientWidth, 'x', el.clientHeight)
  } catch (e) {
    console.error('[dashboard] echarts render failed:', e.message, e.stack)
  }
}

const loadDashboard = async () => {
  console.log('[dashboard] loadDashboard start')
  const [dash, dist, trend, taskDist, intent] = await Promise.all([
    api.get('/stats/dashboard'),
    api.get('/stats/distribution', { params: { kind: 'platform' } }),
    api.get('/stats/trend', { params: { days: 7 } }),
    api.get('/stats/distribution', { params: { kind: 'task_status' } }),
    api.get('/stats/distribution', { params: { kind: 'intent' } })
  ])
  console.log('[dashboard] api data ok, intent:', JSON.stringify(intent).slice(0, 200))
  const d = dash.result
  cards[0].value = d.total_leads
  cards[1].value = d.high_intent_leads
  cards[2].value = d.avg_intent_score
  cards[3].value = d.running_tasks

  charts.forEach(c => c.dispose())
  charts = []
  nextTick(() => {
    render(platformChart.value, {
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['40%', '65%'],
        data: dist.results.length ? dist.results : [{ name: '暂无数据', value: 1 }],
        label: { formatter: '{b}: {c}' }
      }]
    })
    render(intentChart.value, {
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['40%', '65%'],
        data: intent.results.length ? intent.results : [{ name: '暂无数据', value: 1 }],
        label: { formatter: '{b}: {c}' }
      }]
    })
    render(trendChart.value, {
      tooltip: { trigger: 'axis' },
      grid: { left: 40, right: 20, top: 30, bottom: 30 },
      xAxis: { type: 'category', data: trend.results.map(t => t.date) },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.15 },
        data: trend.results.map(t => t.value),
        itemStyle: { color: '#409EFF' }
      }]
    })
    render(taskChart.value, {
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['40%', '65%'],
        data: taskDist.results.length ? taskDist.results : [{ name: '暂无任务', value: 1 }],
        label: { formatter: '{b}: {c}' }
      }]
    })
  })
}

onMounted(loadDashboard)
onBeforeUnmount(() => charts.forEach(c => c.dispose()))
</script>

<style scoped>
.stat-card { display: flex; align-items: center; gap: 16px; }
.stat-icon { width: 52px; height: 52px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.stat-value { font-size: 24px; font-weight: 700; color: #303133; }
.stat-label { font-size: 13px; color: #909399; margin-top: 2px; }
</style>
