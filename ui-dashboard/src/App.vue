<template>
  <div id="app-container">
    <header class="app-header">
      <div class="header-logo">合同管理</div>
      <nav class="header-nav">
        <router-link to="/dashboard" class="nav-link">📊 看板</router-link>
        <router-link to="/contracts" class="nav-link">📋 合同</router-link>
        <router-link to="/invoices" class="nav-link">🧾 发票</router-link>
        <router-link to="/suppliers" class="nav-link">🏢 供应商</router-link>
      </nav>
      <div class="header-right">
        <span class="db-status" :class="dbOk ? 'ok' : 'err'">{{ dbOk ? '● 在线' : '○ 离线' }}</span>
      </div>
    </header>
    <main class="app-main"><router-view /></main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getDbSummary } from './api'
const dbOk = ref(false)
onMounted(async () => {
  try { await getDbSummary(); dbOk.value = true } catch { dbOk.value = false }
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif; background: #f0f2f5; color: #1f2937; }
#app-container { min-height: 100vh; display: flex; flex-direction: column; }
.app-header {
  background: #fff; border-bottom: 1px solid #e5e7eb; padding: 0 28px; height: 52px;
  display: flex; align-items: center; gap: 32px; position: sticky; top: 0; z-index: 100;
}
.header-logo { font-size: 16px; font-weight: 700; color: #1e40af; letter-spacing: 0.5px; }
.header-nav { display: flex; gap: 4px; flex: 1; }
.nav-link {
  text-decoration: none; padding: 8px 14px; border-radius: 6px; font-size: 13px;
  color: #4b5563; transition: all 0.15s;
}
.nav-link:hover { background: #f3f4f6; color: #1f2937; }
.nav-link.router-link-active { background: #eff6ff; color: #2563eb; font-weight: 500; }
.header-right { display: flex; align-items: center; }
.db-status { font-size: 12px; padding: 3px 10px; border-radius: 10px; }
.db-status.ok { background: #dcfce7; color: #166534; }
.db-status.err { background: #fee2e2; color: #991b1b; }
.app-main { flex: 1; padding: 20px 28px; max-width: 1440px; margin: 0 auto; width: 100%; }
</style>
