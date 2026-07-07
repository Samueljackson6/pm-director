import { fileURLToPath } from 'node:url';
import { defineConfig } from '@vben/vite-config';
import type { Plugin } from 'vite';

/**
 * 排除指定目录的插件
 * 在构建时排除 src/views/asset 和 src/views/wms 目录
 */
function excludeDirectoriesPlugin(): Plugin {
  return {
    name: 'exclude-directories',
    resolveId(id) {
      // 排除 asset 和 wms 目录下的所有文件
      if (
        id.includes('/src/views/asset/') ||
        id.includes('/src/views/wms/') ||
        id.includes('src/views/asset') ||
        id.includes('src/views/wms') ||
        id.includes('\\src\\views\\asset\\') ||
        id.includes('\\src\\views\\wms\\')
      ) {
        // 返回虚拟模块 ID，标记为外部模块
        return { id: '\0excluded', external: true };
      }
      return null;
    },
    load(id) {
      // 如果是排除的模块，返回空内容避免构建错误
      if (id === '\0excluded') {
        return 'export default {};';
      }
      return null;
    },
  };
}

/**
 * ids@3.0.1 使用命名导出 { Ids }，但 bpmn-js-token-simulation
 * 使用 import Ids from 'ids'（默认导入）。
 * 此插件在构建时为 ids 模块添加默认导出修复。
 */
function fixIdsDefaultExportPlugin(): Plugin {
  return {
    name: 'fix-ids-default-export',
    enforce: 'post',
    transform(code, id) {
      if (id.includes('ids/dist/index.js')) {
        return {
          code: code.replace(
            'export { Ids };',
            'export { Ids }; export default Ids;',
          ),
          map: null,
        };
      }
      return null;
    },
  };
}

/**
 * 将 `@vben-core/shared` 的子路径解析到其 TypeScript 源码，而不是预构建的
 * `dist` 产物。
 *
 * 背景：pm-director 仓库中 `@vben-core/shared` 的 `dist/*.mjs` 是由
 * `unbuild --stub` 生成的「加载器」——它们在模块顶层通过 jiti 动态加载
 * `src/*.ts` 并重新导出。生产构建时（NODE_ENV=production）Vite 解析
 * `exports.default` 条件命中这些 dist 加载器，从而把 Node 专属的 `jiti`
 * 拉入浏览器构建图，导致 rollup 因 `createRequire is not exported by
 * __vite-browser-external` 而崩溃。
 *
 * 这里把这些子路径直接别名到 `src` 下的真实源码（等价于 dev 模式下
 * `exports.development` 条件的行为），彻底绕开 jiti 加载器，既消除了
 * jiti 的浏览器依赖，也避免 dist 加载器里的顶层 await 在 es2015 目标下报错。
 */
function aliasSharedToSource(): { find: string; replacement: string }[] {
  const sharedRoot = fileURLToPath(
    new URL('../../packages/@core/base/shared/', import.meta.url),
  );
  const subpaths: Record<string, string> = {
    cache: 'src/cache/index.ts',
    color: 'src/color/index.ts',
    constants: 'src/constants/index.ts',
    'global-state': 'src/global-state.ts',
    store: 'src/store.ts',
    utils: 'src/utils/index.ts',
  };
  return Object.entries(subpaths).map(([sub, target]) => ({
    find: `@vben-core/shared/${sub}`,
    replacement: fileURLToPath(new URL(target, `file://${sharedRoot}`)),
  }));
}

// @ts-ignore - defineConfig 类型推断问题，不影响运行
export default defineConfig(async () => {
  return {
    application: {},
    vite: {
      resolve: {
        alias: aliasSharedToSource(),
      },
      optimizeDeps: {
        exclude: ['ids'],
      },
      // 生产环境部署到 /web 路径下
      css: {
        preprocessorOptions: {
          scss: {
            api: 'modern-compiler',
          },
        },
      },
      base: process.env.NODE_ENV === 'production' ? '/web/' : '/',
      server: {
        allowedHosts: true,
        proxy: {
          '/admin-api': {
            changeOrigin: true,
            rewrite: (path: string) => path.replace(/^\/admin-api/, ''),
            // 本地开发环境指向 pm-director 后端 (8800)
            target: 'http://localhost:8800',
            ws: true,
          },
        },
      },
      build: {
        rollupOptions: {
          plugins: [
            // 排除 asset 和 wms 目录
            excludeDirectoriesPlugin(),
            // 修复 ids 默认导出问题
            fixIdsDefaultExportPlugin(),
          ],
        },
      },
    },
  };
});
