import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getDashboardOverviewApi } from '#/api/dashboard';
import type { DashboardOverview } from '#/api/dashboard';

vi.mock('#/api/request', () => ({
  requestClient: {
    get: vi.fn(),
  },
}));

import { requestClient } from '#/api/request';

const mockOverview: DashboardOverview = {
  generated_at: '2026-07-07T00:00:00Z',
  filters: { period: 'all', from: null, to: null, project_type: null },
  summary: {
    contract_count: 50,
    contract_total_amount: 2364.79,
    invoiced_amount: 1049.13,
    received_amount: 707.15,
    unreceived_amount: 847.61,
    receipt_rate: 67.4,
    uninvoiced_amount: 1315.66,
    sub_invoiced_amount: 399.96,
    sub_paid_amount: 287.03,
    currency_unit: '万元',
  },
  contracts_by_type: [
    { project_type: '服务类', count: 37, amount: 1621.9 },
    { project_type: '科研类', count: 10, amount: 667.49 },
  ],
  contracts_by_status: [
    { contract_status: 'signed', count: 50, amount: 2364.79 },
  ],
  invoice_status_distribution: [
    { status: '已回款', count: 25, amount_wan: 477.14 },
    { status: '已开', count: 46, amount_wan: 1004.32 },
  ],
  invoice_monthly: [
    { month: '2024-09', invoiced_wan: 49.83, received_wan: 0 },
    { month: '2024-10', invoiced_wan: 65.3, received_wan: 18.03 },
  ],
  finance_trend: [
    {
      batch_id: '2026-W26',
      import_time: '2026-06-30T00:00:00Z',
      invoiced_wan: 1049.13,
      received_wan: 707.15,
    },
  ],
  top_customers: [
    { customer: '四川蜀能电科', count: 1, total_amount: 496.6 },
  ],
  pending_tasks: {
    unmatched_payments: 71,
    pending_deliverables: 120,
    overdue_payments: 0,
    uninvoiced_contracts: 30,
  },
  recent_contracts: [
    {
      contract_id: 'ZH02-202602014',
      project_name: '测试项目',
      contract_amount: 28.62,
      party_a: '甲方',
      sign_date: '2026-02-23',
      project_type: '服务类',
      contract_status: 'signed',
      invoice_total: 14.31,
      payment_total: 0,
    },
  ],
};

describe('getDashboardOverviewApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('调用了 /api/dashboard/overview 端点并返回已解包的 data', async () => {
    (requestClient.get as any).mockResolvedValue(mockOverview);

    const result = await getDashboardOverviewApi();

    expect(requestClient.get).toHaveBeenCalledWith('/api/dashboard/overview', {
      params: undefined,
    });
    expect(result).toBe(mockOverview);

    // 断言关键字段映射正确
    expect(result.summary.invoiced_amount).toBe(1049.13);
    expect(result.summary.received_amount).toBe(707.15);
    expect(result.summary.receipt_rate).toBe(67.4);
    expect(result.summary.currency_unit).toBe('万元');
    expect(Array.isArray(result.contracts_by_type)).toBe(true);
    expect(result.contracts_by_type[0].project_type).toBe('服务类');
    expect(Array.isArray(result.invoice_status_distribution)).toBe(true);
    expect(Array.isArray(result.finance_trend)).toBe(true);
    expect(Array.isArray(result.top_customers)).toBe(true);
    expect(result.pending_tasks.unmatched_payments).toBe(71);
    expect(Array.isArray(result.recent_contracts)).toBe(true);
  });

  it('把 query 参数转发给 request', async () => {
    (requestClient.get as any).mockResolvedValue(mockOverview);

    const params = { period: 'all', project_type: '科研类' };
    await getDashboardOverviewApi(params);

    expect(requestClient.get).toHaveBeenCalledWith('/api/dashboard/overview', {
      params,
    });
  });
});
