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
          <h2 class="text-xl font-semibold text-gray-800">合同详情</h2>
          <div v-if="c" class="text-sm text-gray-500 mt-0.5">
            {{ c.contract_id }} · {{ c.official_name || c.project_name }}
          </div>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a-tag
          v-if="c?.contract_status"
          :color="statusColor(c.contract_status)"
          class="rounded-full px-3 py-0.5 text-xs"
        >
          {{ statusLabel(c.contract_status) }}
        </a-tag>
        <a-button type="primary" size="small" ghost @click="openEditModal"> 编辑 </a-button>
        <a-button size="small" ghost> 导出 </a-button>
      </div>
    </div>

    <!-- 三态：loading / error / 正常内容 -->
    <state-block :loading="loading" :error="error" error-title="合同详情加载失败" @retry="load">
      <!-- ============ KPI 指标行（紧凑现代） ============ -->
      <div v-if="c" class="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">合同含税总额</div>
          <div class="text-2xl font-bold text-gray-900">{{ fmtMoney(c.contract_amount) }}</div>
          <div class="text-xs text-gray-400 mt-0.5">万元</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">已开票</div>
          <div class="text-2xl font-bold text-blue-600">{{ finance ? fmtMoney(invoiceTotal) : '—' }}</div>
          <div class="text-xs text-gray-400 mt-0.5">{{ finance ? invoiceRate + '% 开票率' : '—' }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">已回款</div>
          <div class="text-2xl font-bold text-green-600">{{ finance ? fmtMoney(paymentTotal) : '—' }}</div>
          <div class="text-xs text-gray-400 mt-0.5">{{ finance ? receiptRate + '% 回款率' : '—' }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">已开票未回款</div>
          <div class="text-2xl font-bold text-red-500">{{ finance ? fmtMoney(unreceivedAmount) : '—' }}</div>
          <div class="text-xs text-gray-400 mt-0.5">{{ finance ? unreceivedRate + '% 未回款率' : '—' }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">合同总额未回款</div>
          <div class="text-2xl font-bold text-orange-500">{{ finance ? fmtMoney(contractUnreceived) : '—' }}</div>
          <div class="text-xs text-gray-400 mt-0.5">{{ finance ? contractUnreceivedRate + '% 未回款率' : '—' }}</div>
        </div>
      </div>

      <!-- ============ 吸顶锚点条 ============ -->
      <div v-if="c" class="sticky top-0 z-20 bg-white/85 backdrop-blur-sm border-y border-gray-200 -mx-6 px-6">
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

      <!-- ============ 第1行：基本信息 + 财务汇总 ============ -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <!-- 基本信息卡片（占 8/12） -->
        <a-card
          title="基本信息"
          id="overview"
          class="lg:col-span-8 rounded-lg"
          size="small"
          :body-style="{ padding: '16px' }"
        >
          <div v-if="c" class="space-y-5">
            <!-- 签约信息 -->
            <div>
              <div class="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wider">签约信息</div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div class="text-xs text-gray-400 mb-1">签订日期</div>
                  <div class="font-medium text-gray-900">{{ c.sign_date || '-' }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-400 mb-1">到期日期</div>
                  <div class="font-medium text-gray-900">{{ c.expiry_date || '未设置' }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-400 mb-1">税率</div>
                  <div class="font-medium text-gray-900">{{ c.tax_rate ? c.tax_rate + '%' : '-' }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-400 mb-1">SGSC编号</div>
                  <div class="font-medium text-gray-900">{{ c.sgsc_id || '-' }}</div>
                </div>
              </div>
            </div>

            <a-divider class="my-0" />

            <!-- 合同双方 -->
            <div>
              <div class="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wider">合同双方</div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <a-card size="small" class="bg-blue-50 border-0" :body-style="{ padding: '12px' }">
                  <div class="text-xs text-blue-600 mb-1 font-medium">甲方</div>
                  <div class="font-medium text-gray-900 text-sm">{{ clean(c.party_a) }}</div>
                  <div v-if="c.party_a_contact" class="text-xs text-gray-500 mt-1">
                    👤 {{ c.party_a_contact }}
                    <span v-if="c.party_a_phone"> · 📞 {{ c.party_a_phone }}</span>
                  </div>
                </a-card>
                <a-card size="small" class="bg-green-50 border-0" :body-style="{ padding: '12px' }">
                  <div class="text-xs text-green-600 mb-1 font-medium">乙方</div>
                  <div class="font-medium text-gray-900 text-sm">{{ clean(c.party_b) }}</div>
                  <div v-if="c.party_b_contact" class="text-xs text-gray-500 mt-1">
                    👤 {{ c.party_b_contact }}
                    <span v-if="c.party_b_phone"> · 📞 {{ c.party_b_phone }}</span>
                  </div>
                </a-card>
              </div>
            </div>

            <!-- 验收标准（如有） -->
            <template v-if="c.acceptance_criteria || c.acceptance_method">
              <a-divider class="my-0" />
              <div>
                <div class="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wider">验收标准</div>
                <div v-if="c.acceptance_criteria" class="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 rounded-lg p-3">
                  {{ c.acceptance_criteria }}
                </div>
                <div v-if="c.acceptance_method" class="text-xs text-gray-500 mt-1">
                  验收方式：{{ c.acceptance_method }}
                  <span v-if="c.acceptance_location"> · {{ c.acceptance_location }}</span>
                </div>
              </div>
            </template>

            <!-- 中标信息（如有） -->
            <template v-if="c.bidder || c.bid_amount">
              <a-divider class="my-0" />
              <div>
                <div class="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wider">中标信息</div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div v-if="c.bidder">
                    <div class="text-xs text-gray-400 mb-1">中标方</div>
                    <div class="font-medium text-gray-900 text-sm">{{ c.bidder }}</div>
                  </div>
                  <div v-if="c.bid_amount">
                    <div class="text-xs text-gray-400 mb-1">中标金额</div>
                    <div class="font-medium text-gray-900 text-sm">¥{{ c.bid_amount }} 万元</div>
                  </div>
                  <div v-if="c.bid_date">
                    <div class="text-xs text-gray-400 mb-1">中标时间</div>
                    <div class="font-medium text-gray-900 text-sm">{{ c.bid_date }}</div>
                  </div>
                </div>
              </div>
            </template>

            <!-- 分包信息（如有） -->
            <template v-if="c.subcontract_company">
              <a-divider class="my-0" />
              <div>
                <div class="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wider">分包信息</div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div>
                    <div class="text-xs text-gray-400 mb-1">分包单位</div>
                    <div class="font-medium text-gray-900 text-sm">{{ c.subcontract_company }}</div>
                  </div>
                  <div v-if="c.subcontract_contact">
                    <div class="text-xs text-gray-400 mb-1">联系人</div>
                    <div class="font-medium text-gray-900 text-sm">{{ c.subcontract_contact }}</div>
                  </div>
                  <div v-if="c.subcontract_amount">
                    <div class="text-xs text-gray-400 mb-1">分包金额</div>
                    <div class="font-medium text-gray-900 text-sm">¥{{ c.subcontract_amount }} 万元</div>
                  </div>
                </div>
              </div>
            </template>
          </div>

          <div v-else class="py-8 text-center text-gray-400 text-sm">
            <a-empty description="暂无基本信息" />
          </div>
        </a-card>

        <!-- 关联发票卡片（替代原财务汇总，占 4/12） -->
        <a-card
          title="关联发票（时间正序）"
          class="lg:col-span-4 rounded-xl shadow-sm"
          size="small"
          :body-style="{ padding: '12px' }"
        >
          <template v-if="sortedInvoices.length">
            <div class="space-y-2 max-h-[400px] overflow-y-auto">
              <div
                v-for="inv in sortedInvoices"
                :key="inv.invoice_id"
                class="flex items-center justify-between p-2.5 bg-gray-50 rounded-lg hover:bg-blue-50/50 cursor-pointer"
                @click="router.push(`/web/invoices/detail/${inv.invoice_id}`)"
              >
                <div class="flex items-center gap-3 min-w-0">
                  <div class="w-7 h-7 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold shrink-0">
                    {{ sortedInvoices.indexOf(inv) + 1 }}
                  </div>
                  <div class="min-w-0">
                    <div class="font-medium text-sm truncate flex items-center gap-2">
                      {{ inv.invoice_no || '发票 ' + (sortedInvoices.indexOf(inv) + 1) }}
                      <a-tag :color="invoiceTypeColor(inv.invoice_type)" size="small">{{ invoiceTypeLabel(inv.invoice_type) }}</a-tag>
                    </div>
                    <div class="text-xs text-gray-400">{{ inv.invoice_date || '日期未知' }}</div>
                  </div>
                </div>
                <div class="text-right shrink-0">
                  <div class="font-semibold text-sm" :class="invoiceStatusAmountClass(inv.status)">
                    ¥{{ fmtMoney(inv.amount / 10000) }} 万
                  </div>
                  <a-tag :color="invoiceStatusColor(inv.status)" size="small">
                    {{ invoiceStatusText(inv.status) }}
                  </a-tag>
                </div>
              </div>
            </div>
          </template>
          <div v-else class="py-8 flex flex-col items-center text-center">
            <a-empty description="暂无关联发票" />
            <div class="text-sm text-gray-400 mt-2">发票数据待补充</div>
          </div>
        </a-card>
      </div>

      <!-- ============ 第2行：关联项目 + 合同文件 ============ -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <a-card title="关联项目" size="small" class="rounded-xl shadow-sm" :body-style="{ padding: '12px' }">
          <template v-if="projects.length">
            <div
              v-for="p in projects"
              :key="p.project_id"
              class="flex items-center justify-between py-3 border-b border-dashed border-gray-200 last:border-0"
            >
              <div class="flex-1 min-w-0">
                <a
                  class="text-primary font-medium cursor-pointer hover:underline truncate block"
                  @click="router.push({ name: 'ProjectDetail', params: { id: p.project_id } })"
                >
                  {{ p.project_name }}
                </a>
                <div class="text-xs text-gray-400 mt-1 flex gap-2">
                  <a-tag size="small">{{ p.project_type }}</a-tag>
                  <a-tag size="small" :color="p.project_status === 'active' ? 'green' : 'default'">
                    {{ p.project_status }}
                  </a-tag>
                </div>
              </div>
              <a-button
                size="small"
                type="link"
                @click="router.push({ name: 'ProjectDetail', params: { id: p.project_id } })"
              >
                查看详情 &#8594;
              </a-button>
            </div>
          </template>
          <div v-else class="py-12 text-center">
            <a-empty description="暂无关联项目" />
          </div>
        </a-card>

        <a-card title="合同文件" size="small" class="rounded-xl shadow-sm" :body-style="{ padding: '12px' }">
          <div class="mb-3 flex justify-end">
            <a-upload
              :before-upload="beforeUpload"
              :show-upload-list="false"
              :disabled="uploading"
            >
              <a-button size="small" type="primary" :loading="uploading">
                <span class="mr-1">&#8593;</span> 上传文件
              </a-button>
            </a-upload>
          </div>
          <template v-if="files.length">
            <div
              v-for="f in files"
              :key="f.file_id"
              class="flex items-center justify-between py-3 border-b border-dashed border-gray-200 last:border-0 hover:bg-gray-50 rounded px-2"
            >
              <div class="flex items-center gap-3 min-w-0">
                <a-icon
                  :type="fileIcon(f.file_type)"
                  :style="{ fontSize: '24px', color: fileColor(f.file_type) }"
                />
                <div class="min-w-0">
                  <div class="font-medium text-sm truncate">{{ f.file_name }}</div>
                  <div class="text-xs text-gray-400">
                    {{ f.file_type?.toUpperCase() }} &#183; {{ formatSize(f.file_size) }}
                    <span v-if="f.upload_time">&#183; {{ f.upload_time?.slice(0, 10) }}</span>
                  </div>
                </div>
              </div>
              <a-button
                size="small"
                type="link"
                :href="downloadUrl(contractId, f.file_id)"
                target="_blank"
              >
                预览
              </a-button>
            </div>
          </template>
          <div v-else class="py-12 text-center">
            <a-empty description="暂无合同文件" />
          </div>
        </a-card>
      </div>

      <!-- ============ 按合同类型切换内容区 ============ -->
      <ResearchContent
        v-if="isResearch"
        :contract="c"
        :stages="stages"
        :budgets="budgets"
        :deliverables="deliverables"
        :payments="payments"
        :contract-id="contractId"
        @reload="load"
      />
      <ServiceContent
        v-else-if="isService"
        :contract="c"
        :payments="payments"
        :contract-id="contractId"
        @reload="load"
      />

      <!-- ============ 项目团队 ============ -->
      <a-card
        title="项目团队"
        id="team"
        size="small"
        class="rounded-lg"
        :body-style="{ padding: '12px' }"
      >
        <div v-if="teamMembers.length" class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div
            v-for="m in teamMembers"
            :key="m.role"
            class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
          >
            <div
              class="w-9 h-9 rounded-full flex items-center justify-center text-white text-sm font-bold shrink-0"
              :style="{ backgroundColor: teamRoleColor(m.role) }"
            >
              {{ m.person_name.charAt(0) }}
            </div>
            <div class="min-w-0">
              <div class="text-xs text-gray-400 mb-0.5">{{ m.role_label }}</div>
              <div class="font-medium text-gray-800 text-sm">{{ m.person_name }}</div>
              <div v-if="m.phone" class="text-xs text-gray-400 mt-0.5">📞 {{ m.phone }}</div>
            </div>
          </div>
        </div>
        <div v-else class="py-6 text-center">
          <a-empty description="暂无团队成员数据" />
        </div>
      </a-card>

      <!-- ============ 合同条款 ============ -->
      <a-card
        title="合同条款"
        id="clauses"
        size="small"
        class="rounded-lg"
        :body-style="{ padding: '16px' }"
      >
        <a-collapse
          v-if="nonConfidentialClauses.length"
          :default-active-key="[]"
        >
          <a-collapse-panel
            v-for="g in nonConfidentialGroups"
            :key="g.key"
            :header="g.label"
          >
            <div class="space-y-3">
              <div
                v-for="cl in g.items"
                :key="cl.clause_id"
                class="clause-item"
              >
                <div class="flex flex-wrap items-center gap-2 mb-2">
                  <span class="font-medium text-sm">{{ cl.trigger_type || '&#8212;' }}</span>
                  <a-tag v-if="cl.rate_pct != null" color="orange">
                    违约金 {{ cl.rate_pct }}%{{ cl.clause_category === 'overdue' ? '/天' : '' }}
                  </a-tag>
                  <a-tag v-if="cl.threshold_days" color="red">逾期超 {{ cl.threshold_days }} 日解除</a-tag>
                  <a-tag v-if="cl.refund_full" color="red">退还全部款项</a-tag>
                </div>
                <div v-if="cl.clause_text" class="clause-text">{{ cl.clause_text }}</div>
              </div>
            </div>
          </a-collapse-panel>
        </a-collapse>
        <div v-else class="py-8 text-center">
          <a-empty description="暂无违约/罚款条款" />
        </div>
      </a-card>

      <!-- ============ 保密条款 ============ -->
      <a-card
        title="保密条款"
        size="small"
        class="rounded-xl shadow-sm"
        :body-style="{ padding: '16px' }"
        v-if="confidentialClauses.length"
      >
        <div class="space-y-3">
          <div
            v-for="cl in confidentialClauses"
            :key="cl.clause_id"
            class="clause-item"
          >
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <a-tag color="purple">保密</a-tag>
              <span class="font-medium text-sm">{{ cl.trigger_type || '&#8212;' }}</span>
              <a-tag v-if="cl.rate_pct != null" color="orange">违约金 {{ cl.rate_pct }}%</a-tag>
            </div>
            <div v-if="cl.clause_text" class="clause-text">{{ cl.clause_text }}</div>
          </div>
        </div>
      </a-card>

      <!-- ============ 编辑合同弹窗 ============ -->
      <a-modal
        v-model:open="editModalVisible"
        title="编辑合同"
        width="800px"
        :confirm-loading="editSaving"
        @ok="saveEdit"
        :ok-text="'保存'"
        :cancel-text="'取消'"
      >
        <a-form :model="editForm" layout="vertical" v-if="editForm">
          <!-- 基本信息 -->
          <div class="text-sm font-semibold text-gray-500 mb-3 border-b pb-2">基本信息</div>
          <div class="grid grid-cols-2 gap-4">
            <a-form-item label="合同编号" name="contract_id">
              <a-input v-model:value="editForm.contract_id" disabled />
            </a-form-item>
            <a-form-item label="合同金额（万元）" name="contract_amount">
              <a-input-number v-model:value="editForm.contract_amount" :precision="2" class="w-full" />
            </a-form-item>
            <a-form-item label="项目名称" name="project_name">
              <a-input v-model:value="editForm.project_name" />
            </a-form-item>
            <a-form-item label="项目类型">
              <a-select v-model:value="editForm.project_type">
                <a-select-option value="科研类">科研类</a-select-option>
                <a-select-option value="服务类">服务类</a-select-option>
                <a-select-option value="物资类">物资类</a-select-option>
                <a-select-option value="施工类">施工类</a-select-option>
              </a-select>
            </a-form-item>
          </div>

          <!-- 签约信息 -->
          <div class="text-sm font-semibold text-gray-500 mb-3 border-b pb-2 mt-4">签约信息</div>
          <div class="grid grid-cols-2 gap-4">
            <a-form-item label="甲方" name="party_a">
              <a-input v-model:value="editForm.party_a" />
            </a-form-item>
            <a-form-item label="乙方" name="party_b">
              <a-input v-model:value="editForm.party_b" />
            </a-form-item>
            <a-form-item label="签订日期">
              <a-date-picker v-model:value="editForm.sign_date" value-format="YYYY-MM-DD" class="w-full" />
            </a-form-item>
            <a-form-item label="税率（%）">
              <a-input-number v-model:value="editForm.tax_rate" :precision="2" :min="0" :max="100" class="w-full" />
            </a-form-item>
            <a-form-item label="签订地点">
              <a-input v-model:value="editForm.sign_location" placeholder="合同签订地点" />
            </a-form-item>
            <a-form-item label="甲方负责人">
              <a-input v-model:value="editForm.party_a_contact" placeholder="姓名" />
            </a-form-item>
            <a-form-item label="甲方电话">
              <a-input v-model:value="editForm.party_a_phone" placeholder="联系方式" />
            </a-form-item>
            <a-form-item label="乙方负责人">
              <a-input v-model:value="editForm.party_b_contact" placeholder="姓名" />
            </a-form-item>
            <a-form-item label="乙方电话">
              <a-input v-model:value="editForm.party_b_phone" placeholder="联系方式" />
            </a-form-item>
            <a-form-item label="合同状态">
              <a-select v-model:value="editForm.contract_status">
                <a-select-option value="signed">已签订</a-select-option>
                <a-select-option value="active">执行中</a-select-option>
                <a-select-option value="completed">已完成</a-select-option>
                <a-select-option value="expired">已到期</a-select-option>
                <a-select-option value="terminated">已终止</a-select-option>
                <a-select-option value="pending">待签订</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="项目性质">
              <a-select v-model:value="editForm.project_nature" allow-clear>
                <a-select-option value="新建项目">新建项目</a-select-option>
                <a-select-option value="续建项目">续建项目</a-select-option>
                <a-select-option value="扩建项目">扩建项目</a-select-option>
              </a-select>
            </a-form-item>
          </div>

          <!-- 合同期限（两类合同通用） -->
          <div class="text-sm font-semibold text-gray-500 mb-3 border-b pb-2 mt-4">合同期限</div>
          <div class="grid grid-cols-2 gap-4">
            <a-form-item label="服务期限">
              <a-input v-model:value="editForm.service_period" placeholder="如：合同签订之日起至2026年12月31日" />
            </a-form-item>
            <a-form-item label="到期日期">
              <a-date-picker v-model:value="editForm.expiry_date" value-format="YYYY-MM-DD" class="w-full" />
            </a-form-item>
          </div>

          <!-- 服务内容与方式（仅服务类） -->
          <template v-if="editForm.project_type === '服务类'">
            <div class="text-sm font-semibold text-gray-500 mb-3 border-b pb-2 mt-4">服务内容与方式</div>
            <a-form-item label="服务内容">
              <a-textarea v-model:value="editForm.service_content" :rows="4" placeholder="合同约定的技术服务内容..." />
            </a-form-item>
            <div class="grid grid-cols-2 gap-4">
              <a-form-item label="服务方式">
                <a-input v-model:value="editForm.service_method" placeholder="如：现场技术服务" />
              </a-form-item>
              <a-form-item label="服务地点">
                <a-input v-model:value="editForm.service_location" placeholder="如：四川省乐山市" />
              </a-form-item>
              <a-form-item label="服务进度">
                <a-input v-model:value="editForm.service_schedule" placeholder="如：分3次交付" />
              </a-form-item>
              <a-form-item label="服务质量要求">
                <a-input v-model:value="editForm.service_quality" placeholder="如：符合XX技术规范" />
              </a-form-item>
            </div>
          </template>

          <!-- 验收标准 -->
          <div class="text-sm font-semibold text-gray-500 mb-3 border-b pb-2 mt-4">验收信息</div>
          <a-form-item label="验收标准">
            <a-textarea v-model:value="editForm.acceptance_criteria" :rows="3" placeholder="验收标准和条件..." />
          </a-form-item>
          <div class="grid grid-cols-2 gap-4">
            <a-form-item label="验收方式">
              <a-input v-model:value="editForm.acceptance_method" placeholder="如：现场验收" />
            </a-form-item>
            <a-form-item label="验收地点">
              <a-input v-model:value="editForm.acceptance_location" placeholder="验收时间和地点" />
            </a-form-item>
          </div>

          <!-- 关联信息 -->
          <div class="text-sm font-semibold text-gray-500 mb-3 border-b pb-2 mt-4">关联信息</div>
          <div class="grid grid-cols-2 gap-4">
            <a-form-item label="正式名称（official_name）">
              <a-input v-model:value="editForm.official_name" placeholder="在列表中显示的完整名称" />
            </a-form-item>
            <a-form-item label="财务编号（financial_id）">
              <a-input v-model:value="editForm.financial_id" placeholder="内部财务系统编号" />
            </a-form-item>
            <a-form-item label="项目负责人（project_leader）">
              <a-input v-model:value="editForm.project_leader" />
            </a-form-item>
            <a-form-item label="SGSC编号（sgsc_id）">
              <a-input v-model:value="editForm.sgsc_id" placeholder="国家电网合同编号" />
            </a-form-item>
          </div>

          <!-- 科研类专属：阶段与交付物 -->
          <template v-if="editForm.project_type === '科研类'">
            <div class="text-sm font-semibold text-gray-500 mb-3 border-b pb-2 mt-4">研究阶段</div>
            <div class="space-y-3">
              <div
                v-for="(s, idx) in editForm.editStages"
                :key="idx"
                class="flex items-start gap-2 p-3 bg-gray-50 rounded-lg"
              >
                <span class="text-xs text-gray-400 mt-1.5 min-w-[40px]">阶段{{ Number(idx) + 1 }}</span>
                <div class="flex-1 grid grid-cols-2 gap-2">
                  <a-input v-model:value="s.stage_name" placeholder="阶段名称" size="small" />
                  <a-select v-model:value="s.status" size="small" placeholder="状态">
                    <a-select-option value="completed">已完成</a-select-option>
                    <a-select-option value="in_progress">进行中</a-select-option>
                    <a-select-option value="pending">待开始</a-select-option>
                  </a-select>
                  <a-input v-model:value="s.start_time" placeholder="开始时间" size="small" />
                  <a-input v-model:value="s.end_time" placeholder="结束时间" size="small" />
                  <a-textarea v-model:value="s.remarks" placeholder="阶段主要内容" :rows="2" size="small" class="col-span-2" />
                  <a-textarea v-model:value="s.acceptance_criteria" placeholder="考核目标" :rows="2" size="small" class="col-span-2" />
                </div>
                <a-button type="text" danger size="small" @click="removeEditStage(Number(idx))">
                  <template #icon><span class="text-lg leading-none">✕</span></template>
                </a-button>
              </div>
              <a-button type="dashed" size="small" block @click="addEditStage">
                <span class="mr-1">＋</span> 添加阶段
              </a-button>
            </div>

            <div class="text-sm font-semibold text-gray-500 mb-3 border-b pb-2 mt-4">交付物</div>
            <div class="space-y-3">
              <div
                v-for="(d, idx) in editForm.editDeliverables"
                :key="idx"
                class="flex items-start gap-2 p-3 bg-gray-50 rounded-lg"
              >
                <span class="text-xs text-gray-400 mt-1.5 min-w-[40px]">交付{{ Number(idx) + 1 }}</span>
                <div class="flex-1 grid grid-cols-3 gap-2">
                  <a-input v-model:value="d.deliverable_name" placeholder="交付物名称" size="small" class="col-span-2" />
                  <a-select v-model:value="d.deliverable_type" size="small" placeholder="类型">
                    <a-select-option value="报告">报告</a-select-option>
                    <a-select-option value="软件">软件</a-select-option>
                    <a-select-option value="专利">专利</a-select-option>
                    <a-select-option value="样机">样机</a-select-option>
                    <a-select-option value="论文">论文</a-select-option>
                    <a-select-option value="其他">其他</a-select-option>
                  </a-select>
                  <a-select v-model:value="d.status" size="small" placeholder="状态">
                    <a-select-option value="completed">已交付</a-select-option>
                    <a-select-option value="pending">待交付</a-select-option>
                  </a-select>
                </div>
                <a-button type="text" danger size="small" @click="removeEditDeliverable(Number(idx))">
                  <template #icon><span class="text-lg leading-none">✕</span></template>
                </a-button>
              </div>
              <a-button type="dashed" size="small" block @click="addEditDeliverable">
                <span class="mr-1">＋</span> 添加交付物
              </a-button>
            </div>
          </template>
        </a-form>
      </a-modal>

      <!-- ============ 添加发票弹窗 ============ -->
      <a-modal
        v-model:open="addInvoiceVisible"
        title="添加发票"
        :confirm-loading="invoiceSaving"
        @ok="saveInvoice"
        :ok-text="'保存'"
        :cancel-text="'取消'"
      >
        <a-form :model="invoiceForm" layout="vertical">
          <div class="grid grid-cols-2 gap-4">
            <a-form-item label="发票号">
              <a-input v-model:value="invoiceForm.invoice_no" placeholder="如：INV-2026-001" />
            </a-form-item>
            <a-form-item label="发票日期">
              <a-date-picker v-model:value="invoiceForm.invoice_date" value-format="YYYY-MM-DD" class="w-full" />
            </a-form-item>
            <a-form-item label="金额（万元）">
              <a-input-number v-model:value="invoiceForm.amount" :precision="2" :min="0" class="w-full" placeholder="发票金额" />
            </a-form-item>
            <a-form-item label="税率（%）">
              <a-input-number v-model:value="invoiceForm.tax_rate" :precision="2" :min="0" :max="100" class="w-full" placeholder="如：6" />
            </a-form-item>
            <a-form-item label="发票类型">
              <a-select v-model:value="invoiceForm.invoice_type">
                <a-select-option value="客户开票">客户开票</a-select-option>
                <a-select-option value="客户回款">客户回款</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="方向">
              <a-select v-model:value="invoiceForm.direction">
                <a-select-option value="outbound">销项（开票）</a-select-option>
                <a-select-option value="inbound">进项（回款）</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="回款日期">
              <a-date-picker v-model:value="invoiceForm.received_date" value-format="YYYY-MM-DD" class="w-full" />
            </a-form-item>
            <a-form-item label="状态">
              <a-select v-model:value="invoiceForm.status">
                <a-select-option value="已开">已开</a-select-option>
                <a-select-option value="已回款">已回款</a-select-option>
                <a-select-option value="待开">待开</a-select-option>
              </a-select>
            </a-form-item>
          </div>
          <a-form-item label="备注">
            <a-textarea v-model:value="invoiceForm.notes" :rows="2" placeholder="补充说明..." />
          </a-form-item>
        </a-form>
      </a-modal>
    </state-block>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getContractDetailApi, getContractTeamApi, createPaymentApi, deletePaymentApi, uploadContractFileApi, contractFileDownloadUrl, updateContractApi } from '#/api/contracts'
import { createInvoiceApi } from '#/api/invoices'
import StageGantt from '#/views/contracts/components/stage-gantt.vue'
import ResearchContent from '#/views/contracts/components/ResearchContent.vue'
import ServiceContent from '#/views/contracts/components/ServiceContent.vue'
import StateBlock from '#/components/state-block/index.vue'

const route = useRoute()
const router = useRouter()
const detail = ref<any>(null)
const loading = ref(true)
const error = ref('')
const uploading = ref(false)
const serviceExpanded = ref(false)

// 编辑弹窗
const editModalVisible = ref(false)
const editSaving = ref(false)
const editForm = ref<Record<string, any>>({})

function openEditModal() {
  if (!c.value) return
  editForm.value = {
    contract_id: c.value.contract_id || '',
    project_name: c.value.project_name || '',
    official_name: c.value.official_name || '',
    contract_amount: c.value.contract_amount || 0,
    party_a: c.value.party_a || '',
    party_b: c.value.party_b || '',
    sign_date: c.value.sign_date || '',
    expiry_date: c.value.expiry_date || '',
    tax_rate: c.value.tax_rate || null,
    contract_status: c.value.contract_status || 'signed',
    project_type: c.value.project_type || '服务类',
    project_nature: c.value.project_nature || '',
    project_leader: c.value.project_leader || '',
    financial_id: c.value.financial_id || '',
    service_period: c.value.service_period || '',
    service_content: c.value.service_content || '',
    sgsc_id: c.value.sgsc_id || '',
    party_a_contact: c.value.party_a_contact || '',
    party_a_phone: c.value.party_a_phone || '',
    party_b_contact: c.value.party_b_contact || '',
    party_b_phone: c.value.party_b_phone || '',
    service_method: c.value.service_method || '',
    service_location: c.value.service_location || '',
    service_schedule: c.value.service_schedule || '',
    service_quality: c.value.service_quality || '',
    acceptance_criteria: c.value.acceptance_criteria || '',
    acceptance_method: c.value.acceptance_method || '',
    acceptance_location: c.value.acceptance_location || '',
    sign_location: c.value.sign_location || '',
    // 科研类专属：阶段与交付物
    editStages: (stages.value || []).map((s: any) => ({
      stage_name: s.stage_name || '',
      stage_number: s.stage_number,
      start_time: s.start_time || '',
      end_time: s.end_time || '',
      remarks: s.remarks || '',
      acceptance_criteria: s.acceptance_criteria || '',
      status: s.status || 'pending',
      stage_id: s.stage_id || '',
    })),
    editDeliverables: (deliverables.value || []).map((d: any) => ({
      deliverable_name: d.deliverable_name || '',
      deliverable_type: d.deliverable_type || '报告',
      status: d.status || 'pending',
      deliverable_id: d.deliverable_id || '',
    })),
  }
  editModalVisible.value = true
}

// 阶段增删
function addEditStage() {
  if (!editForm.value) return
  const stages = editForm.value.editStages || []
  if (!Array.isArray(stages)) editForm.value.editStages = []
  editForm.value.editStages.push({
    stage_name: '',
    stage_number: stages.length + 1,
    start_time: '',
    end_time: '',
    remarks: '',
    acceptance_criteria: '',
    status: 'pending',
    stage_id: '',
  })
}
function removeEditStage(idx: number) {
  if (!editForm.value || !Array.isArray(editForm.value.editStages)) return
  editForm.value.editStages.splice(idx, 1)
}

// 交付物增删
function addEditDeliverable() {
  if (!editForm.value) return
  const dels = editForm.value.editDeliverables || []
  if (!Array.isArray(dels)) editForm.value.editDeliverables = []
  editForm.value.editDeliverables.push({
    deliverable_name: '',
    deliverable_type: '报告',
    status: 'pending',
    deliverable_id: '',
  })
}
function removeEditDeliverable(idx: number) {
  if (!editForm.value || !Array.isArray(editForm.value.editDeliverables)) return
  editForm.value.editDeliverables.splice(idx, 1)
}

async function saveEdit() {
  if (!c.value || !editForm.value) return
  editSaving.value = true
  try {
    const payload: Record<string, any> = { ...editForm.value }
    // 如果 project_type 变了，或本身就是科研类，附带阶段和交付物
    const isResearch = editForm.value.project_type === '科研类'
    if (isResearch && Array.isArray(editForm.value.editStages)) {
      payload.stages = editForm.value.editStages
    }
    if (isResearch && Array.isArray(editForm.value.editDeliverables)) {
      payload.deliverables = editForm.value.editDeliverables
    }
    await updateContractApi(c.value.contract_id, payload)
    message.success('合同更新成功')
    editModalVisible.value = false
    load() // 刷新数据
  } catch (e: any) {
    message.error('更新失败: ' + (e?.message || '未知错误'))
  } finally {
    editSaving.value = false
  }
}

const c = computed(() => detail.value?.contract ?? null)
const isResearch = computed(() => c.value?.project_type === '科研类')
const isService = computed(() => c.value?.project_type === '服务类')

// 吸顶锚点条：数据 + 滚动联动
const anchors = computed(() => [
  { id: 'overview', label: '概览' },
  { id: 'content', label: isResearch.value ? '阶段' : '服务内容' },
  { id: 'payment', label: '付款' },
  { id: 'team', label: '团队' },
  { id: 'clauses', label: '条款' },
])
const activeAnchor = ref('overview')
function scrollToAnchor(id: string) {
  const el = document.getElementById(id)
  if (!el) return
  const y = el.getBoundingClientRect().top + window.pageYOffset - 56
  window.scrollTo({ top: y, behavior: 'smooth' })
}
let anchorObserver: IntersectionObserver | null = null
watch(
  () => c.value,
  () => {
    nextTick(() => {
      anchorObserver?.disconnect()
      anchorObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) activeAnchor.value = (e.target as HTMLElement).id
          })
        },
        { rootMargin: '-56px 0px -70% 0px' },
      )
      anchors.value.forEach((a) => {
        const el = document.getElementById(a.id)
        if (el) anchorObserver?.observe(el)
      })
    })
  },
  { flush: 'post' },
)
onUnmounted(() => anchorObserver?.disconnect())
const stages = computed(() => detail.value?.stages ?? [])
const payments = computed(() => detail.value?.payments ?? [])
const deliverables = computed(() => detail.value?.deliverables ?? [])

// 关联发票 — 按日期正序排列（距现在远的在前）
const invoiceList = computed(() => (detail.value?.invoices as any[]) ?? [])
const sortedInvoices = computed(() => {
  return [...invoiceList.value].sort((a, b) => {
    const da = a.invoice_date || '9999-99-99'
    const db = b.invoice_date || '9999-99-99'
    return da.localeCompare(db)
  })
})
const addInvoiceVisible = ref(false)
const invoiceSaving = ref(false)
const invoiceForm = ref<Record<string, any>>({})

function openAddInvoice() {
  invoiceForm.value = {
    invoice_no: '',
    invoice_date: '',
    amount: null,
    tax_rate: c.value?.tax_rate || null,
    invoice_type: '客户开票',
    direction: 'outbound',
    received_date: '',
    status: '已开',
    notes: '',
  }
  addInvoiceVisible.value = true
}

async function saveInvoice() {
  invoiceSaving.value = true
  try {
    await createInvoiceApi({
      ...invoiceForm.value,
      project_id: c.value?.contract_id || '',
    })
    message.success('发票已创建')
    addInvoiceVisible.value = false
    load() // 刷新数据
  } catch (e: any) {
    message.error('创建失败: ' + (e?.message || '未知错误'))
  } finally {
    invoiceSaving.value = false
  }
}
const finance = computed(() => detail.value?.finance ?? null)
const projects = computed(() => detail.value?.projects ?? [])
const files = computed(() => {
  const raw = (detail.value?.files as any[]) ?? []
  return raw.filter((f: any) => {
    const t = (f.file_type || '').toLowerCase()
    return !t.includes('text') && !t.includes('.txt') && !t.includes('plain')
  })
})
const clauses = computed(() => detail.value?.clauses ?? [])

// 保密条款单独展示（兼容新旧分类）
const confidentialClauses = computed(() =>
  clauses.value.filter(
    (cl: any) => cl.clause_category === 'confidentiality' || cl.clause_category === 'confidential'
  )
)
const nonConfidentialClauses = computed(() =>
  clauses.value.filter(
    (cl: any) =>
      cl.clause_category !== 'confidentiality' && cl.clause_category !== 'confidential'
  )
)

// 非保密条款分组
const nonConfidentialGroups = computed(() => {
  const CAT_LABELS: Record<string, string> = {
    breach_liability: '违约责任',
    liquidated_damages: '违约金',
    penalty: '罚款',
    overdue: '逾期',
    compensation: '赔偿',
    ip: '知识产权',
    force_majeure: '不可抗力',
    termination: '解除/终止',
    dispute: '争议解决',
  }
  const CAT_ORDER = [
    'breach_liability',
    'liquidated_damages',
    'penalty',
    'overdue',
    'compensation',
    'ip',
    'dispute',
    'force_majeure',
    'termination',
  ]
  const map: Record<string, any[]> = {}
  for (const cl of nonConfidentialClauses.value) (map[cl.clause_category] ||= []).push(cl)
  return CAT_ORDER.filter((c) => map[c]).map((c) => ({ key: c, label: CAT_LABELS[c], items: map[c] }))
})

// 经费预算
const budgets = computed(() => detail.value?.budgets ?? [])

// 项目团队
const teamRaw = ref<any[]>([])
const teamMembers = computed(() => teamRaw.value || [])
const teamLoading = ref(false)

function teamRoleColor(role: string): string {
  const colors: Record<string, string> = {
    project_leader: '#1677ff',
    party_a_contact: '#52c41a',
    party_b_contact: '#fa8c16',
  }
  return colors[role] || '#8c8c8c'
}

async function loadTeam() {
  if (!route.query.id) return
  teamLoading.value = true
  try {
    teamRaw.value = (await getContractTeamApi(route.query.id as string))?.key_members ?? []
  } catch { /* silent */ }
  finally { teamLoading.value = false }
}

// 付款 CRUD
const addPaymentVisible = ref(false)
const paymentSaving = ref(false)
const paymentForm = ref<Record<string, any>>({})

function openAddPaymentModal() {
  paymentForm.value = {
    payment_stage: '',
    planned_amount: 0,
    planned_date: '',
    status: 'pending',
    payment_condition: '',
  }
  addPaymentVisible.value = true
}

async function savePayment() {
  paymentSaving.value = true
  try {
    await createPaymentApi(contractId.value, paymentForm.value)
    message.success('付款记录已添加')
    addPaymentVisible.value = false
    load()
  } catch (e: any) {
    message.error('添加失败: ' + (e?.message || '未知错误'))
  } finally {
    paymentSaving.value = false
  }
}

async function deletePayment(p: any) {
  if (!p?.payment_id) return
  try {
    await deletePaymentApi(contractId.value, p.payment_id)
    message.success('付款记录已删除')
    load()
  } catch (e: any) {
    message.error('删除失败: ' + (e?.message || '未知错误'))
  }
}

// 合同状态标签
function statusColor(status: string): string {
  const map: Record<string, string> = {
    signed: 'green',
    active: 'blue',
    completed: 'default',
    expired: 'red',
    terminated: 'orange',
    pending: 'gray',
  }
  return map[status] || 'default'
}
function statusLabel(status: string): string {
  const map: Record<string, string> = {
    signed: '已签订',
    active: '执行中',
    completed: '已完成',
    expired: '已到期',
    terminated: '已终止',
    pending: '待签订',
  }
  return map[status] || status
}

// 发票类型 / 状态 标签映射（兼容 DB 中文值 与 历史 'paid'）
function invoiceStatusText(status: string | null | undefined): string {
  if (status === '已回款' || status === 'paid') return '已回款'
  if (status === '已开') return '已开票'
  return status || '未知'
}
function invoiceStatusColor(status: string | null | undefined): string {
  if (status === '已回款' || status === 'paid') return 'green'
  if (status === '已开') return 'blue'
  return 'default'
}
function invoiceStatusAmountClass(status: string | null | undefined): string {
  if (status === '已回款' || status === 'paid') return 'text-green-600'
  if (status === '已开') return 'text-blue-600'
  return 'text-orange-500'
}
function invoiceTypeLabel(type: string | null | undefined): string {
  if (type === '客户回款') return '客户回款'
  if (type === '客户开票') return '客户开票'
  return type || '其他'
}
function invoiceTypeColor(type: string | null | undefined): string {
  return type === '客户回款' ? 'green' : 'blue'
}

// 文件图标和颜色
function fileIcon(fileType: string): string {
  if (!fileType) return 'file'
  const t = fileType.toLowerCase()
  if (t.includes('pdf')) return 'file-pdf'
  if (t.includes('doc') || t.includes('word')) return 'file-word'
  if (t.includes('xls') || t.includes('excel')) return 'file-excel'
  if (t.includes('ppt') || t.includes('powerpoint')) return 'file-ppt'
  if (t.includes('image') || t.includes('jpg') || t.includes('png')) return 'file-image'
  return 'file'
}
function fileColor(fileType: string): string {
  if (!fileType) return '#666'
  const t = fileType.toLowerCase()
  if (t.includes('pdf')) return '#ff4d4f'
  if (t.includes('doc') || t.includes('word')) return '#1890ff'
  if (t.includes('xls') || t.includes('excel')) return '#52c41a'
  if (t.includes('ppt') || t.includes('powerpoint')) return '#fa8c16'
  return '#666'
}
function formatSize(bytes: number): string {
  if (!bytes || bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i]
}

function downloadUrl(cid: string, fileId: string): string {
  return contractFileDownloadUrl(cid, fileId)
}

// 阶段数据质量检查
const hasValidStages = computed(() => {
  if (!stages.value.length) return false
  return stages.value.some((s: any) => s.start_time || s.end_time)
})
const validStages = computed(() => {
  return stages.value.filter((s: any) => s.start_time || s.end_time)
})

// 阶段详情表格列定义
const stageColumns = [
  { title: '阶段', key: 'stage_number', width: 130 },
  { title: '阶段内容', key: 'remarks', ellipsis: true },
  { title: '考核目标', key: 'acceptance_criteria', ellipsis: true },
  { title: '时间', key: 'time', width: 200 },
  { title: '状态', key: 'status', width: 80, align: 'center' as const },
]

// 解析验收标准文本：处理 Python list 格式或纯文本
function parseCriteriaText(criteria: string | null | undefined): string {
  if (!criteria) return ''
  const listMatch = criteria.match(/^\s*\[(.*)\]\s*$/s)
  if (listMatch) {
    const inner = listMatch[1] || ''
    const items = inner
      .split(/['"],\s*['"]/)
      .map((s) => s.replace(/^['"]|['"]$/g, '').trim())
      .filter(Boolean)
    return items.slice(0, 3).join('；') + (items.length > 3 ? ' ...' : '')
  }
  const text = criteria.trim()
  return text.length > 100 ? text.slice(0, 100) + '...' : text
}

// 从阶段数据中提取可读的时间范围（从 start_time 中解析结束部分补齐 end_time 为空的情况）
function extractStageTime(s: any): string {
  const raw = s.start_time || ''
  const end = s.end_time || ''
  if (!raw && !end) return '-'
  // 如果 start_time 包含 " — " 或 " 至 " 分段符，提取两端
  const cleaned = raw.replace(/(\d)\s+(?=\d)/g, '$1')
  const rangeMatch = cleaned.match(/^(.+?)\s*[—–至]\s*(.+)$/)
  if (rangeMatch) {
    return `${rangeMatch[1].trim()} ~ ${rangeMatch[2].trim()}`
  }
  if (end) return `${raw} ~ ${end}`
  return raw
}

const contractId = computed(() => (route.query.id as string) || c.value?.contract_id || '')

function fmt(n: number | null | undefined): string {
  if (n == null) return '0.00'
  return n.toFixed(2)
}
function fmtMoney(n: number | null | undefined): string {
  if (n == null) return '0.00'
  return n.toFixed(2)
}

// 付款数据结构化（DB 金额已统一为万元，不再需要除1万）
// 仅展示计划金额、付款条件/节点、状态；不臆造阶段↔付款、付款↔发票的关联
const paymentsView = computed(() => {
  return payments.value.map((p: any) => {
    const isPaid = p.status === 'paid' || p.status === 'completed' || p.status === '已支付'
    const plannedAmount = Number(p.planned_amount) || 0
    const statusLabel =
      p.status === 'paid' || p.status === '已支付'
        ? '已支付'
        : p.status === 'pending' || p.status === '待支付'
          ? '待支付'
          : p.status || '待支付'
    return {
      ...p,
      planned_amount: plannedAmount,
      isPaid,
      statusLabel,
    }
  })
})

// 付款汇总（仅计划总额，回款以 finance 为准）
const paymentsTotal = computed(() => {
  const planned = paymentsView.value.reduce((sum: number, p: any) => sum + (p.planned_amount || 0), 0)
  return { planned, paid: 0 }
})

// KPI: 已开票（来自 finance_records 快照，单位万元）
const invoiceTotal = computed(() => {
  const f = finance.value
  return f ? (Number(f.invoice_total) || 0) : 0
})

// KPI: 已回款（来自 finance_records 快照，单位万元）
const paymentTotal = computed(() => {
  const f = finance.value
  return f ? (Number(f.payment_total) || 0) : 0
})

// KPI: 未回款（来自 finance_records 快照，单位万元）
const unreceivedAmount = computed(() => {
  const f = finance.value
  return f ? (Number(f.payment_unreceived) || 0) : 0
})

// KPI: 开票率（invoice_total / contract_total，finance 口径）
const invoiceRate = computed(() => {
  const f = finance.value
  if (!f) return '0.0'
  const ct = Number(f.contract_total) || 0
  const it = Number(f.invoice_total) || 0
  return ct > 0 ? ((it / ct) * 100).toFixed(1) : '0.0'
})

// KPI: 回款率（payment_total / contract_total，finance 口径，保留 1 位小数）
const receiptRate = computed(() => {
  const f = finance.value
  if (!f) return '0.0'
  const ct = Number(f.contract_total) || 0
  const pt = Number(f.payment_total) || 0
  return ct > 0 ? ((pt / ct) * 100).toFixed(1) : '0.0'
})

// KPI: 按合同总额未回款 = contract_total - payment_total
const contractUnreceived = computed(() => {
  const f = finance.value
  if (!f) return 0
  return (Number(f.contract_total) || 0) - (Number(f.payment_total) || 0)
})

// KPI: 已开票未回款率 = payment_unreceived / invoice_total
const unreceivedRate = computed(() => {
  const f = finance.value
  if (!f) return '0.0'
  const it = Number(f.invoice_total) || 0
  const ur = Number(f.payment_unreceived) || 0
  return it > 0 ? ((ur / it) * 100).toFixed(1) : '0.0'
})

// KPI: 按合同总额未回款率 = contractUnreceived / contract_total
const contractUnreceivedRate = computed(() => {
  const f = finance.value
  if (!f) return '0.0'
  const ct = Number(f.contract_total) || 0
  const cu = contractUnreceived.value
  return ct > 0 ? ((cu / ct) * 100).toFixed(1) : '0.0'
})


// 清理文本
function clean(s: string | null | undefined): string {
  if (!s) return '-'
  return s.replace(/[\n\r]+/g, ' ').trim()
}

// 导航
function goBack() {
  router.push({ name: 'ContractList' })
}

// 文件上传前处理
function beforeUpload(file: File) {
  uploading.value = true
  uploadContractFileApi(contractId.value, file)
    .then(() => {
      message.success('文件上传成功')
      load()
    })
    .catch((err: any) => {
      message.error('文件上传失败: ' + (err?.message || '未知错误'))
    })
    .finally(() => {
      uploading.value = false
    })
  return false
}

async function load() {
  loading.value = true
  error.value = ''
  serviceExpanded.value = false
  try {
    detail.value = await getContractDetailApi(route.query.id as string)
    loadTeam() // 并行加载团队信息
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || '未知错误'
  } finally {
    loading.value = false
  }
}

onMounted(load)

// 监听路由参数变化，当合同ID变化时重新加载数据
watch(
  () => route.query.id,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      load()
      loadTeam()
    }
  },
  { immediate: false },
)
</script>

<style scoped>
.clause-item {
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fafafa;
  transition: background-color 0.2s;
}
.clause-item:hover {
  background: #f5f5f5;
}
.clause-text {
  margin-top: 8px;
  font-size: 13px;
  color: #6b7280;
  white-space: pre-wrap;
  line-height: 1.7;
}
</style>
