import type { Router } from "vue-router";
import { LOGIN_PATH } from "@vben/constants";
import { preferences } from "@vben/preferences";
import { useAccessStore, useDictStore, useUserStore } from "@vben/stores";
import { startProgress, stopProgress } from "@vben/utils";
import { message } from "ant-design-vue";
import { getSimpleDictDataList } from "#/api/system/dict/data";
import { accessRoutes, coreRouteNames } from "#/router/routes";
import { useAuthStore } from "#/store";
import { generateAccess } from "./access";

function findFirstMenuPath(menus: any[]): string | null {
  if (!menus || menus.length === 0) {
    return null;
  }
  const first = menus[0];
  if (first.children && first.children.length > 0) {
    return findFirstMenuPath(first.children);
  }
  return first.path || null;
}

function setupCommonGuard(router: Router) {
  const loadedPaths = new Set<string>();
  router.beforeEach((to) => {
    to.meta.loaded = loadedPaths.has(to.path);
    if (!to.meta.loaded && preferences.transition.progress) {
      startProgress();
    }
    return true;
  });
  router.afterEach((to) => {
    loadedPaths.add(to.path);
    if (preferences.transition.progress) {
      stopProgress();
    }
  });
}

function setupAccessGuard(router: Router) {
  router.beforeEach(async (to, from) => {
    const accessStore = useAccessStore();
    const userStore = useUserStore();
    const authStore = useAuthStore();
    const dictStore = useDictStore();
    if (coreRouteNames.includes(to.name as string)) {
      if (to.path === LOGIN_PATH && accessStore.accessToken) {
        return decodeURIComponent(
          (to.query?.redirect as string) ||
            userStore.userInfo?.homePath ||
            findFirstMenuPath(accessStore.accessMenus) ||
            preferences.app.defaultHomePath,
        );
      }
      return true;
    }
    if (!accessStore.accessToken) {
      if (to.meta.ignoreAccess) {
        return true;
      }
      if (to.fullPath !== LOGIN_PATH) {
        return {
          path: LOGIN_PATH,
          query:
            (to.fullPath === preferences.app.defaultHomePath || to.fullPath === "/")
              ? {}
              : { redirect: encodeURIComponent(to.fullPath) },
          replace: true,
        };
      }
      return to;
    }
    if (accessStore.isAccessChecked) {
      return true;
    }
    dictStore.setDictCacheByApi(getSimpleDictDataList);
    let userInfo = userStore.userInfo;
    if (!userInfo) {
      const loading = message.loading({ content: "Loading menu..." });
      try {
        const authPermissionInfo = await authStore.fetchUserInfo();
        if (authPermissionInfo) {
          userInfo = authPermissionInfo.user;
        }
      } finally {
        loading();
      }
    }
    const userRoles = userStore.userRoles ?? [];
    const { accessibleMenus, accessibleRoutes } = await generateAccess({
      roles: userRoles,
      router,
      routes: accessRoutes,
    });
    accessStore.setAccessMenus(accessibleMenus);
    accessStore.setAccessRoutes(accessibleRoutes);
    accessStore.setIsAccessChecked(true);
    userStore.setUserRoles(userRoles);
    const redirectPath = (from.query.redirect ??
      (to.path === preferences.app.defaultHomePath
        ? userInfo?.homePath || findFirstMenuPath(accessibleMenus) || preferences.app.defaultHomePath
        : to.fullPath)) as string;
    return {
      ...router.resolve(decodeURIComponent(redirectPath)),
      replace: true,
    };
  });
}

function createRouterGuard(router: Router) {
  setupCommonGuard(router);
  setupAccessGuard(router);
}

export { createRouterGuard };
