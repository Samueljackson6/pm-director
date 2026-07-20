import type { AppRouteRecordRaw } from '@vben-core/typings';

import { describe, expect, it } from 'vitest';

import { convertServerMenuToRouteRecordStringComponent } from '../generate-menus';

function createContractMenu(childPath: string): AppRouteRecordRaw[] {
  return [
    {
      children: [
        {
          component: 'contracts/list',
          id: 2,
          meta: { title: '合同台账' },
          name: 'ContractList',
          parentId: 1,
          path: childPath,
          visible: true,
        },
      ],
      component: 'BasicLayout',
      id: 1,
      meta: { title: '合同履约' },
      name: 'ContractManagement',
      parentId: 0,
      path: '/contracts',
      visible: true,
    },
  ];
}

describe('convertServerMenuToRouteRecordStringComponent', () => {
  it('为相对子路由拼接父路径', () => {
    // Given：相对路径由后端作为父菜单的子路由返回。
    const menuList = createContractMenu('list');

    // When：转换为 Vben 路由记录。
    const routes = convertServerMenuToRouteRecordStringComponent(menuList);

    // Then：子路由保留父菜单语义。
    expect(routes[0]?.children?.[0]?.path).toBe('/contracts/list');
  });

  it('保持绝对子路由而不重复拼接父路径', () => {
    // Given：项目台账作为跨分组绝对路径子项返回。
    const menuList = createContractMenu('/projects/list');

    // When：转换为 Vben 路由记录。
    const routes = convertServerMenuToRouteRecordStringComponent(menuList);

    // Then：绝对路径不能变成 /contracts//projects/list。
    expect(routes[0]?.children?.[0]?.path).toBe('/projects/list');
  });
});
