export interface InvoiceRecord {
  readonly invoice_id: number;
  readonly invoice_no?: string;
  readonly project_id?: number | string;
  readonly project_name?: string;
  readonly customer_name?: string;
  readonly direction?: string;
  readonly invoice_type?: string;
  readonly invoice_date?: string;
  readonly status?: string;
  readonly payment_status?: string;
  readonly received_date?: string;
  readonly amount?: number | null;
  readonly tax_rate?: number | null;
  readonly tax_amount?: number | null;
  readonly total_with_tax?: number | null;
  readonly source?: string;
  readonly created_at?: string;
  readonly updated_at?: string;
  readonly import_time?: string;
  readonly notes?: string;
}

export interface InvoiceReceipt {
  readonly receipt_id: number;
  readonly receipt_no?: string;
  readonly receipt_date?: string;
  readonly receipt_method?: string;
  readonly amount?: number;
  readonly link_amount?: number;
}

export interface InvoiceFile {
  readonly file_id: number;
  readonly file_name: string;
  readonly file_type?: string;
  readonly file_size?: number;
}

export interface InvoiceEditForm {
  invoice_no: string;
  invoice_date: string;
  amount: number | null;
  tax_rate: number | null;
  tax_amount: number | null;
  total_with_tax: number | null;
  status: string;
  received_date: string;
  notes: string;
}

export interface ParsedInvoiceNotes {
  readonly contractNo: string;
  readonly invoiceType: string;
  readonly invoiceDate: string;
  readonly status: string;
  readonly matchStatus: string;
  readonly source: string;
  readonly processTime: string;
}

export interface InvoiceOverviewProps {
  readonly invoice: InvoiceRecord;
  readonly parsedNotes: ParsedInvoiceNotes | null;
  readonly calculatedTaxAmount: number | null;
  readonly total_with_tax: number | null;
  readonly fmtMoney: (value: number | null | undefined) => string;
  readonly statusColor: (value: string | undefined) => string;
  readonly paymentStatusColor: (value: string | undefined) => string;
  readonly invoiceTypeColor: (value: string | undefined) => string;
}
