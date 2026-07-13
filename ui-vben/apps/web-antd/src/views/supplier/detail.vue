<template>
  <div class="p-6 space-y-4 bg-gradient-to-b from-gray-50 to-gray-100 min-h-screen">
    <!-- ============ 标题栏 ============ -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <a-button
          type="text"
          class="flex items-center justify-center w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-100"
          @click="goBack"
        >
          <span class="text-lg">&#8592;</span>
        </a-button>
        <div>
          <h2 class="text-xl font-semibold text-gray-800">供应商详情</h2>
          <div class="text-sm text-gray-500 mt-0.5">
            {{ supplierInfo?.企业名称 }} · {{ supplierInfo?.统一社会信用代码 }}
          </div>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a-tag :color="statusColor(supplierInfo?.登记状态)" class="rounded-full px-3 py-0.5 text-xs">
          {{ supplierInfo?.登记状态 || '未知' }}
        </a-tag>
        <a-tag :color="riskLevelColor(riskLevel)" class="rounded-full px-3 py-0.5 text-xs">
          {{ riskLabel }}
        </a-tag>
        <a-button type="primary" size="small" ghost @click="refreshData">
          刷新数据
        </a-button>
      </div>
    </div>

    <!-- 三态：loading / error / 正常内容 -->
    <state-block :loading="loading" :error="error" error-title="供应商数据加载失败" @retry="loadData">
      <!-- ============ KPI 指标行 ============ -->
      <div v-if="supplierInfo" class="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">注册资本</div>
          <div class="text-2xl font-bold text-gray-900">{{ supplierInfo.注册资本 || '-' }}</div>
          <div class="text-xs text-gray-400 mt-0.5">实缴: {{ supplierInfo.实缴资本 || '-' }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">成立年限</div>
          <div class="text-2xl font-bold text-gray-900">{{ companyAge }}</div>
          <div class="text-xs text-gray-400 mt-0.5">{{ supplierInfo.成立日期 }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">参保人数</div>
          <div class="text-2xl font-bold text-blue-600">{{ supplierInfo.参保人数 || 0 }}</div>
          <div class="text-xs text-gray-400 mt-0.5">人员规模</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">软件著作权</div>
          <div class="text-2xl font-bold text-green-600">{{ softwareCount }}</div>
          <div class="text-xs text-gray-400 mt-0.5">技术实力</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">对外投资</div>
          <div class="text-2xl font-bold text-purple-600">{{ investmentCount }}</div>
          <div class="text-xs text-gray-400 mt-0.5">家企业</div>
        </div>
      </div>

      <!-- ============ 吸顶锚点条 ============ -->
      <div v-if="supplierInfo" class="sticky top-0 z-20 bg-white/85 backdrop-blur-sm border-y border-gray-200 -mx-6 px-6">
        <div class="flex gap-1 py-2 overflow-x-auto">
          <button
            v-for="a in anchors"
            :key="a.id"
            @click="scrollToAnchor(a.id)"
            :class="['px-3 py-1.5 text-sm rounded-md whitespace-nowrap transition-colors',
                     activeAnchor === a.id ? 'bg-blue-50 text-blue-600 font-medium' : 'text-gray-500 hover:bg-gray-100']"
          >
            {{ a.label }}
          </button>
        </div>
      </div>

      <!-- ============ 第1行：基本信息 + 风险扫描 ============ -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <!-- 基本信息卡片（占 8/12） -->
        <a-card
          title="工商信息"
          id="overview"
          class="lg:col-span-8 rounded-lg"
          size="small"
          :body-style="{ padding: '16px' }"
        >
          <div v-if="supplierInfo" class="space-y-5">
            <!-- 企业标识 -->
            <div>
              <div class="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wider">企业标识</div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div class="text-xs text-gray-400 mb-1">企业名称</div>
                  <div class="font-medium text-gray-900">{{ supplierInfo.企业名称 }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-400 mb-1">统一社会信用代码</div>
                  <div class="font-medium text-gray-900 text-xs">{{ supplierInfo.统一社会信用代码 }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-400 mb-1">法定代表人</div>
                  <div class="font-medium text-gray-900">{{ supplierInfo.法定代表人 }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-400 mb-1">企业类型</div>
                  <div class="font-medium text-gray-900 text-xs">{{ supplierInfo.企业类型 }}</div>
                </div>
              </div>
            </div>

            <a-divider class="my-0" />

            <!-- 注册信息 -->
            <div>
              <div class="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wider">注册信息</div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div class="text-xs text-gray-400 mb-1">成立日期</div>
                  <div class="font-medium text-gray-900">{{ supplierInfo.成立日期 }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-400 mb-1">营业期限</div>
                  <div class="font-medium text-gray-900 text-xs">{{ supplierInfo.营业期限 }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-400 mb-1">登记机关</div>
                  <div class="font-medium text-gray-900 text-xs">{{ supplierInfo.登记机关 }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-400 mb-1">纳税人资质</div>
                  <div class="font-medium text-gray-900">{{ supplierInfo.纳税人资质 }}</div>
                </div>
              </div>
            </div>

            <a-divider class="my-0" />

            <!-- 企业简介 -->
            <div v-if="profile">
              <div class="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wider">企业简介</div>
              <div class="text-sm text-gray-700 leading-relaxed bg-gray-50 rounded-lg p-3">
                {{ profile.简介 }}
              </div>
              <div class="text-xs text-gray-400 mt-2">
                企查查行业: {{ profile.企查查行业 }}
              </div>
            </div>

            <!-- 注册地址 -->
            <div>
              <div class="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wider">注册地址</div>
              <div class="text-sm text-gray-700">
                📍 {{ supplierInfo.注册地址 }}
              </div>
            </div>

            <!-- 经营范围 -->
            <div>
              <div class="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wider">经营范围</div>
              <div class="text-xs text-gray-600 leading-relaxed max-h-32 overflow-y-auto bg-gray-50 rounded-lg p-3">
                {{ supplierInfo.经营范围 }}
              </div>
            </div>
          </div>
        </a-card>

        <!-- 风险扫描卡片（占 4/12） -->
        <a-card
          title="风险扫描"
          id="risk"
          class="lg:col-span-4 rounded-xl shadow-sm"
          size="small"
          :body-style="{ padding: '12px' }"
        >
          <template v-if="riskScan">
            <!-- 风险等级 -->
            <div class="text-center mb-4">
              <div class="text-xs text-gray-400 mb-2">风险评级</div>
              <div class="text-3xl font-bold mb-1" :class="riskLevelTextClass">
                {{ riskLabel }}
              </div>
              <div class="text-xs text-gray-500">
                扫描 {{ riskScan.有记录因子数 + riskScan.无记录因子数 }} 项风险因子
              </div>
            </div>

            <!-- 风险统计 -->
            <div class="grid grid-cols-2 gap-3 mb-4">
              <div class="bg-red-50 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold text-red-600">{{ riskScan.有记录因子数 }}</div>
                <div class="text-xs text-gray-500 mt-1">有风险</div>
              </div>
              <div class="bg-green-50 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold text-green-600">{{ riskScan.无记录因子数 }}</div>
                <div class="text-xs text-gray-500 mt-1">无风险</div>
              </div>
            </div>

            <!-- 主要风险因子 -->
            <div v-if="riskFactors.length" class="space-y-2">
              <div class="text-xs font-semibold text-gray-500 mb-2">风险因子详情</div>
              <div
                v-for="factor in riskFactors.slice(0, 5)"
                :key="factor.风险因子"
                class="flex items-center justify-between py-2 px-3 rounded-lg"
                :class="factor.条目数 > 0 ? 'bg-red-50' : 'bg-gray-50'"
              >
                <span class="text-xs text-gray-700">{{ factor.风险因子 }}</span>
                <a-tag :color="factor.条目数 > 0 ? 'red' : 'green'" size="small">
                  {{ factor.条目数 }}条
                </a-tag>
              </div>
            </div>

            <!-- 无风险提示 -->
            <div v-else class="text-center py-8">
              <div class="text-5xl mb-2">✅</div>
              <div class="text-sm text-gray-600">暂无任何风险记录</div>
            </div>
          </template>
        </a-card>
      </div>

      <!-- ============ 第2行：软件著作权 + 对外投资 ============ -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- 软件著作权 -->
        <a-card title="软件著作权" id="ipr" size="small" class="rounded-xl shadow-sm" :body-style="{ padding: '12px' }">
          <template #extra>
            <span class="text-xs text-gray-400">共 {{ softwareCount }} 项</span>
          </template>
          <template v-if="softwareList.length">
            <div class="space-y-2 max-h-[400px] overflow-y-auto">
              <div
                v-for="(sw, idx) in softwareList.slice(0, 10)"
                :key="idx"
                class="flex items-center justify-between p-2.5 bg-gray-50 rounded-lg hover:bg-blue-50/50"
              >
                <div class="flex items-center gap-3 min-w-0">
                  <div class="w-7 h-7 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold shrink-0">
                    {{ idx + 1 }}
                  </div>
                  <div class="min-w-0">
                    <div class="font-medium text-sm truncate">{{ sw.软件全称 }}</div>
                    <div class="text-xs text-gray-400">
                      {{ sw.登记号 }} · {{ sw.登记日期 }}
                    </div>
                  </div>
                </div>
                <a-tag v-if="sw.权利取得方式" color="blue" size="small">
                  {{ sw.权利取得方式 }}
                </a-tag>
              </div>
            </div>
            <div v-if="softwareCount > 10" class="text-center mt-3">
              <a-button type="link" size="small">查看全部 {{ softwareCount }} 项</a-button>
            </div>
          </template>
          <div v-else class="py-8 text-center">
            <a-empty description="暂无软件著作权记录" />
          </div>
        </a-card>

        <!-- 对外投资 -->
        <a-card title="对外投资" id="investment" size="small" class="rounded-xl shadow-sm" :body-style="{ padding: '12px' }">
          <template #extra>
            <span class="text-xs text-gray-400">共 {{ investmentCount }} 家企业</span>
          </template>
          <template v-if="investmentList.length">
            <div class="space-y-2">
              <div
                v-for="inv in investmentList"
                :key="inv.被投资企业名称"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-purple-50/50"
              >
                <div class="min-w-0 flex-1">
                  <div class="font-medium text-sm text-gray-900">{{ inv.被投资企业名称 }}</div>
                  <div class="text-xs text-gray-400 mt-1 flex items-center gap-2">
                    <span>成立: {{ inv.成立日期 }}</span>
                    <a-tag :color="inv.状态 === '存续' ? 'green' : 'default'" size="small">
                      {{ inv.状态 }}
                    </a-tag>
                  </div>
                </div>
                <div class="text-right shrink-0 ml-4">
                  <div class="font-semibold text-sm text-purple-600">{{ inv.持股比例 }}</div>
                  <div class="text-xs text-gray-400">{{ inv['认缴出资额/持股数'] }}</div>
                </div>
              </div>
            </div>
          </template>
          <div v-else class="py-8 text-center">
            <a-empty description="暂无对外投资记录" />
          </div>
        </a-card>
      </div>

      <!-- ============ 综合评级 ============ -->
      <a-card title="综合评级" size="small" class="rounded-xl shadow-sm" :body-style="{ padding: '16px' }">
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div class="text-center">
            <div class="text-xs text-gray-400 mb-2">基本资质</div>
            <div class="flex justify-center mb-2">
              <a-rate :value="rating.basic" disabled :count="5" allow-half />
            </div>
            <div class="text-xs text-gray-600">{{ ratingLabels.basic }}</div>
          </div>
          <div class="text-center">
            <div class="text-xs text-gray-400 mb-2">风险状况</div>
            <div class="flex justify-center mb-2">
              <a-rate :value="rating.risk" disabled :count="5" allow-half />
            </div>
            <div class="text-xs text-gray-600">{{ ratingLabels.risk }}</div>
          </div>
          <div class="text-center">
            <div class="text-xs text-gray-400 mb-2">技术实力</div>
            <div class="flex justify-center mb-2">
              <a-rate :value="rating.tech" disabled :count="5" allow-half />
            </div>
            <div class="text-xs text-gray-600">{{ ratingLabels.tech }}</div>
          </div>
          <div class="text-center">
            <div class="text-xs text-gray-400 mb-2">经营稳定性</div>
            <div class="flex justify-center mb-2">
              <a-rate :value="rating.stability" disabled :count="5" allow-half />
            </div>
            <div class="text-xs text-gray-600">{{ ratingLabels.stability }}</div>
          </div>
          <div class="text-center bg-blue-50 rounded-lg p-3">
            <div class="text-xs text-gray-400 mb-2">综合评分</div>
            <div class="text-3xl font-bold text-blue-600 mb-2">{{ rating.overall }}</div>
            <a-tag color="blue">{{ ratingLabels.overall }}</a-tag>
          </div>
        </div>
      </a-card>
    </state-block>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import StateBlock from '#/components/state-block/index.vue'
import { getSupplierQccInfoApi } from '#/api/suppliers'

const route = useRoute()
const router = useRouter()

// 数据状态
const loading = ref(true)
const error = ref('')
const supplierInfo = ref<any>(null)
const profile = ref<any>(null)
const riskScan = ref<any>(null)
const softwareList = ref<any[]>([])
const investmentList = ref<any[]>([])

// 吸顶锚点
const anchors = computed(() => [
  { id: 'overview', label: '基本信息' },
  { id: 'risk', label: '风险扫描' },
  { id: 'ipr', label: '知识产权' },
  { id: 'investment', label: '对外投资' },
])
const activeAnchor = ref('overview')

// 计算属性
const companyAge = computed(() => {
  if (!supplierInfo.value?.成立日期) return '-'
  const setupDate = new Date(supplierInfo.value.成立日期)
  const now = new Date()
  const years = Math.floor((now.getTime() - setupDate.getTime()) / (365.25 * 24 * 60 * 60 * 1000))
  return `${years}年`
})

const softwareCount = computed(() => softwareList.value.length)
const investmentCount = computed(() => investmentList.value.length)

const riskFactors = computed(() => {
  if (!riskScan.value?.风险因子扫描) return []
  return riskScan.value.风险因子扫描.filter((f: any) => f.条目数 > 0)
})

const riskLevel = computed(() => {
  if (!riskScan.value) return 'unknown'
  const hasRisk = riskScan.value.有记录因子数 || 0
  if (hasRisk === 0) return 'excellent'
  if (hasRisk <= 2) return 'good'
  if (hasRisk <= 5) return 'medium'
  return 'high'
})

const riskLabel = computed(() => {
  const labels: Record<string, string> = {
    excellent: '优秀',
    good: '良好',
    medium: '中等',
    high: '高风险',
    unknown: '未知'
  }
  return labels[riskLevel.value] || '未知'
})

const riskLevelTextClass = computed(() => {
  const classes: Record<string, string> = {
    excellent: 'text-green-600',
    good: 'text-blue-600',
    medium: 'text-orange-600',
    high: 'text-red-600',
    unknown: 'text-gray-600'
  }
  return classes[riskLevel.value] || 'text-gray-600'
})

// 综合评级
const rating = computed(() => {
  if (!supplierInfo.value) return { basic: 3, risk: 3, tech: 3, stability: 3, overall: 3.0 }

  // 基本资质评分
  let basic = 3
  if (supplierInfo.value.实缴资本 && supplierInfo.value.实缴资本 !== '-') basic += 1
  if (supplierInfo.value.参保人数 && parseInt(supplierInfo.value.参保人数) > 30) basic += 0.5

  // 风险状况评分
  let risk = 5
  const riskCount = riskScan.value?.有记录因子数 || 0
  if (riskCount > 0) risk = Math.max(1, 5 - riskCount * 0.5)

  // 技术实力评分
  let tech = 2
  if (softwareCount.value > 10) tech += 1.5
  else if (softwareCount.value > 5) tech += 1
  else if (softwareCount.value > 0) tech += 0.5

  // 经营稳定性评分
  let stability = 3
  const age = parseInt(companyAge.value) || 0
  if (age > 10) stability += 1.5
  else if (age > 5) stability += 1
  else if (age > 3) stability += 0.5

  const overall = (basic + risk + tech + stability) / 4

  return { basic, risk, tech, stability, overall }
})

const ratingLabels = computed(() => {
  const getLabel = (score: number) => {
    if (score >= 4.5) return '优秀'
    if (score >= 3.5) return '良好'
    if (score >= 2.5) return '一般'
    return '较差'
  }

  return {
    basic: getLabel(rating.value.basic),
    risk: getLabel(rating.value.risk),
    tech: getLabel(rating.value.tech),
    stability: getLabel(rating.value.stability),
    overall: getLabel(rating.value.overall)
  }
})

// 方法
function statusColor(status: string): string {
  if (!status) return 'default'
  if (status.includes('存续') || status.includes('在营')) return 'green'
  if (status.includes('注销') || status.includes('吊销')) return 'red'
  return 'default'
}

function riskLevelColor(level: string): string {
  const colors: Record<string, string> = {
    excellent: 'green',
    good: 'blue',
    medium: 'orange',
    high: 'red',
    unknown: 'default'
  }
  return colors[level] || 'default'
}

function scrollToAnchor(id: string) {
  const el = document.getElementById(id)
  if (!el) return
  const y = el.getBoundingClientRect().top + window.pageYOffset - 56
  window.scrollTo({ top: y, behavior: 'smooth' })
}

function goBack() {
  router.push({ name: 'SupplierList' })
}

async function refreshData() {
  message.loading('正在刷新数据...')
  await loadData()
  message.success('数据已刷新')
}

async function loadData() {
  loading.value = true
  error.value = ''

  try {
    const creditCode = route.query.id as string

    // 调用后端 API（后端调用企查查 MCP）
    const data = await getSupplierQccInfoApi(creditCode)

    // 解析数据
    supplierInfo.value = data.basic_info
    profile.value = data.profile
    riskScan.value = data.risk_scan

    // 软件著作权列表
    if (data.software_copyrights && data.software_copyrights.软件著作权信息) {
      softwareList.value = data.software_copyrights.软件著作权信息
    } else {
      softwareList.value = []
    }

    // 对外投资列表
    if (data.external_investments && data.external_investments.对外投资信息) {
      investmentList.value = data.external_investments.对外投资信息
    } else {
      investmentList.value = []
    }

  } catch (e: any) {
    error.value = e?.message || '加载失败'
    message.error('加载供应商数据失败: ' + error.value)
  } finally {
    loading.value = false
  }
}

// 滚动监听
let anchorObserver: IntersectionObserver | null = null

watch(
  () => supplierInfo.value,
  () => {
    nextTick(() => {
      anchorObserver?.disconnect()
      anchorObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) activeAnchor.value = (e.target as HTMLElement).id
          })
        },
        { rootMargin: '-56px 0px -70% 0px' }
      )
      anchors.value.forEach((a) => {
        const el = document.getElementById(a.id)
        if (el) anchorObserver?.observe(el)
      })
    })
  },
  { flush: 'post' }
)

onMounted(loadData)
</script>

<style scoped>
/* 自定义样式 */
</style>
