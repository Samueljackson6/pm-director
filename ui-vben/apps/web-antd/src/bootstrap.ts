import { createApp, watchEffect } from 'vue';
import VueDOMPurifyHTML from 'vue-dompurify-html';

import { registerAccessDirective } from '@vben/access';
import { registerLoadingDirective } from '@vben/common-ui/es/loading';
import { preferences } from '@vben/preferences';
import { initStores } from '@vben/stores';
import '@vben/styles';
import '@vben/styles/antd';

import { useTitle } from '@vueuse/core';

import { $t, setupI18n } from '#/locales';
import { setupFormCreate } from '#/plugins/form-create';

import { initComponentAdapter } from './adapter/component';
import { initSetupVbenForm } from './adapter/form';
import App from './app.vue';
import { router } from './router';

import './styles/custom-menu.css';
import './styles/antd-theme.css';
import './styles/finance-tokens.css';

async function bootstrap(namespace: string) {
  // 初始化组件适配器
  await initComponentAdapter();

  // 初始化表单组件
  await initSetupVbenForm();

  // // 设置弹窗的默认配置
  // setDefaultModalProps({
  //   fullscreenButton: false,
  // });
  // // 设置抽屉的默认配置
  // setDefaultDrawerProps({
  //   zIndex: 1020,
  // });

  const app = createApp(App);
  app.use(VueDOMPurifyHTML);

  // 注册v-loading指令
  registerLoadingDirective(app, {
    loading: 'loading', // 在这里可以自定义指令名称，也可以明确提供false表示不注册这个指令
    spinning: 'spinning',
  });

  // 国际化 i18n 配置
  await setupI18n(app);

  // 配置 pinia-store
  await initStores(app, { namespace });

  // 安装权限指令
  registerAccessDirective(app);

  // 初始化 tippy
  const { initTippy } = await import('@vben/common-ui/es/tippy');
  initTippy(app);

  // 如果已登录，预生成动态路由（避免在路由守卫中生成导致死循环）
  const { useAccessStore } = await import('@vben/stores');
  const accessStore = useAccessStore();
  if (accessStore.accessToken && !accessStore.isAccessChecked) {
    try {
      const { generateAccess } = await import('#/router/access');
      const { useUserStore } = await import('@vben/stores');
      const userStore = useUserStore();
      if (!userStore.userInfo) {
        const { useAuthStore } = await import('#/store');
        const authStore = useAuthStore();
        await authStore.fetchUserInfo();
      }
      await generateAccess({
        roles: userStore.userRoles ?? [],
        router,
        routes: (await import('#/router/routes')).accessRoutes,
      });
      accessStore.setIsAccessChecked(true);
    } catch (e) {
      console.error('Pre-generate routes failed:', e);
    }
  }

  // 配置路由及路由守卫
  app.use(router);

  // formCreate
  setupFormCreate(app);

  // 配置Motion插件
  const { MotionPlugin } = await import('@vben/plugins/motion');
  app.use(MotionPlugin);

  // 动态更新标题
  watchEffect(() => {
    if (preferences.app.dynamicTitle) {
      const routeTitle = router.currentRoute.value.meta?.title;
      const pageTitle =
        (routeTitle ? `${$t(routeTitle)} - ` : '') + preferences.app.name;
      useTitle(pageTitle);
    }
  });

  app.mount('#app');
}

export { bootstrap };
