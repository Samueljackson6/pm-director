import { describe, expect, it } from 'vitest';

import {
  buildDetailLocation,
  buildListReturnLocation,
  parseDetailId,
} from '../business-navigation';

describe('列表与详情导航上下文', () => {
  it('列表进入详情时携带来源、筛选条件和分页，并可完整恢复', () => {
    const detailLocation = buildDetailLocation({
      from: {
        name: 'ProjectList',
        query: {
          page: '3',
          pageSize: '50',
          search: '国网',
          status: 'active',
          type: 'service',
        },
      },
      id: 'PRJ-001',
      name: 'ProjectDetail',
    });

    expect(detailLocation).toEqual({
      name: 'ProjectDetail',
      query: {
        from: 'ProjectList',
        id: 'PRJ-001',
        return_page: '3',
        return_pageSize: '50',
        return_search: '国网',
        return_status: 'active',
        return_type: 'service',
      },
    });

    expect(
      buildListReturnLocation({
        currentDetailName: 'ProjectDetail',
        detailQuery: detailLocation.query,
        fallbackName: 'ProjectList',
      }),
    ).toEqual({
      name: 'ProjectList',
      query: {
        page: '3',
        pageSize: '50',
        search: '国网',
        status: 'active',
        type: 'service',
      },
    });
  });

  it('缺失、空白或多值 ID 返回稳定错误态', () => {
    expect(parseDetailId({})).toEqual({ reason: 'missing', status: 'invalid' });
    expect(parseDetailId({ id: '   ' })).toEqual({
      reason: 'missing',
      status: 'invalid',
    });
    expect(parseDetailId({ id: ['PRJ-001', 'PRJ-002'] })).toEqual({
      reason: 'multiple',
      status: 'invalid',
    });
    expect(parseDetailId({ id: 'PRJ-001' })).toEqual({
      id: 'PRJ-001',
      status: 'ready',
    });
  });

  it('非法来源不能把返回动作指向当前详情页形成循环', () => {
    expect(
      buildListReturnLocation({
        currentDetailName: 'ProjectDetail',
        detailQuery: {
          from: 'ProjectDetail',
          id: '',
          return_page: '2',
        },
        fallbackName: 'ProjectList',
      }),
    ).toEqual({
      name: 'ProjectList',
      query: { page: '2' },
    });
  });
});
