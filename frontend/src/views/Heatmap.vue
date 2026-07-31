<template>
  <div>
    <div class="page-card">
      <div class="page-title">客户地域分布 · 热力图</div>
      <el-alert type="info" :closable="false" class="mb16"
        title="需要高德地图 JS API Key 才能加载地图。未配置时显示聚合表格，已配置时展示全国热力图与点位标注。" />
      <div class="flex" style="gap: 8px; margin-bottom: 16px">
        <el-input v-model="amapKey" placeholder="输入高德地图 Key（web端 JS API）" style="width: 360px">
          <template #append>
            <el-button @click="initMap">加载地图</el-button>
          </template>
        </el-input>
        <el-button @click="loadData">刷新数据</el-button>
      </div>

      <div v-if="mapReady" ref="mapContainer" style="height: 560px; border-radius: 8px"></div>

      <el-table v-else :data="points" v-loading="loading" stripe>
        <el-table-column prop="city" label="城市" min-width="120" />
        <el-table-column prop="lng" label="经度" width="120" />
        <el-table-column prop="lat" label="纬度" width="120" />
        <el-table-column label="线索数" width="120">
          <template #default="{ row }"><el-tag type="danger">{{ row.count }}</el-tag></template>
        </el-table-column>
        <el-table-column label="占比" min-width="180">
          <template #default="{ row }">
            <el-progress :percentage="Math.round(row.count / maxCount * 100)" :stroke-width="10" />
          </template>
        </el-table-column>
        <el-table-column v-if="!points.length" label="提示">
          <template #default>暂无带地域的线索数据，先运行采集任务获取客户线索</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const points = ref([])
const loading = ref(false)
const maxCount = ref(1)
const amapKey = ref(localStorage.getItem('amap_key') || '')
const mapReady = ref(false)
const mapContainer = ref(null)
let map = null
let heatmap = null

const loadData = async () => {
  loading.value = true
  try {
    const data = await api.get('/stats/heatmap')
    points.value = data.results
    maxCount.value = Math.max(...points.value.map(p => p.count), 1)
    if (mapReady.value && map) {
      renderMap()
    }
  } finally {
    loading.value = false
  }
}

const renderMap = () => {
  if (!map || !window.AMap) return
  map.clearMap()
  const data = points.value.map(p => [p.lng, p.lat, p.count])
  if (data.length) {
    heatmap = new window.AMap.Heatmap(map, {
      radius: 25,
      opacity: [0, 0.8],
      gradient: { 0.4: 'rgb(0,255,255)', 0.65: 'rgb(0,255,0)', 0.85: 'yellow', 1: 'rgb(255,0,0)' }
    })
    heatmap.setDataSet({ data, max: maxCount.value })
    // 视野自适应
    const lngs = points.value.map(p => p.lng)
    const lats = points.value.map(p => p.lat)
    map.setFitView(null, false, [80, 80, 80, 80])
    map.setZoomAndCenter(5, [ (Math.min(...lngs) + Math.max(...lngs)) / 2, (Math.min(...lats) + Math.max(...lats)) / 2 ])
  }
  // 点位标注
  points.value.forEach(p => {
    const marker = new window.AMap.Marker({
      position: [p.lng, p.lat],
      content: `<div style="background:#F56C6C;color:#fff;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;box-shadow:0 2px 8px rgba(245,108,108,.5)">${p.count}</div>`
    })
    marker.on('click', () => {
      new window.AMap.InfoWindow({ content: `<b>${p.city}</b><br/>线索数：${p.count}` }).open(map, [p.lng, p.lat])
    })
    map.add(marker)
  })
}

const initMap = () => {
  if (!amapKey.value) return
  localStorage.setItem('amap_key', amapKey.value)
  if (window.AMap) {
    map = new window.AMap.Map(mapContainer.value, { zoom: 5, center: [104, 35] })
    mapReady.value = true
    renderMap()
    return
  }
  const script = document.createElement('script')
  script.src = `https://webapi.amap.com/maps?v=2.0&key=${amapKey.value}&plugin=AMap.Heatmap`
  script.onload = () => {
    map = new window.AMap.Map(mapContainer.value, { zoom: 5, center: [104, 35] })
    mapReady.value = true
    renderMap()
  }
  document.head.appendChild(script)
}

onMounted(() => {
  loadData()
  if (amapKey.value) initMap()
})
</script>

<style scoped>
.mb16 { margin-bottom: 16px; }
</style>
