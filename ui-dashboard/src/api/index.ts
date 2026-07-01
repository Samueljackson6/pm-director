import axios from 'axios'
const api = axios.create({ baseURL: '/api', timeout: 15000 })

export interface Stats { contract_count: number; total_amount: number; invoiced: number; received: number; receipt_rate: number; stages: number; payments: number; deliverables: number; sub_invoiced: number; sub_paid: number }

export const getStats = () => api.get<Stats>('/stats').then(r => r.data)
export const getContracts = (page = 1, size = 20, search = '', sort = 'amount_desc') =>
  api.get('/contracts', { params: { page, size, search, sort } }).then(r => r.data)
export const getContract = (id: string) => api.get('/contracts/' + id).then(r => r.data)
export const getInvoices = (projectId = '', page = 1, size = 50) =>
  api.get('/invoices', { params: { project_id: projectId, page, size } }).then(r => r.data)
export const getInvoiceSummary = () => api.get('/invoices/summary').then(r => r.data)
export const getSuppliers = () => api.get('/suppliers').then(r => r.data)
export const getSupplier = (id: string) => api.get('/suppliers/' + id).then(r => r.data)
export const getTypeDistribution = () => api.get('/stats/types').then(r => r.data)
export const getDbSummary = () => api.get('/db/summary').then(r => r.data)
