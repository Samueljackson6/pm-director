<template>
  <div class="p-6 bg-gradient-to-b from-gray-50 to-gray-100 min-h-screen">
    <!-- ═══ 标题栏 ═══ -->
    <div class="max-w-6xl mx-auto space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <a-button type="text" class="flex items-center justify-center w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-100" @click="goBack">
            <span class="text-lg">←</span>
          </a-button>
          <div>
            <h1 class="text-xl font-semibold text-gray-800">{{ supplier?.supplier_name || '供应商详情' }}</h1>
            <p v-if="supplier" class="text-sm text-gray-400">
              {{ supplier.supplier_id }} · {{ supplier.credit_code || '无信用代码' }} · 首次合作 {{ supplier.first_cooperation_date || '未记录' }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <a-tag v-if="supplier" :color="supplier.status === 'active' ? 'green' : 'default'" class="rounded-full px-3 py-0.5 text-xs">
            {{ supplier.status === 'active' ? '合作中' : '已暂停' }}
          </a-tag>
          <a-button size="small" ghost @click="openAddInvoice">+ 发票</a-button>
          <a-button size="small" type="primary" @click="openAddPayment">+ 付款</a-button>
        </div>
      </div>

      <!-- ═══ 三态容器 ═══ -->
      <state-block :loading="loading" :error="error" error-title="供应商数据加载失败" @retry="load">
        <template v-if="supplier">

          <!-- ═══ KPI 指标行 ═══ -->
          <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
            <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
              <div class="text-xs text-gray-400 mb-1">合同总额（万元）</div>
              <div class="text-2xl font-bold text-gray-900">{{ fmtMoney(supplier.total_contract_amount) }}</div>
            </div>
            <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
              <div class="text-xs text-gray-400 mb-1">已开票（万元）</div>
              <div class="text-2xl font-bold text-blue-600">{{ fmtMoney(supplier.total_invoiced) }}</div>
              <div class="text-[10px] text-gray-400 mt-0.5">开票率 {{ invoiceRate }}%</div>
            </div>
            <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
              <div class="text-xs text-gray-400 mb-1">已付款（万元）</div>
              <div class="text-2xl font-bold text-green-600">{{ fmtMoney(supplier.total_paid) }}</div>
              <div class="text-[10px] text-gray-400 mt-0.5">付款率 {{ paymentRate }}%</div>
            </div>
            <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
              <div class="text-xs text-gray-400 mb-1">未付款（万元）</div>
              <div class="text-2xl font-bold text-orange-500">{{ fmtMoney(supplier.total_unpaid) }}</div>
              <div class="text-[10px] text-gray-400 mt-0.5">占总额 {{ unpaidRate }}%</div>
            </div>
            <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
              <div class="text-xs text-gray-400 mb-1">合作项目</div>
              <div class="text-2xl font-bold text-purple-600">{{ contracts.length }}</div>
              <div class="text-[10px] text-gray-400 mt-0.5">{{ activeContractCount }} 进行中</div>
            </div>
          </div>

          <!-- ═══ 吸顶锚点 ═══ -->
          <div class="sticky top-0 z-20 bg-white/85 backdrop-blur-sm border-y border-gray-200 -mx-6 px-6">
            <div class="flex gap-1 py-2 max-w-6xl mx-auto">
              <button v-for="a in anchors" :key="a.id" @click="scrollToAnchor(a.id)"
                :class="['px-3 py-1.5 text-sm rounded-md whitespace-nowrap transition-colors',
                         activeAnchor === a.id ? 'bg-blue-50 text-blue-600 font-medium' : 'text-gray-500 hover:bg-gray-100']">
                {{ a.label }}
              </button>
            </div>
          </div>

          <!-- ════════════════════════════════════════════════════════
               1. 企业信息（基础信息 + 企查查合并）
               ════════════════════════════════════════════════════════ -->
          <div id="info" class="bg-white rounded-lg border border-gray-200 overflow-hidden scroll-mt-16">
            <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
              <span class="w-1 h-4 rounded-full bg-blue-500"></span>
              <span class="text-sm font-semibold text-gray-700">企业信息</span>
              <span class="text-xs text-gray-400 font-normal ml-1">基础信息</span>
              <span class="ml-auto text-xs text-gray-400 bg-gray-100 rounded px-2 py-0.5">📡 数据来源：企查查</span>
            </div>
            <div class="px-5 py-4">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-y-4 gap-x-6">
                <div><div class="text-xs text-gray-400">供应商名称</div><div class="text-sm font-medium text-gray-900">{{ supplier.supplier_name }}</div></div>
                <div><div class="text-xs text-gray-400">简称</div><div class="text-sm text-gray-700">{{ supplier.short_name || '-' }}</div></div>
                <div><div class="text-xs text-gray-400">统一社会信用代码</div><div class="text-sm font-mono text-gray-700">{{ supplier.credit_code || '-' }}</div></div>
                <div><div class="text-xs text-gray-400">类别</div><div class="text-sm"><a-tag class="text-xs">{{ supplier.category || '未分类' }}</a-tag></div></div>

                <div><div class="text-xs text-gray-400">法定代表人</div><div class="text-sm text-gray-700">{{ qccBasic?.legalPerson || '-' }}</div></div>
                <div><div class="text-xs text-gray-400">注册资本</div><div class="text-sm text-gray-700">{{ qccBasic?.registeredCapital || '-' }}</div></div>
                <div><div class="text-xs text-gray-400">成立日期</div><div class="text-sm text-gray-700">{{ qccBasic?.establishDate || '-' }}</div></div>
                <div><div class="text-xs text-gray-400">企业状态</div><div class="text-sm" :style="{ color: qccBasic?.status === '存续' ? '#34c759' : '#ff9500' }">{{ qccBasic?.status || '-' }}</div></div>

                <div style="grid-column: span 2;">
                  <div class="text-xs text-gray-400">注册地址</div>
                  <div class="text-sm text-gray-700">{{ qccBasic?.address || '-' }}</div>
                </div>
                <div><div class="text-xs text-gray-400">首次合作</div><div class="text-sm text-gray-700">{{ supplier.first_cooperation_date || '-' }}</div></div>
                <div><div class="text-xs text-gray-400">联系人</div><div class="text-sm text-gray-700">{{ supplier.contact_person || '-' }} {{ supplier.contact_phone ? '/' + supplier.contact_phone : '' }}</div></div>
              </div>
              <div v-if="supplier.evaluation" class="mt-3 pt-3 border-t border-gray-100">
                <div class="text-xs text-gray-400 mb-1">评估备注</div>
                <div class="text-sm text-gray-600">{{ supplier.evaluation }}</div>
              </div>
              <div v-if="supplier.credit_code" class="mt-3 pt-3 border-t border-gray-100 flex gap-2">
                <a-button size="small" ghost @click="syncQcc">🔄 同步企查查</a-button>
                <a-button size="small" ghost @click="openQccDetail">📋 查看详情</a-button>
              </div>
            </div>
          </div>

          <!-- ════════════════════════════════════════════════════════
               2. 合作项目
               ════════════════════════════════════════════════════════ -->
          <div id="projects" class="bg-white rounded-lg border border-gray-200 overflow-hidden scroll-mt-16">
            <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
              <span class="w-1 h-4 rounded-full bg-teal-500"></span>
              <span class="text-sm font-semibold text-gray-700">合作项目</span>
              <span class="text-xs text-gray-400 font-normal ml-1">({{ contracts.length }}) · 总额 ¥{{ totalContractAmount }} 万</span>
            </div>
            <div class="px-5 py-4 space-y-3">
              <template v-if="contracts.length">
                <div v-for="c in contracts" :key="c.id" class="border border-gray-100 rounded-xl p-4 hover:border-blue-200 hover:shadow-sm transition-all">
                  <div class="flex items-start justify-between mb-3">
                    <div>
                      <div class="flex items-center gap-2">
                        <span class="text-sm font-semibold text-gray-900">{{ c.project_id }}</span>
                        <a-tag :color="c.status === 'active' ? 'blue' : 'green'" size="small">
                          {{ c.status === 'active' ? '进行中' : '已验收' }}
                        </a-tag>
                      </div>
                      <p class="text-sm text-gray-500 mt-0.5">{{ c.project_name || '' }}</p>
                    </div>
                    <router-link :to="{ name: 'ContractDetail', query: { id: c.project_id } }" class="text-xs text-blue-600 hover:underline shrink-0 mt-1">合同详情 →</router-link>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
                    <div>
                      <div class="text-xs text-gray-400">合同金额</div>
                      <div class="text-lg font-bold text-gray-900">{{ fmtMoney(c.contract_amount) }}</div>
                      <div class="text-xs text-gray-400">签约 {{ c.contract_date || '-' }}</div>
                    </div>
                    <div>
                      <div class="text-xs text-gray-400">已开票</div>
                      <div class="text-lg font-bold text-blue-600">{{ fmtMoney(c.invoice_total) }}</div>
                      <div class="text-xs text-gray-400">开票率 {{ calcRate(c.invoice_total, c.contract_amount) }}%</div>
                    </div>
                    <div>
                      <div class="text-xs text-gray-400">已付款</div>
                      <div class="text-lg font-bold text-green-600">{{ fmtMoney(c.payment_total) }}</div>
                      <div class="text-xs text-gray-400">未付款 {{ fmtMoney(c.unpaid) }} 万</div>
                    </div>
                  </div>

                  <div class="space-y-1.5">
                    <div class="flex justify-between text-xs text-gray-400"><span>开票进度</span><span>{{ calcRate(c.invoice_total, c.contract_amount) }}%</span></div>
                    <div class="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div class="h-full rounded-full transition-all" :style="{ width: calcRate(c.invoice_total, c.contract_amount) + '%', background: '#2563eb' }"></div>
                    </div>
                    <div class="flex justify-between text-xs text-gray-400 mt-1.5"><span>付款进度</span><span>{{ calcRate(c.payment_total, c.contract_amount) }}%</span></div>
                    <div class="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div class="h-full rounded-full transition-all" :style="{ width: calcRate(c.payment_total, c.contract_amount) + '%', background: '#34c759' }"></div>
                    </div>
                  </div>
                </div>
              </template>
              <a-empty v-else description="暂无合作项目" />
            </div>
          </div>

          <!-- ════════════════════════════════════════════════════════
               3. 往来账目（发票 + 付款 Tab 切换）
               ════════════════════════════════════════════════════════ -->
          <div id="finance" class="bg-white rounded-lg border border-gray-200 overflow-hidden scroll-mt-16">
            <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
              <span class="w-1 h-4 rounded-full bg-amber-500"></span>
              <span class="text-sm font-semibold text-gray-700">往来账目</span>
              <div class="ml-auto flex gap-1">
                <button :class="['px-3 py-1 text-xs rounded-md transition-colors', activeFinanceTab === 'invoice' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50']" @click="activeFinanceTab = 'invoice'">供应商发票</button>
                <button :class="['px-3 py-1 text-xs rounded-md transition-colors', activeFinanceTab === 'payment' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50']" @click="activeFinanceTab = 'payment'">付款记录</button>
              </div>
            </div>

            <!-- 发票 Tab -->
            <div v-show="activeFinanceTab === 'invoice'">
              <template v-if="paginatedInvoices.length">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="border-b border-gray-100 bg-gray-50/50">
                      <th class="text-left px-4 py-2.5 text-xs font-medium text-gray-500">发票号</th>
                      <th class="text-left px-4 py-2.5 text-xs font-medium text-gray-500">关联项目</th>
                      <th class="text-left px-4 py-2.5 text-xs font-medium text-gray-500">开票日期</th>
                      <th class="text-right px-4 py-2.5 text-xs font-medium text-gray-500">金额（元）</th>
                      <th class="text-right px-4 py-2.5 text-xs font-medium text-gray-500">税率</th>
                      <th class="text-center px-4 py-2.5 text-xs font-medium text-gray-500">状态</th>
                      <th class="text-center px-4 py-2.5 text-xs font-medium text-gray-500">付款</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="inv in paginatedInvoices" :key="inv.invoice_id" class="border-b border-gray-50 hover:bg-blue-50/30 cursor-pointer" @click="router.push({ name: 'InvoiceDetail', query: { id: inv.invoice_id } })">
                      <td class="px-4 py-3 font-mono text-xs text-blue-600">{{ inv.invoice_no || 'INV#' + inv.invoice_id }}</td>
                      <td class="px-4 py-3 text-gray-700">{{ inv.project_id }}</td>
                      <td class="px-4 py-3 text-gray-500">{{ inv.invoice_date || '-' }}</td>
                      <td class="px-4 py-3 text-right font-medium text-gray-900">{{ fmtAmount(inv.amount) }}</td>
                      <td class="px-4 py-3 text-right text-gray-500">{{ inv.tax_rate ? inv.tax_rate + '%' : '-' }}</td>
                      <td class="px-4 py-3 text-center">
                        <a-tag :color="inv.status === '已开' ? 'blue' : 'orange'" size="small">{{ inv.status || '待开' }}</a-tag>
                      </td>
                      <td class="px-4 py-3 text-center">
                        <a-tag :color="getInvoicePaymentStatus(inv).color" size="small">{{ getInvoicePaymentStatus(inv).label }}</a-tag>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div class="flex items-center justify-between px-4 py-2 border-t border-gray-50 text-xs text-gray-400">
                  <span>共 {{ invoices.length }} 条记录</span>
                  <div class="flex gap-1">
                    <button class="w-6 h-6 flex items-center justify-center rounded" :class="invoicePage === 1 ? 'text-gray-300' : 'text-gray-500 hover:bg-gray-100'" :disabled="invoicePage === 1" @click="invoicePage > 1 && invoicePage--">‹</button>
                    <button v-for="p in invoiceTotalPages" :key="p" @click="invoicePage = p"
                      :class="['w-6 h-6 flex items-center justify-center rounded text-xs', invoicePage === p ? 'bg-blue-600 text-white' : 'text-gray-500 hover:bg-gray-100']">{{ p }}</button>
                    <button class="w-6 h-6 flex items-center justify-center rounded" :class="invoicePage === invoiceTotalPages ? 'text-gray-300' : 'text-gray-500 hover:bg-gray-100'" :disabled="invoicePage === invoiceTotalPages" @click="invoicePage < invoiceTotalPages && invoicePage++">›</button>
                  </div>
                </div>
              </template>
              <a-empty v-else description="暂无供应商发票" class="my-8" />
            </div>

            <!-- 付款 Tab -->
            <div v-show="activeFinanceTab === 'payment'">
              <template v-if="payments.length">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="border-b border-gray-100 bg-gray-50/50">
                      <th class="text-left px-4 py-2.5 text-xs font-medium text-gray-500">付款编号</th>
                      <th class="text-left px-4 py-2.5 text-xs font-medium text-gray-500">关联项目</th>
                      <th class="text-left px-4 py-2.5 text-xs font-medium text-gray-500">付款日期</th>
                      <th class="text-right px-4 py-2.5 text-xs font-medium text-gray-500">金额（元）</th>
                      <th class="text-left px-4 py-2.5 text-xs font-medium text-gray-500">付款方式</th>
                      <th class="text-center px-4 py-2.5 text-xs font-medium text-gray-500">状态</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="pay in payments" :key="pay.payment_id" class="border-b border-gray-50 hover:bg-green-50/30">
                      <td class="px-4 py-3 font-mono text-xs text-gray-500">PAY-{{ pay.payment_id }}</td>
                      <td class="px-4 py-3 text-gray-700">{{ pay.project_id || '-' }}</td>
                      <td class="px-4 py-3 text-gray-500">{{ pay.payment_date || '-' }}</td>
                      <td class="px-4 py-3 text-right font-medium text-gray-900">{{ fmtAmount(pay.amount) }}</td>
                      <td class="px-4 py-3 text-gray-600">{{ pay.payment_method || '银行转账' }}</td>
                      <td class="px-4 py-3 text-center">
                        <a-tag :color="pay.status === '已完成' ? 'green' : 'orange'" size="small">{{ pay.status || '待支付' }}</a-tag>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </template>
              <a-empty v-else description="暂无付款记录" class="my-8" />
            </div>
          </div>

          <!-- ════════════════════════════════════════════════════════
               4. 联系人
               ════════════════════════════════════════════════════════ -->
          <div id="contacts" class="bg-white rounded-lg border border-gray-200 overflow-hidden scroll-mt-16">
            <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
              <span class="w-1 h-4 rounded-full bg-purple-500"></span>
              <span class="text-sm font-semibold text-gray-700">联系人</span>
              <span class="text-xs text-gray-400 font-normal ml-1">({{ contacts.length }})</span>
              <a-button size="small" type="link" class="ml-auto" @click="openAddContact">+ 添加</a-button>
            </div>
            <div class="px-5 py-4">
              <template v-if="contacts.length">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div v-for="c in contacts" :key="c.id" class="relative border border-gray-100 rounded-lg p-4 hover:border-blue-200 hover:shadow-sm transition-all"
                    :class="{ 'ring-1 ring-blue-100': c.is_primary }">
                    <div v-if="c.is_primary" class="absolute top-3 right-3 text-[10px] text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded font-medium">主要</div>
                    <div class="flex items-center gap-3 mb-2">
                      <div class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
                        :style="{ background: contactColor(c.name), color: '#fff' }">{{ c.name.charAt(0) }}</div>
                      <div>
                        <div class="font-medium text-gray-900 text-sm">{{ c.name }}</div>
                        <div class="text-xs text-gray-400">{{ c.position || '-' }}</div>
                      </div>
                    </div>
                    <div class="text-xs text-gray-500 space-y-0.5 ml-[52px]">
                      <div>📞 {{ c.phone || '-' }}</div>
                      <div>✉️ {{ c.email || '-' }}</div>
                    </div>
                    <div class="mt-2 pt-2 border-t border-gray-50 flex gap-2 justify-end">
                      <a-button size="small" type="link" @click="openEditContact(c)">编辑</a-button>
                      <a-popconfirm title="确定删除此联系人？" ok-text="确定" cancel-text="取消" @confirm="deleteContact(c)">
                        <a-button size="small" type="link" danger>删除</a-button>
                      </a-popconfirm>
                    </div>
                  </div>
                </div>
              </template>
              <a-empty v-else description="暂未添加联系人" />
            </div>
          </div>

        </template>
      </state-block>
    </div>

    <!-- ═══ 新增发票弹窗 ═══ -->
    <a-modal v-model:open="addInvoiceVisible" title="新增供应商发票" :confirm-loading="invoiceSaving" @ok="saveInvoice" ok-text="保存" cancel-text="取消" width="560px">
      <a-form :model="invoiceForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12"><a-form-item label="项目编号" required><a-input v-model:value="invoiceForm.project_id" placeholder="如：ZH02-202601001" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="发票号"><a-input v-model:value="invoiceForm.invoice_no" placeholder="可选" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="发票日期" required><a-date-picker v-model:value="invoiceForm.invoice_date" value-format="YYYY-MM-DD" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="金额（元）" required><a-input-number v-model:value="invoiceForm.amount" :precision="2" :min="0" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="税率（%）"><a-input-number v-model:value="invoiceForm.tax_rate" :precision="2" :min="0" :max="100" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="状态"><a-select v-model:value="invoiceForm.status"><a-select-option value="已开">已开</a-select-option><a-select-option value="待开">待开</a-select-option></a-select></a-form-item></a-col>
          <a-col :span="24"><a-form-item label="备注"><a-textarea v-model:value="invoiceForm.notes" :rows="2" /></a-form-item></a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- ═══ 新增付款弹窗 ═══ -->
    <a-modal v-model:open="addPaymentVisible" title="新增付款记录" :confirm-loading="paymentSaving" @ok="savePayment" ok-text="保存" cancel-text="取消" width="560px">
      <a-form :model="paymentForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12"><a-form-item label="项目编号" required><a-input v-model:value="paymentForm.project_id" placeholder="如：ZH02-202601001" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="付款日期" required><a-date-picker v-model:value="paymentForm.payment_date" value-format="YYYY-MM-DD" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="付款金额（元）" required><a-input-number v-model:value="paymentForm.amount" :precision="2" :min="0" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="付款方式"><a-select v-model:value="paymentForm.payment_method"><a-select-option value="银行转账">银行转账</a-select-option><a-select-option value="现金">现金</a-select-option><a-select-option value="支票">支票</a-select-option></a-select></a-form-item></a-col>
          <a-col :span="24"><a-form-item label="备注"><a-textarea v-model:value="paymentForm.notes" :rows="2" /></a-form-item></a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- ═══ 新增/编辑联系人弹窗 ═══ -->
    <a-modal v-model:open="contactModalVisible" :title="editingContact ? '编辑联系人' : '添加联系人'" :confirm-loading="contactSaving" @ok="saveContact" ok-text="保存" cancel-text="取消" width="480px">
      <a-form :model="contactForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12"><a-form-item label="姓名" required><a-input v-model:value="contactForm.name" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="职位"><a-input v-model:value="contactForm.position" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="电话"><a-input v-model:value="contactForm.phone" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="邮箱"><a-input v-model:value="contactForm.email" /></a-form-item></a-col>
          <a-col :span="24"><a-form-item label="备注"><a-textarea v-model:value="contactForm.notes" :rows="2" /></a-form-item></a-col>
          <a-col :span="24"><a-form-item><a-checkbox v-model:checked="contactForm.is_primary">设为主要联系人</a-checkbox></a-form-item></a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- ═══ 企查查详情弹窗 ═══ -->
    <a-modal v-model:open="qccDetailVisible" title="企查查数据详情" :footer="null" width="700px">
      <div v-if="qccData" class="space-y-4">
        <div v-if="qccData.basic_info" class="bg-gray-50 rounded-lg p-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-2">工商信息</h4>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div v-for="(v, k) in qccData.basic_info" :key="k">
              <span class="text-xs text-gray-400 block">{{ k }}</span>
              <span class="text-gray-700">{{ v ?? '-' }}</span>
            </div>
          </div>
        </div>
        <div v-if="qccData.risk_scan" class="bg-gray-50 rounded-lg p-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-2">风险扫描</h4>
          <pre class="text-xs text-gray-600 whitespace-pre-wrap">{{ JSON.stringify(qccData.risk_scan, null, 2) }}</pre>
        </div>
        <div v-if="qccData.software_copyrights" class="bg-gray-50 rounded-lg p-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-2">软件著作权（{{ qccData.software_copyrights.length || 0 }} 项）</h4>
          <div v-if="qccData.software_copyrights.length" class="space-y-1">
            <div v-for="s in qccData.software_copyrights" :key="s.id || s.name" class="text-xs text-gray-600 py-1 border-b border-gray-200 last:border-0">{{ s.name || s.software_name }} · {{ s.reg_number || '-' }}</div>
          </div>
        </div>
        <div v-if="qccData.profile" class="bg-gray-50 rounded-lg p-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-2">企业简介</h4>
          <p class="text-sm text-gray-600">{{ qccData.profile.introduction || qccData.profile.summary || '暂无简介' }}</p>
        </div>
      </div>
      <a-empty v-else description="暂无企查查数据，请先同步" />
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getSupplierDetailApi, createContactApi, updateContactApi, deleteContactApi } from '#/api/suppliers'
import { createInvoiceApi } from '#/api/invoices'
import { requestClient } from '#/api/request'
import StateBlock from '#/components/state-block/index.vue'

const route = useRoute()
const router = useRouter()

// ── 核心数据 ──
const supplier = ref<any>(null)
const contracts = ref<any[]>([])
const invoices = ref<any[]>([])
const payments = ref<any[]>([])
const contacts = ref<any[]>([])
const qccData = ref<any>(null)
const loading = ref(true)
const error = ref('')

// ── 锚点导航 ──
const anchors = [
  { id: 'info', label: '企业信息' },
  { id: 'projects', label: '合作项目' },
  { id: 'finance', label: '往来账目' },
  { id: 'contacts', label: '联系人' },
]
const activeAnchor = ref('info')
let anchorObserver: IntersectionObserver | null = null

function scrollToAnchor(id: string) {
  const el = document.getElementById(id)
  if (!el) return
  const y = el.getBoundingClientRect().top + window.pageYOffset - 56
  window.scrollTo({ top: y, behavior: 'smooth' })
}

// ── Tab ──
const activeFinanceTab = ref<'invoice' | 'payment'>('invoice')

// ── 发票分页 ──
const invoicePage = ref(1)
const INVOICE_PAGE_SIZE = 10
const paginatedInvoices = computed(() => {
  const start = (invoicePage.value - 1) * INVOICE_PAGE_SIZE
  return invoices.value.slice(start, start + INVOICE_PAGE_SIZE)
})
const invoiceTotalPages = computed(() => Math.max(1, Math.ceil(invoices.value.length / INVOICE_PAGE_SIZE)))
watch(invoices, () => { invoicePage.value = 1 })

// ── 计算指标 ──
const totalContractAmount = computed(() => contracts.value.reduce((s, c) => s + (c.contract_amount || 0), 0).toFixed(2))
const activeContractCount = computed(() => contracts.value.filter((c: any) => c.status === 'active').length)

const invoiceRate = computed(() => calcRate(supplier.value?.total_invoiced, supplier.value?.total_contract_amount))
const paymentRate = computed(() => calcRate(supplier.value?.total_paid, supplier.value?.total_contract_amount))
const unpaidRate = computed(() => calcRate(supplier.value?.total_unpaid, supplier.value?.total_contract_amount))

const qccBasic = computed(() => qccData.value?.basic_info || null)

// ── 发票付款状态 ──
function getInvoicePaymentStatus(inv: any): { label: string; color: string } {
  const projectPayments = payments.value.filter((p: any) => p.project_id === inv.project_id)
  if (!projectPayments.length) return { label: '待付', color: 'orange' }
  const totalPaid = projectPayments.reduce((s: number, p: any) => s + (p.amount || 0), 0)
  if (totalPaid >= (inv.amount || 0)) return { label: '已付', color: 'green' }
  return { label: '部分付款', color: 'orange' }
}

// ── 工具函数 ──
function fmtMoney(n: number | null | undefined): string {
  if (n == null) return '0.00'
  return n.toFixed(2)
}
function fmtAmount(n: number | null | undefined): string {
  if (n == null) return '0.00'
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
function calcRate(value: number | null | undefined, total: number | null | undefined): string {
  if (!total || !value) return '0'
  return ((value / total) * 100).toFixed(1)
}
function contactColor(name: string): string {
  const colors = ['#2563eb', '#16a34a', '#9333ea', '#ea580c', '#0891b2', '#dc2626']
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

// ── 加载数据 ──
async function load() {
  loading.value = true
  error.value = ''
  try {
    const id = route.params.id || route.query.id
    const data: any = await getSupplierDetailApi(id as string)
    supplier.value = data.supplier ?? null
    contracts.value = data.contracts || []
    invoices.value = data.invoices || []
    payments.value = data.payments || []
    contacts.value = data.contacts || []
    qccData.value = data.qcc_data || null
    if (!supplier.value) error.value = '未找到该供应商'
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || '未知错误'
  } finally {
    loading.value = false
  }
}

// ── 锚点 IntersectionObserver ──
watch(() => supplier.value, () => {
  nextTick(() => {
    anchorObserver?.disconnect()
    anchorObserver = new IntersectionObserver(
      entries => {
        entries.forEach(e => {
          if (e.isIntersecting) activeAnchor.value = (e.target as HTMLElement).id
        })
      },
      { rootMargin: '-56px 0px -70% 0px' },
    )
    anchors.forEach(a => {
      const el = document.getElementById(a.id)
      if (el) anchorObserver?.observe(el)
    })
  })
}, { flush: 'post' })
onUnmounted(() => anchorObserver?.disconnect())

// ── 新增发票 ──
const addInvoiceVisible = ref(false)
const invoiceSaving = ref(false)
const invoiceForm = ref<Record<string, any>>({})
function openAddInvoice() {
  invoiceForm.value = { project_id: '', invoice_no: '', invoice_date: '', invoice_type: '供应商开票', direction: 'inbound', amount: null, tax_rate: null, status: '已开', notes: '' }
  addInvoiceVisible.value = true
}
async function saveInvoice() {
  if (!invoiceForm.value.project_id) { message.error('请输入项目编号'); return }
  invoiceSaving.value = true
  try {
    await createInvoiceApi({ ...invoiceForm.value, supplier_id: supplier.value?.supplier_id })
    message.success('发票创建成功')
    addInvoiceVisible.value = false
    load()
  } catch (e: any) {
    message.error('创建失败: ' + (e?.message || '未知错误'))
  } finally { invoiceSaving.value = false }
}

// ── 新增付款 ──
const addPaymentVisible = ref(false)
const paymentSaving = ref(false)
const paymentForm = ref<Record<string, any>>({})
function openAddPayment() {
  paymentForm.value = { project_id: '', payment_date: '', amount: null, payment_method: '银行转账', status: '已完成', notes: '' }
  addPaymentVisible.value = true
}
async function savePayment() {
  if (!paymentForm.value.project_id) { message.error('请输入项目编号'); return }
  if (!paymentForm.value.amount) { message.error('请输入付款金额'); return }
  paymentSaving.value = true
  try {
    await requestClient.post('/api/supplier-payments', { ...paymentForm.value, supplier_id: supplier.value?.supplier_id })
    message.success('付款记录创建成功')
    addPaymentVisible.value = false
    load()
  } catch (e: any) {
    message.error('创建失败: ' + (e?.message || '未知错误'))
  } finally { paymentSaving.value = false }
}

// ── 联系人 CRUD ──
const contactModalVisible = ref(false)
const contactSaving = ref(false)
const editingContact = ref<any>(null)
const contactForm = ref<Record<string, any>>({})

function openAddContact() {
  editingContact.value = null
  contactForm.value = { name: '', position: '', phone: '', email: '', is_primary: false, notes: '' }
  contactModalVisible.value = true
}
function openEditContact(c: any) {
  editingContact.value = c
  contactForm.value = { name: c.name, position: c.position || '', phone: c.phone || '', email: c.email || '', is_primary: !!c.is_primary, notes: c.notes || '' }
  contactModalVisible.value = true
}
async function saveContact() {
  if (!contactForm.value.name) { message.error('请输入联系人姓名'); return }
  contactSaving.value = true
  try {
    const sid = supplier.value?.supplier_id
    const payload = { ...contactForm.value, is_primary: contactForm.value.is_primary ? 1 : 0 }
    if (editingContact.value) {
      await updateContactApi(sid, editingContact.value.id, payload)
      message.success('联系人已更新')
    } else {
      await createContactApi(sid, payload)
      message.success('联系人已添加')
    }
    contactModalVisible.value = false
    load()
  } catch (e: any) {
    message.error('保存失败: ' + (e?.message || '未知错误'))
  } finally { contactSaving.value = false }
}
async function deleteContact(c: any) {
  try {
    await deleteContactApi(supplier.value?.supplier_id, c.id)
    message.success('联系人已删除')
    load()
  } catch (e: any) {
    message.error('删除失败: ' + (e?.message || '未知错误'))
  }
}

// ── QCC 同步 ──
const qccDetailVisible = ref(false)
async function syncQcc() {
  const code = supplier.value?.credit_code
  if (!code) { message.warning('该供应商无信用代码'); return }
  try {
    await requestClient.post(`/api/suppliers/sync/${code}`)
    message.success('同步成功')
    load()
  } catch (e: any) {
    message.error('同步失败: ' + (e?.message || '未知错误'))
  }
}
function openQccDetail() {
  qccDetailVisible.value = true
}

// ── 初始化 ──
onMounted(load)
watch(
  () => route.params.id || route.query.id,
  (newId, oldId) => { if (newId && newId !== oldId) load() },
  { immediate: false },
)

function goBack() {
  router.push({ name: 'SupplierList' })
}
</script>

<style scoped>
.text-lg { font-size: 1.125rem; }
.w-full { width: 100%; }
.scroll-mt-16 { scroll-margin-top: 64px; }
</style>
