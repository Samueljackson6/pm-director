import { describe, expect, it } from 'vitest';

import { reviewContracts, reviewIssues, reviewSnapshot } from '../review-data';

describe('阶段3评审数据契约', () => {
  it('应将客户应收与供应商应付明确分轨', () => {
    const customerSteps: string[] = reviewSnapshot.customerLane.map(
      (step) => step.label,
    );
    const supplierSteps: string[] = reviewSnapshot.supplierLane.map(
      (step) => step.label,
    );
    const overlap = customerSteps.filter((step) =>
      supplierSteps.includes(step),
    );
    expect(overlap).toEqual([]);
    expect(customerSteps).toContain('客户回款');
    expect(supplierSteps).toContain('供应商付款');
  });

  it('应为合同样例提供来源与核验状态', () => {
    const contract = reviewContracts[0];
    const evidenceKinds = contract?.evidence.map((item) => item.kind);
    expect(evidenceKinds).toEqual(['original', 'text', 'parsed', 'verified']);
    expect(contract?.verificationStatus).toBe('needs_review');
  });

  it('应把历史 inbound 语义冲突放入核验队列', () => {
    const issue = reviewIssues.find(
      (item) => item.code === 'INBOUND_SEMANTICS',
    );
    expect(issue?.level).toBe('critical');
    expect(issue?.status).toBe('pending_review');
  });
});
