export interface SupplierBasicInfo {
  readonly 企业名称?: string;
  readonly 统一社会信用代码?: string;
  readonly 法定代表人?: string;
  readonly 企业类型?: string;
  readonly 纳税人资质?: string;
  readonly 营业期限?: string;
  readonly 注册资本?: string;
  readonly 实缴资本?: string;
  readonly 成立日期?: string;
  readonly 参保人数?: number | string;
  readonly 人员规模?: string;
  readonly 登记状态?: string;
  readonly 注册地址?: string;
  readonly 经营范围?: string;
}

export interface SupplierLocalQccBasicInfo {
  readonly company_name?: string;
  readonly legal_representative?: string;
  readonly insured_count?: number | string;
  readonly registered_capital?: string;
  readonly paid_capital?: string;
  readonly business_status?: string;
  readonly company_type?: string;
  readonly taxpayer_qualification?: string;
  readonly personnel_scale?: string;
  readonly industry?: string;
  readonly registration_capital?: string;
  readonly paid_in_capital?: string;
  readonly establishment_date?: string;
  readonly registration_status?: string;
  readonly business_scope?: string;
  readonly registered_address?: string;
  readonly credit_code?: string;
}

export interface SupplierProfile { readonly 简介?: string; readonly 企查查行业?: string; }
export interface SupplierRiskFactor { readonly 风险因子: string; readonly 条目数: number; }
export interface SupplierRiskScan { readonly 有记录因子数?: number; readonly 无记录因子数?: number; readonly 风险因子扫描?: readonly SupplierRiskFactor[]; }
export interface SupplierLocalRiskScan { readonly risk_factors_count?: number; readonly clean_factors_count?: number; readonly risk_factors_json?: string; readonly 风险因子扫描?: readonly SupplierRiskFactor[]; }
export interface SupplierSoftwareCopyright { readonly 软件全称?: string; readonly 登记号?: string; readonly 登记日期?: string; }
export interface SupplierExternalInvestment { readonly 被投资企业名称: string; readonly 成立日期?: string; readonly 状态?: string; readonly 持股比例?: string; readonly '认缴出资额/持股数'?: string; }

export interface SupplierQccResponse {
  readonly basic_info?: SupplierBasicInfo;
  readonly profile?: SupplierProfile;
  readonly risk_scan?: SupplierRiskScan;
  readonly software_copyrights?: { readonly 软件著作权信息?: readonly SupplierSoftwareCopyright[]; };
  readonly external_investments?: { readonly 对外投资信息?: readonly SupplierExternalInvestment[]; };
}

export interface SupplierDetailResponse {
  readonly supplier?: Record<string, unknown>;
  readonly contracts?: readonly Record<string, unknown>[];
  readonly supplier_invoices?: readonly Record<string, unknown>[];
  readonly invoices?: readonly Record<string, unknown>[];
  readonly payments?: readonly Record<string, unknown>[];
  readonly contacts?: readonly Record<string, unknown>[];
  readonly data_states?: Record<string, string>;
  readonly qcc_data?: {
    readonly basic_info?: SupplierBasicInfo | SupplierLocalQccBasicInfo;
    readonly profile?: SupplierProfile | { readonly profile?: string; readonly qcc_industry?: string } | null;
    readonly risk_scan?: SupplierRiskScan | SupplierLocalRiskScan | null;
    readonly software_copyrights?: { readonly 软件著作权信息?: readonly Record<string, unknown>[]; readonly items?: readonly Record<string, unknown>[]; };
    readonly external_investments?: { readonly 对外投资信息?: readonly Record<string, unknown>[]; readonly items?: readonly Record<string, unknown>[]; };
  } | null;
}
