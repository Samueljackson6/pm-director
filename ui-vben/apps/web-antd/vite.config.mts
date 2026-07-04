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

// @ts-ignore - defineConfig 类型推断问题，不影响运行
export default defineConfig(async () => {
  return {
    application: {},
    vite: {
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
            // mock代理目标地址
            target: 'http://localhost:48080/admin-api',
            ws: true,
          },
        },
      },
      build: {
        rollupOptions: {
          external: [/^node:/, 'jiti'],
          plugins: [
            // 排除 asset 和 wms 目录
            excludeDirectoriesPlugin(),
            // 修复 ids 默认导出问题
            fixIdsDefaultExportPlugin(),
          ],
          external: ['jiti'],
        },
      },
    },
  };
});
