import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '数据大盘' } },
      { path: 'keywords', name: 'Keywords', component: () => import('../views/Keywords.vue'), meta: { title: '关键词管理' } },
      { path: 'tasks', name: 'Tasks', component: () => import('../views/Tasks.vue'), meta: { title: '任务中心' } },
      { path: 'leads', name: 'Leads', component: () => import('../views/Leads.vue'), meta: { title: '线索库' } },
      { path: 'heatmap', name: 'Heatmap', component: () => import('../views/Heatmap.vue'), meta: { title: '地域热力导航' } },
      { path: 'analysis', name: 'AIAnalysis', component: () => import('../views/AIAnalysis.vue'), meta: { title: 'AI 分析' } },
      { path: 'member', name: 'MemberCenter', component: () => import('../views/MemberCenter.vue'), meta: { title: '会员中心' } },
      { path: 'system', name: 'SystemAdmin', component: () => import('../views/SystemAdmin.vue'), meta: { title: '系统管理' } },
      { path: 'disclaimer', name: 'Disclaimer', component: () => import('../views/Disclaimer.vue'), meta: { title: '合规声明' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
