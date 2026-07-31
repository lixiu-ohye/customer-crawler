<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="login-title">客户大数据智能获客平台</h2>
      <el-tabs v-model="tab" class="mt16">
        <el-tab-pane label="登录" name="login">
          <el-form :model="form" @keyup.enter="submit">
            <el-form-item>
              <el-input v-model="form.username" placeholder="用户名" size="large" :prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password :prefix-icon="Lock" />
            </el-form-item>
            <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="submit">登 录</el-button>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form :model="form" @keyup.enter="submit">
            <el-form-item>
              <el-input v-model="form.username" placeholder="用户名" size="large" :prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.email" placeholder="邮箱（可选）" size="large" :prefix-icon="Message" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.password" type="password" placeholder="密码（至少6位）" size="large" show-password :prefix-icon="Lock" />
            </el-form-item>
            <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="submit">注 册</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <div class="tip">演示账号：admin / admin123456</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const tab = ref('login')
const loading = ref(false)
const form = reactive({ username: '', password: '', email: '' })

const submit = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    if (tab.value === 'login') {
      await auth.login(form.username, form.password)
    } else {
      await auth.register(form.username, form.password, form.email)
    }
    ElMessage.success(tab.value === 'login' ? '登录成功' : '注册成功')
    router.push('/dashboard')
  } catch (e) {
    // 拦截器已提示
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1f2d3d 0%, #2b4a6f 50%, #409EFF 100%); }
.login-card { width: 400px; background: #fff; border-radius: 12px; padding: 40px 36px; box-shadow: 0 12px 40px rgba(0,0,0,.25); }
.login-title { text-align: center; font-size: 20px; color: #303133; }
.submit-btn { width: 100%; }
.tip { margin-top: 16px; text-align: center; font-size: 12px; color: #909399; }
</style>
