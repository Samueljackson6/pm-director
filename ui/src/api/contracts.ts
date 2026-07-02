import { baseRequestClient } from '#/api/request'
export function getContractsApi(params?: any) { return baseRequestClient.get('/contracts', { params }) }
export function getContractDetailApi(id: string) { return baseRequestClient.get('/contracts/' + id) }
export function getStatsApi() { return baseRequestClient.get('/stats') }
export function getTypesApi() { return baseRequestClient.get('/stats/types') }
