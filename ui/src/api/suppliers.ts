import { baseRequestClient } from '#/api/request'
export function getSuppliersApi() { return baseRequestClient.get('/suppliers') }
