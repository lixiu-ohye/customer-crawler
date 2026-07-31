<template>
  <div class="fb-wrap">
    <!-- 悬浮气泡：全站右下角，永久展示 -->
    <transition name="fb-pop">
      <div v-if="visible" class="fb-bubble" @click="goPromotion" title="推广活动">
        <span class="fb-icon">🎁</span>
        <span class="fb-pulse"></span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const visible = ref(false)

onMounted(() => {
  // 轻微延迟出现，避免首屏遮挡
  setTimeout(() => { visible.value = true }, 800)
})

const goPromotion = () => {
  router.push('/promotion')
}
</script>

<style scoped>
.fb-wrap { position: fixed; right: 20px; bottom: 20px; z-index: 9999; }
.fb-bubble {
  position: relative;
  width: 60px; height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff5722 0%, #ff8a50 100%);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(255, 87, 34, .45);
  transition: transform .2s ease;
  user-select: none;
}
.fb-bubble:hover { transform: scale(1.08); }
.fb-icon { font-size: 26px; line-height: 1; }
.fb-pulse {
  position: absolute; inset: 0;
  border-radius: 50%;
  border: 3px solid rgba(255, 87, 34, .5);
  animation: fbPulse 2s infinite;
  pointer-events: none;
}
@keyframes fbPulse {
  0% { transform: scale(1); opacity: .9; }
  70% { transform: scale(1.5); opacity: 0; }
  100% { transform: scale(1.5); opacity: 0; }
}
.fb-pop-enter-active { transition: all .3s ease; }
.fb-pop-enter-from { transform: translateY(20px); opacity: 0; }
</style>
