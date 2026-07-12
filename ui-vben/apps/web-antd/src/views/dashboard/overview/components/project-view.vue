<template>
  <div class="space-y-4">
    <!-- Metrics -->
    <div class="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
      <metric-card label="进行中项目" :value="ex?.active_projects" unit="个" :digits="0" tone="primary" />
      <metric-card label="高风险项目" :value="ex?.high_risk_projects" unit="个" :digits="0" tone="danger" />
      <metric-card label="已完成项目" :value="ex?.completed_projects" unit="个" :digits="0" tone="received" />
      <metric-card label="待交付成果" :value="ex?.pending_deliverables" unit="项" :digits="0" tone="warning" />
      <metric-card label="逾期付款节点" :value="ex?.overdue_stages" unit="个" :digits="0" tone="danger" />
      <metric-card label="缺负责人项目" :value="ex?.missing_manager_projects" unit="个" :digits="0" tone="warning" />
    </div>

    <!-- 状态 / 风险分布 -->
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div class="rounded-lg border bg-card p-4 shadow-sm">
        <div class="mb-3 font-medium text-card-foreground">项目状态分布</div>
        <div class="space-y-3">
          <div v-for="b in statusBars" :key="b.status" class="space-y-1">
            <div class="flex justify-between text-sm">
              <span class="text-card-foreground">{{ b.status }}</span>
              <span class="text-xs text-muted-foreground">{{ b.count }} 个</span>
            </div>
            <div class="h-2 w-full rounded bg-accent">
              <div
                class="h-2 rounded"
                :style="{ width: b.pct + '%', background: 'var(--dash-primary)' }"
              ></div>
            </div>
          </div>
          <div v-if="!statusBars.length" class="text-sm text-muted-foreground">暂无数据</div>
        </div>
      </div>
      <div class="rounded-lg border bg-card p-4 shadow-sm">
        <div class="mb-3 font-medium text-card-foreground">项目风险分布</div>
        <div class="space-y-3">
          <div v-for="b in riskBars" :key="b.level" class="space-y-1">
            <div class="flex justify-between text-sm">
              <span class="text-card-foreground">{{ b.level }}</span>
              <span class="text-xs text-muted-foreground">{{ b.count }} 个</span>
            </div>
            <div class="h-2 w-full rounded bg-accent">
              <div
                class="h-2 rounded"
                :style="{ width: b.pct + '%', background: b.color }"
              ></div>
            </div>
          </div>
          <div v-if="!riskBars.length" class="text-sm text-muted-foreground">暂无数据</div>
        </div>
      </div>
    </div>

    <!-- 近期项目 -->
    <div class="rounded-lg border bg-card shadow-sm">
      <div class="border-b px-4 py-3 font-medium text-card-foreground">近期项目</div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b text-left text-muted-foreground">
              <th class="px-3 py-2 font-medium">项目名称</th>
              <th class="px-3 py-2 font-medium">客户</th>
              <th class="px-3 py-2 text-right font-medium">合同金额(万元)</th>
              <th class="px-3 py-2 font-medium">项目经理</th>
              <th class="px-3 py-2 font-medium">当前状态</th>
              <th class="px-3 py-2 font-medium">总体进度</th>
              <th class="px-3 py-2 font-medium">风险等级</th>
              <th class="px-3 py-2 font-medium">计划结束日期</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in ex?.recent_projects ?? []"
              :key="p.project_id"
              class="border-b last:border-0 hover:bg-accent"
            >
              <td class="px-3 py-2 font-medium text-card-foreground">
                {{ p.project_name || '数据待补充' }}
              </td>
              <td class="px-3 py-2 text-muted-foreground">
                {{ p.customer_name || '数据待补充' }}
              </td>
              <td class="px-3 py-2 text-right">
                {{ p.total_contract_amount ? fmtMoney(p.total_contract_amount) : '数据待补充' }}
              </td>
              <td class="px-3 py-2 text-muted-foreground">
                {{ p.project_manager || '数据待补充' }}
              </td>
              <td class="px-3 py-2 text-muted-foreground">
                {{ p.project_status || '数据待补充' }}
              </td>
              <td class="px-3 py-2">
                <a-progress
                  v-if="p.overall_progress"
                  :percent="p.overall_progress"
                  size="small"
                />
                <span v-else class="text-xs text-muted-foreground">数据待补充</span>
              </td>
              <td class="px-3 py-2">
                <a-tag v-if="p.risk_level" :color="riskTagColor(p.risk_level)" size="small">
                  {{ p.risk_level }}
                </a-tag>
                <span v-else class="text-xs text-muted-foreground">数据待补充</span>
              </td>
              <td class="px-3 py-2 text-muted-foreground">
                {{ p.planned_end || '数据待补充' }}
              </td>
            </tr>
            <tr v-if="!ex?.recent_projects?.length">
              <td colspan="8" class="px-3 py-6 text-center text-muted-foreground">
                暂无项目数据
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import type { DashboardOverview } from '#/api/dashboard';
import MetricCard from './metric-card.vue';
import { fmtMoney, riskTagColor, riskTone } from '../dashboard-types';

const props = defineProps<{ overview: DashboardOverview }>();

const ex = computed(() => props.overview.project_execution);

const statusBars = computed(() => {
  const arr = ex.value?.status_distribution ?? [];
  const max = Math.max(1, ...arr.map((d) => d.count || 0));
  return arr.map((d) => ({
    status: d.status || '未分类',
    count: d.count,
    pct: ((d.count || 0) / max) * 100,
  }));
});

const riskBars = computed(() => {
  const arr = ex.value?.risk_distribution ?? [];
  const max = Math.max(1, ...arr.map((d) => d.count || 0));
  return arr.map((d) => {
    const tone = riskTone(d.risk_level);
    const colorMap: Record<string, string> = {
      danger: 'var(--dash-danger)',
      warning: 'var(--dash-warning)',
      received: 'var(--dash-received)',
    };
    return {
      level: d.risk_level || '未知',
      count: d.count,
      pct: ((d.count || 0) / max) * 100,
      color: colorMap[tone] ?? 'var(--dash-muted, #9ca3af)',
    };
  });
});
</script>
