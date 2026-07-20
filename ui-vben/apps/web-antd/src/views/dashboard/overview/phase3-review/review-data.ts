export type ContractId = {
  readonly kind: 'contract-id';
  readonly value: string;
};

export type EvidenceItem = {
  readonly kind: 'original' | 'parsed' | 'text' | 'verified';
  readonly label: string;
  readonly note: string;
  readonly status: 'available' | 'needs_review' | 'verified';
};

export type ReviewContract = {
  readonly amountLabel: string;
  readonly contractId: ContractId;
  readonly deliveryType: '服务类' | '物资类' | '科研类';
  readonly evidence: readonly EvidenceItem[];
  readonly legalForm: string;
  readonly partyA: string;
  readonly paymentPattern: string;
  readonly projectName: string;
  readonly rowKey: number;
  readonly stateGridId: string;
  readonly verificationStatus: 'needs_review' | 'verified';
};

export type ReviewIssue = {
  readonly action: string;
  readonly code:
    | 'INBOUND_SEMANTICS'
    | 'MISSING_SGSC'
    | 'RECEIPT_MATCH'
    | 'STAGE_PAYMENT_LINK';
  readonly count: number;
  readonly description: string;
  readonly level: 'critical' | 'warning';
  readonly status: 'pending_review';
  readonly title: string;
};

export const reviewSnapshot = {
  capturedAt: '2026-07-15 只读快照',
  source: 'SQLite 聚合 + 合同规则文档',
  metrics: [
    {
      key: 'contracts',
      label: '当前合同',
      value: '45',
      note: '服务 32 · 科研 10 · 未分类 3',
      tone: 'cyan',
    },
    {
      key: 'missing-sgsc',
      label: '缺少 SGSC 编号',
      value: '16',
      note: '必须保留内部编号与来源',
      tone: 'amber',
    },
    {
      key: 'semantic-conflicts',
      label: '回款语义待迁移',
      value: '34',
      note: '历史 inbound 实为客户回款',
      tone: 'rose',
    },
    {
      key: 'supplier-payments',
      label: '供应商付款事实',
      value: '0',
      note: '不得展示成熟应付闭环',
      tone: 'slate',
    },
  ],
  customerLane: [
    { label: '合同约定', status: 'verified' },
    { label: '阶段与成果', status: 'partial' },
    { label: '验收/考核', status: 'needs_review' },
    { label: '客户开票', status: 'partial' },
    { label: '客户回款', status: 'partial' },
    { label: '质保金回款', status: 'needs_review' },
  ],
  supplierLane: [
    { label: '供应商合同', status: 'partial' },
    { label: '供应商交付', status: 'needs_review' },
    { label: '供应商发票', status: 'blocked' },
    { label: '付款审批', status: 'blocked' },
    { label: '供应商付款', status: 'blocked' },
  ],
} as const;

export const reviewContracts: readonly ReviewContract[] = [
  {
    rowKey: 1,
    contractId: { kind: 'contract-id', value: 'ZH02-2026-DEMO-01' },
    stateGridId: 'SGSC-DEMO-KY-01',
    projectName: '国网科研项目合同（脱敏评审样例）',
    legalForm: '技术服务合同',
    deliveryType: '科研类',
    partyA: '国网四川某分支机构（脱敏）',
    amountLabel: '待核验 · 万元',
    paymentPattern: '研究阶段 N:1 → 付款节点待确认',
    verificationStatus: 'needs_review',
    evidence: [
      {
        kind: 'original',
        label: 'PDF 原件',
        note: '法律与审计源头真值',
        status: 'available',
      },
      {
        kind: 'text',
        label: 'OCR DOCX',
        note: '派生文本层，可重新生成',
        status: 'available',
      },
      {
        kind: 'parsed',
        label: '结构化抽取',
        note: '付款阶段存在 N:1 候选关系',
        status: 'needs_review',
      },
      {
        kind: 'verified',
        label: '人工核验',
        note: '3 个关键字段仍待确认',
        status: 'needs_review',
      },
    ],
  },
  {
    rowKey: 2,
    contractId: { kind: 'contract-id', value: 'ZH02-2026-DEMO-02' },
    stateGridId: '待补充',
    projectName: '国网技术服务合同（脱敏评审样例）',
    legalForm: '技术服务合同',
    deliveryType: '服务类',
    partyA: '国网四川某供电单位（脱敏）',
    amountLabel: '已核验 · 万元',
    paymentPattern: '验收款 97% + 质保金 3%（业务修正规则）',
    verificationStatus: 'needs_review',
    evidence: [
      {
        kind: 'original',
        label: 'PDF 原件',
        note: '付款原文为验收后支付',
        status: 'available',
      },
      {
        kind: 'text',
        label: 'OCR DOCX',
        note: '日期存在 OCR 噪声',
        status: 'needs_review',
      },
      {
        kind: 'parsed',
        label: '结构化抽取',
        note: '97% + 3% 为业务规则补充',
        status: 'needs_review',
      },
      {
        kind: 'verified',
        label: '人工核验',
        note: '保留原值与采用值差异',
        status: 'verified',
      },
    ],
  },
  {
    rowKey: 3,
    contractId: { kind: 'contract-id', value: 'ZH02-2026-DEMO-03' },
    stateGridId: 'SGSC-DEMO-WZ-01',
    projectName: '国网物资购销合同（脱敏评审样例）',
    legalForm: '产品购销合同',
    deliveryType: '物资类',
    partyA: '国网四川某单位（脱敏）',
    amountLabel: '待核验 · 万元',
    paymentPattern: '到货/验收/发票复合条件，比例待确认',
    verificationStatus: 'needs_review',
    evidence: [
      {
        kind: 'original',
        label: 'PDF 原件',
        note: '付款条款页面不完整',
        status: 'available',
      },
      {
        kind: 'text',
        label: 'OCR DOCX',
        note: '缺少完整付款段落',
        status: 'needs_review',
      },
      {
        kind: 'parsed',
        label: '结构化抽取',
        note: '无法可靠推断比例',
        status: 'needs_review',
      },
      {
        kind: 'verified',
        label: '人工核验',
        note: '需要补扫合同页',
        status: 'needs_review',
      },
    ],
  },
];

export const reviewIssues: readonly ReviewIssue[] = [
  {
    code: 'INBOUND_SEMANTICS',
    title: '客户回款与供应商发票语义冲突',
    description:
      '34 条 inbound 记录实际是历史客户回款，迁移前禁止进入供应商发票页面。',
    level: 'critical',
    count: 34,
    status: 'pending_review',
    action: '建立迁移批次并逐条核对 receipts',
  },
  {
    code: 'MISSING_SGSC',
    title: '国网正式编号缺失',
    description: '保留内部编号，不用项目名称猜测覆盖。',
    level: 'warning',
    count: 16,
    status: 'pending_review',
    action: '从原件首页和映射表生成候选',
  },
  {
    code: 'RECEIPT_MATCH',
    title: '客户回款尚未完成发票匹配',
    description: '自动匹配只能生成候选，必须保留人工确认边界。',
    level: 'warning',
    count: 9,
    status: 'pending_review',
    action: '对比付款方、金额、日期和项目编号',
  },
  {
    code: 'STAGE_PAYMENT_LINK',
    title: '阶段与付款计划缺少事实关联',
    description: '当前关联表为 0，禁止按数组顺序硬配。',
    level: 'critical',
    count: 84,
    status: 'pending_review',
    action: '按合同原文生成 N:M 候选并复核',
  },
];
