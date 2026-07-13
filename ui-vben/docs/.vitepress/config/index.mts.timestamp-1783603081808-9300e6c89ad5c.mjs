// .vitepress/config/index.mts
import { withPwa } from "file:///D:/Tare-workspace/pm-director/ui-vben/node_modules/.pnpm/@vite-pwa+vitepress@1.1.0_v_25916404174e35ce18c212cec78a3b27/node_modules/@vite-pwa/vitepress/dist/index.mjs";
import { defineConfigWithTheme } from "file:///D:/Tare-workspace/pm-director/ui-vben/node_modules/.pnpm/vitepress@1.6.4_@algolia+cl_ca1b2c338c9dbcf77a1bd5b615fbecff/node_modules/vitepress/dist/node/index.js";

// .vitepress/config/en.mts
import { defineConfig } from "file:///D:/Tare-workspace/pm-director/ui-vben/node_modules/.pnpm/vitepress@1.6.4_@algolia+cl_ca1b2c338c9dbcf77a1bd5b615fbecff/node_modules/vitepress/dist/node/index.js";

// ../package.json
var version = "5.5.9";

// .vitepress/config/en.mts
var en = defineConfig({
  description: "Vben Admin & Enterprise level management system framework",
  lang: "en-US",
  themeConfig: {
    darkModeSwitchLabel: "Theme",
    darkModeSwitchTitle: "Switch to Dark Mode",
    docFooter: {
      next: "Next Page",
      prev: "Previous Page"
    },
    editLink: {
      pattern: "https://github.com/vbenjs/vue-vben-admin/edit/main/docs/src/:path",
      text: "Edit this page on GitHub"
    },
    footer: {
      copyright: `Copyright \xA9 2020-${(/* @__PURE__ */ new Date()).getFullYear()} Vben`,
      message: "Released under the MIT License."
    },
    langMenuLabel: "Language",
    lastUpdated: {
      formatOptions: {
        dateStyle: "short",
        timeStyle: "medium"
      },
      text: "Last updated on"
    },
    lightModeSwitchTitle: "Switch to Light Mode",
    nav: nav(),
    outline: {
      label: "Navigate"
    },
    returnToTopLabel: "Back to top",
    sidebar: {
      "/en/commercial/": {
        base: "/en/commercial/",
        items: sidebarCommercial()
      },
      "/en/guide/": { base: "/en/guide/", items: sidebarGuide() }
    }
  }
});
function sidebarGuide() {
  return [
    {
      collapsed: false,
      text: "Introduction",
      items: [
        {
          link: "introduction/vben",
          text: "About Vben Admin"
        },
        {
          link: "introduction/why",
          text: "Why Choose Us?"
        },
        { link: "introduction/quick-start", text: "Quick Start" },
        { link: "introduction/thin", text: "Lite Version" }
      ]
    },
    {
      text: "Basics",
      items: [
        { link: "essentials/concept", text: "Basic Concepts" },
        { link: "essentials/development", text: "Local Development" },
        { link: "essentials/route", text: "Routing and Menu" },
        { link: "essentials/settings", text: "Configuration" },
        { link: "essentials/icons", text: "Icons" },
        { link: "essentials/styles", text: "Styles" },
        { link: "essentials/external-module", text: "External Modules" },
        { link: "essentials/build", text: "Build and Deployment" },
        { link: "essentials/server", text: "Server Interaction and Data Mock" }
      ]
    },
    {
      text: "Advanced",
      items: [
        { link: "in-depth/login", text: "Login" },
        { link: "in-depth/theme", text: "Theme" },
        { link: "in-depth/access", text: "Access Control" },
        { link: "in-depth/locale", text: "Internationalization" },
        { link: "in-depth/features", text: "Common Features" },
        { link: "in-depth/check-updates", text: "Check Updates" },
        { link: "in-depth/loading", text: "Global Loading" },
        { link: "in-depth/ui-framework", text: "UI Framework Switching" }
      ]
    },
    {
      text: "Engineering",
      items: [
        { link: "project/standard", text: "Standards" },
        { link: "project/cli", text: "CLI" },
        { link: "project/dir", text: "Directory Explanation" },
        { link: "project/test", text: "Unit Testing" },
        { link: "project/tailwindcss", text: "Tailwind CSS" },
        { link: "project/changeset", text: "Changeset" },
        { link: "project/vite", text: "Vite Config" }
      ]
    },
    {
      text: "Others",
      items: [
        { link: "other/project-update", text: "Project Update" },
        { link: "other/remove-code", text: "Remove Code" },
        { link: "other/faq", text: "FAQ" }
      ]
    }
  ];
}
function sidebarCommercial() {
  return [
    {
      link: "community",
      text: "Community"
    },
    {
      link: "technical-support",
      text: "Technical-support"
    },
    {
      link: "customized",
      text: "Customized"
    }
  ];
}
function nav() {
  return [
    {
      activeMatch: "^/en/(guide|components)/",
      text: "Doc",
      items: [
        {
          activeMatch: "^/en/guide/",
          link: "/en/guide/introduction/vben",
          text: "Guide"
        },
        // {
        //   activeMatch: '^/en/components/',
        //   link: '/en/components/introduction',
        //   text: 'Components',
        // },
        {
          text: "Historical Versions",
          items: [
            {
              link: "https://doc.vvbin.cn",
              text: "2.x Version Documentation"
            }
          ]
        }
      ]
    },
    {
      text: "Demo",
      items: [
        {
          text: "Vben Admin",
          items: [
            {
              link: "https://www.vben.pro",
              text: "Demo Version"
            },
            {
              link: "https://ant.vben.pro",
              text: "Ant Design Vue Version"
            },
            {
              link: "https://naive.vben.pro",
              text: "Naive Version"
            },
            {
              link: "https://ele.vben.pro",
              text: "Element Plus Version"
            }
          ]
        },
        {
          text: "Others",
          items: [
            {
              link: "https://vben.vvbin.cn",
              text: "Vben Admin 2.x"
            }
          ]
        }
      ]
    },
    {
      text: version,
      items: [
        {
          link: "https://github.com/vbenjs/vue-vben-admin/releases",
          text: "Changelog"
        },
        {
          link: "https://github.com/orgs/vbenjs/projects/5",
          text: "Roadmap"
        },
        {
          link: "https://github.com/vbenjs/vue-vben-admin/blob/main/.github/contributing.md",
          text: "Contribution"
        }
      ]
    },
    {
      link: "/commercial/technical-support",
      text: "\u{1F984} Tech Support"
    },
    {
      link: "/sponsor/personal",
      text: "\u2728 Sponsor"
    },
    {
      link: "/commercial/community",
      text: "\u{1F468}\u200D\u{1F466}\u200D\u{1F466} Community"
    }
    // {
    //   link: '/friend-links/',
    //   text: '🤝 Friend Links',
    // },
  ];
}

// .vitepress/config/shared.mts
import { resolve } from "node:path";
import {
  viteArchiverPlugin,
  viteVxeTableImportsPlugin
} from "file:///D:/Tare-workspace/pm-director/ui-vben/internal/vite-config/dist/index.mjs";
import {
  GitChangelog,
  GitChangelogMarkdownSection
} from "file:///D:/Tare-workspace/pm-director/ui-vben/node_modules/.pnpm/@nolebase+vitepress-plugin-_2552fc68d68bd05d44decb5564feb72d/node_modules/@nolebase/vitepress-plugin-git-changelog/dist/vite/index.mjs";
import tailwind from "file:///D:/Tare-workspace/pm-director/ui-vben/node_modules/.pnpm/tailwindcss@3.4.19_yaml@2.9.0/node_modules/tailwindcss/lib/index.js";
import { defineConfig as defineConfig3, postcssIsolateStyles } from "file:///D:/Tare-workspace/pm-director/ui-vben/node_modules/.pnpm/vitepress@1.6.4_@algolia+cl_ca1b2c338c9dbcf77a1bd5b615fbecff/node_modules/vitepress/dist/node/index.js";
import {
  groupIconMdPlugin,
  groupIconVitePlugin
} from "file:///D:/Tare-workspace/pm-director/ui-vben/node_modules/.pnpm/vitepress-plugin-group-icon_040f59f59022cc63244c7dfb07974949/node_modules/vitepress-plugin-group-icons/dist/index.mjs";

// .vitepress/config/plugins/demo-preview.ts
import crypto from "node:crypto";
import { readdirSync } from "node:fs";
import { join } from "node:path";
var rawPathRegexp = (
  // eslint-disable-next-line regexp/no-super-linear-backtracking, regexp/strict
  /^(.+?(?:\.([\da-z]+))?)(#[\w-]+)?(?: ?{(\d+(?:[,-]\d+)*)? ?(\S+)?})? ?(?:\[(.+)])?$/
);
function rawPathToToken(rawPath) {
  const [
    filepath = "",
    extension = "",
    region = "",
    lines = "",
    lang = "",
    rawTitle = ""
  ] = (rawPathRegexp.exec(rawPath) || []).slice(1);
  const title = rawTitle || filepath.split("/").pop() || "";
  return { extension, filepath, lang, lines, region, title };
}
var demoPreviewPlugin = (md) => {
  md.core.ruler.after("inline", "demo-preview", (state) => {
    const insertComponentImport = (importString) => {
      const index = state.tokens.findIndex(
        (i) => i.type === "html_block" && i.content.match(/<script setup>/g)
      );
      if (index === -1) {
        const importComponent = new state.Token("html_block", "", 0);
        importComponent.content = `<script setup>
${importString}
</script>
`;
        state.tokens.splice(0, 0, importComponent);
      } else {
        if (state.tokens[index]) {
          const content = state.tokens[index].content;
          state.tokens[index].content = content.replace(
            "</script>",
            `${importString}
</script>`
          );
        }
      }
    };
    const regex = /<DemoPreview[^>]*\sdir="([^"]*)"/g;
    state.src = state.src.replaceAll(regex, (_match, dir) => {
      const componentDir = join(process.cwd(), "src", dir).replaceAll(
        "\\",
        "/"
      );
      let childFiles = [];
      let dirExists = true;
      try {
        childFiles = readdirSync(componentDir, {
          encoding: "utf8",
          recursive: false,
          withFileTypes: false
        }) || [];
      } catch {
        dirExists = false;
      }
      if (!dirExists) {
        return "";
      }
      const uniqueWord = generateContentHash(componentDir);
      const ComponentName = `DemoComponent_${uniqueWord}`;
      insertComponentImport(
        `import ${ComponentName} from '${componentDir}/index.vue'`
      );
      const { path: _path } = state.env;
      const index = state.tokens.findIndex((i) => i.content.match(regex));
      if (!state.tokens[index]) {
        return "";
      }
      const firstString = "index.vue";
      childFiles = childFiles.toSorted((a, b) => {
        if (a === firstString) return -1;
        if (b === firstString) return 1;
        return a.localeCompare(b, "en", { sensitivity: "base" });
      });
      state.tokens[index].content = `<DemoPreview files="${encodeURIComponent(JSON.stringify(childFiles))}" ><${ComponentName}/>
        `;
      const _dummyToken = new state.Token("", "", 0);
      const tokenArray = [];
      childFiles.forEach((filename) => {
        const templateStart = new state.Token("html_inline", "", 0);
        templateStart.content = `<template #${filename}>`;
        tokenArray.push(templateStart);
        const resolvedPath = join(componentDir, filename);
        const { extension, filepath, lang, lines, title } = rawPathToToken(resolvedPath);
        const token = new state.Token("fence", "code", 0);
        token.info = `${lang || extension}${lines ? `{${lines}}` : ""}${title ? `[${title}]` : ""}`;
        token.content = `<<< ${filepath}`;
        token.src = [resolvedPath];
        tokenArray.push(token);
        const templateEnd = new state.Token("html_inline", "", 0);
        templateEnd.content = "</template>";
        tokenArray.push(templateEnd);
      });
      const endTag = new state.Token("html_inline", "", 0);
      endTag.content = "</DemoPreview>";
      tokenArray.push(endTag);
      state.tokens.splice(index + 1, 0, ...tokenArray);
      return "";
    });
  });
};
function generateContentHash(input, length = 10) {
  const hash = crypto.createHash("sha256").update(input).digest("hex");
  return Number.parseInt(hash, 16).toString(36).slice(0, length);
}

// .vitepress/config/zh.mts
import { defineConfig as defineConfig2 } from "file:///D:/Tare-workspace/pm-director/ui-vben/node_modules/.pnpm/vitepress@1.6.4_@algolia+cl_ca1b2c338c9dbcf77a1bd5b615fbecff/node_modules/vitepress/dist/node/index.js";
var zh = defineConfig2({
  description: "Vben Admin & \u4F01\u4E1A\u7EA7\u7BA1\u7406\u7CFB\u7EDF\u6846\u67B6",
  lang: "zh-Hans",
  themeConfig: {
    darkModeSwitchLabel: "\u4E3B\u9898",
    darkModeSwitchTitle: "\u5207\u6362\u5230\u6DF1\u8272\u6A21\u5F0F",
    docFooter: {
      next: "\u4E0B\u4E00\u9875",
      prev: "\u4E0A\u4E00\u9875"
    },
    editLink: {
      pattern: "https://github.com/vbenjs/vue-vben-admin/edit/main/docs/src/:path",
      text: "\u5728 GitHub \u4E0A\u7F16\u8F91\u6B64\u9875\u9762"
    },
    footer: {
      copyright: `Copyright \xA9 2020-${(/* @__PURE__ */ new Date()).getFullYear()} Vben`,
      message: "\u57FA\u4E8E MIT \u8BB8\u53EF\u53D1\u5E03."
    },
    langMenuLabel: "\u591A\u8BED\u8A00",
    lastUpdated: {
      formatOptions: {
        dateStyle: "short",
        timeStyle: "medium"
      },
      text: "\u6700\u540E\u66F4\u65B0\u4E8E"
    },
    lightModeSwitchTitle: "\u5207\u6362\u5230\u6D45\u8272\u6A21\u5F0F",
    nav: nav2(),
    outline: {
      label: "\u9875\u9762\u5BFC\u822A"
    },
    returnToTopLabel: "\u56DE\u5230\u9876\u90E8",
    sidebar: {
      "/commercial/": { base: "/commercial/", items: sidebarCommercial2() },
      "/components/": { base: "/components/", items: sidebarComponents() },
      "/guide/": { base: "/guide/", items: sidebarGuide2() }
    },
    sidebarMenuLabel: "\u83DC\u5355"
  }
});
function sidebarGuide2() {
  return [
    {
      collapsed: false,
      text: "\u7B80\u4ECB",
      items: [
        {
          link: "introduction/vben",
          text: "\u5173\u4E8E Vben Admin"
        },
        {
          link: "introduction/why",
          text: "\u4E3A\u4EC0\u4E48\u9009\u62E9\u6211\u4EEC?"
        },
        { link: "introduction/quick-start", text: "\u5FEB\u901F\u5F00\u59CB" },
        { link: "introduction/thin", text: "\u7CBE\u7B80\u7248\u672C" },
        {
          base: "/",
          link: "components/introduction",
          text: "\u7EC4\u4EF6\u6587\u6863"
        }
      ]
    },
    {
      text: "\u57FA\u7840",
      items: [
        { link: "essentials/concept", text: "\u57FA\u7840\u6982\u5FF5" },
        { link: "essentials/development", text: "\u672C\u5730\u5F00\u53D1" },
        { link: "essentials/route", text: "\u8DEF\u7531\u548C\u83DC\u5355" },
        { link: "essentials/settings", text: "\u914D\u7F6E" },
        { link: "essentials/icons", text: "\u56FE\u6807" },
        { link: "essentials/styles", text: "\u6837\u5F0F" },
        { link: "essentials/external-module", text: "\u5916\u90E8\u6A21\u5757" },
        { link: "essentials/build", text: "\u6784\u5EFA\u4E0E\u90E8\u7F72" },
        { link: "essentials/server", text: "\u670D\u52A1\u7AEF\u4EA4\u4E92\u4E0E\u6570\u636EMock" }
      ]
    },
    {
      text: "\u6DF1\u5165",
      items: [
        { link: "in-depth/login", text: "\u767B\u5F55" },
        // { link: 'in-depth/layout', text: '布局' },
        { link: "in-depth/theme", text: "\u4E3B\u9898" },
        { link: "in-depth/access", text: "\u6743\u9650" },
        { link: "in-depth/locale", text: "\u56FD\u9645\u5316" },
        { link: "in-depth/features", text: "\u5E38\u7528\u529F\u80FD" },
        { link: "in-depth/check-updates", text: "\u68C0\u67E5\u66F4\u65B0" },
        { link: "in-depth/loading", text: "\u5168\u5C40loading" },
        { link: "in-depth/ui-framework", text: "\u7EC4\u4EF6\u5E93\u5207\u6362" }
      ]
    },
    {
      text: "\u5DE5\u7A0B",
      items: [
        { link: "project/standard", text: "\u89C4\u8303" },
        { link: "project/cli", text: "CLI" },
        { link: "project/dir", text: "\u76EE\u5F55\u8BF4\u660E" },
        { link: "project/test", text: "\u5355\u5143\u6D4B\u8BD5" },
        { link: "project/tailwindcss", text: "Tailwind CSS" },
        { link: "project/changeset", text: "Changeset" },
        { link: "project/vite", text: "Vite Config" }
      ]
    },
    {
      text: "\u5176\u4ED6",
      items: [
        { link: "other/project-update", text: "\u9879\u76EE\u66F4\u65B0" },
        { link: "other/remove-code", text: "\u79FB\u9664\u4EE3\u7801" },
        { link: "other/faq", text: "\u5E38\u89C1\u95EE\u9898" }
      ]
    }
  ];
}
function sidebarCommercial2() {
  return [
    {
      link: "community",
      text: "\u4EA4\u6D41\u7FA4"
    },
    {
      link: "technical-support",
      text: "\u6280\u672F\u652F\u6301"
    },
    {
      link: "customized",
      text: "\u5B9A\u5236\u5F00\u53D1"
    }
  ];
}
function sidebarComponents() {
  return [
    {
      text: "\u7EC4\u4EF6",
      items: [
        {
          link: "introduction",
          text: "\u4ECB\u7ECD"
        }
      ]
    },
    {
      collapsed: false,
      text: "\u5E03\u5C40\u7EC4\u4EF6",
      items: [
        {
          link: "layout-ui/page",
          text: "Page \u9875\u9762"
        }
      ]
    },
    {
      collapsed: false,
      text: "\u901A\u7528\u7EC4\u4EF6",
      items: [
        {
          link: "common-ui/vben-api-component",
          text: "ApiComponent Api\u7EC4\u4EF6\u5305\u88C5\u5668"
        },
        {
          link: "common-ui/vben-alert",
          text: "Alert \u8F7B\u91CF\u63D0\u793A\u6846"
        },
        {
          link: "common-ui/vben-modal",
          text: "Modal \u6A21\u6001\u6846"
        },
        {
          link: "common-ui/vben-drawer",
          text: "Drawer \u62BD\u5C49"
        },
        {
          link: "common-ui/vben-form",
          text: "Form \u8868\u5355"
        },
        {
          link: "common-ui/vben-vxe-table",
          text: "Vxe Table \u8868\u683C"
        },
        {
          link: "common-ui/vben-count-to-animator",
          text: "CountToAnimator \u6570\u5B57\u52A8\u753B"
        },
        {
          link: "common-ui/vben-ellipsis-text",
          text: "EllipsisText \u7701\u7565\u6587\u672C"
        }
      ]
    }
  ];
}
function nav2() {
  return [
    {
      activeMatch: "^/(guide|components)/",
      text: "\u6587\u6863",
      items: [
        {
          activeMatch: "^/guide/",
          link: "/guide/introduction/vben",
          text: "\u6307\u5357"
        },
        {
          activeMatch: "^/components/",
          link: "/components/introduction",
          text: "\u7EC4\u4EF6"
        },
        {
          text: "\u5386\u53F2\u7248\u672C",
          items: [
            {
              link: "https://doc.vvbin.cn",
              text: "2.x\u7248\u672C\u6587\u6863"
            }
          ]
        }
      ]
    },
    {
      text: "\u6F14\u793A",
      items: [
        {
          text: "Vben Admin",
          items: [
            {
              link: "https://www.vben.pro",
              text: "\u6F14\u793A\u7248\u672C"
            },
            {
              link: "https://ant.vben.pro",
              text: "Ant Design Vue \u7248\u672C"
            },
            {
              link: "https://naive.vben.pro",
              text: "Naive \u7248\u672C"
            },
            {
              link: "https://ele.vben.pro",
              text: "Element Plus\u7248\u672C"
            }
          ]
        },
        {
          text: "\u5176\u4ED6",
          items: [
            {
              link: "https://vben.vvbin.cn",
              text: "Vben Admin 2.x"
            }
          ]
        }
      ]
    },
    {
      text: version,
      items: [
        {
          link: "https://github.com/vbenjs/vue-vben-admin/releases",
          text: "\u66F4\u65B0\u65E5\u5FD7"
        },
        {
          link: "https://github.com/orgs/vbenjs/projects/5",
          text: "\u8DEF\u7EBF\u56FE"
        },
        {
          link: "https://github.com/vbenjs/vue-vben-admin/blob/main/.github/contributing.md",
          text: "\u8D21\u732E"
        }
      ]
    },
    {
      link: "/commercial/technical-support",
      text: "\u{1F984} \u6280\u672F\u652F\u6301"
    },
    {
      link: "/sponsor/personal",
      text: "\u2728 \u8D5E\u52A9"
    },
    {
      link: "/commercial/community",
      text: "\u{1F468}\u200D\u{1F466}\u200D\u{1F466} \u4EA4\u6D41\u7FA4"
      // items: [
      //   {
      //     link: 'https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&appChannel=share&inviteCode=22ySzj7pKiw&businessType=9&from=246610&biz=ka&mainSourceId=share&subSourceId=others&jumpsource=shorturl#/pc',
      //     text: 'QQ频道',
      //   },
      //   {
      //     link: 'https://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=mjZmlhgVzzUxvdxllB6C1vHpX8O8QRL0&authKey=DBdFbBwERmfaKY95JvRWqLCJIRGJAmKyZbrpzZ41EKDMZ5SR6MfbjOBaaNRN73fr&noverify=0&group_code=4286109',
      //     text: 'QQ群',
      //   },
      //   {
      //     link: 'https://discord.gg/VU62jTecad',
      //     text: 'Discord',
      //   },
      // ],
    }
    // {
    //   link: '/friend-links/',
    //   text: '🤝 友情链接',
    // },
  ];
}
var search = {
  root: {
    placeholder: "\u641C\u7D22\u6587\u6863",
    translations: {
      button: {
        buttonAriaLabel: "\u641C\u7D22\u6587\u6863",
        buttonText: "\u641C\u7D22\u6587\u6863"
      },
      modal: {
        errorScreen: {
          helpText: "\u4F60\u53EF\u80FD\u9700\u8981\u68C0\u67E5\u4F60\u7684\u7F51\u7EDC\u8FDE\u63A5",
          titleText: "\u65E0\u6CD5\u83B7\u53D6\u7ED3\u679C"
        },
        footer: {
          closeText: "\u5173\u95ED",
          navigateText: "\u5207\u6362",
          searchByText: "\u641C\u7D22\u63D0\u4F9B\u8005",
          selectText: "\u9009\u62E9"
        },
        noResultsScreen: {
          noResultsText: "\u65E0\u6CD5\u627E\u5230\u76F8\u5173\u7ED3\u679C",
          reportMissingResultsLinkText: "\u70B9\u51FB\u53CD\u9988",
          reportMissingResultsText: "\u4F60\u8BA4\u4E3A\u8BE5\u67E5\u8BE2\u5E94\u8BE5\u6709\u7ED3\u679C\uFF1F",
          suggestedQueryText: "\u4F60\u53EF\u4EE5\u5C1D\u8BD5\u67E5\u8BE2"
        },
        searchBox: {
          cancelButtonAriaLabel: "\u53D6\u6D88",
          cancelButtonText: "\u53D6\u6D88",
          resetButtonAriaLabel: "\u6E05\u9664\u67E5\u8BE2\u6761\u4EF6",
          resetButtonTitle: "\u6E05\u9664\u67E5\u8BE2\u6761\u4EF6"
        },
        startScreen: {
          favoriteSearchesTitle: "\u6536\u85CF",
          noRecentSearchesText: "\u6CA1\u6709\u641C\u7D22\u5386\u53F2",
          recentSearchesTitle: "\u641C\u7D22\u5386\u53F2",
          removeFavoriteSearchButtonTitle: "\u4ECE\u6536\u85CF\u4E2D\u79FB\u9664",
          removeRecentSearchButtonTitle: "\u4ECE\u641C\u7D22\u5386\u53F2\u4E2D\u79FB\u9664",
          saveRecentSearchButtonTitle: "\u4FDD\u5B58\u81F3\u641C\u7D22\u5386\u53F2"
        }
      }
    }
  }
};

// .vitepress/config/shared.mts
var shared = defineConfig3({
  appearance: "dark",
  head: head(),
  markdown: {
    preConfig(md) {
      md.use(demoPreviewPlugin);
      md.use(groupIconMdPlugin);
    }
  },
  pwa: pwa(),
  srcDir: "src",
  themeConfig: {
    i18nRouting: true,
    logo: "https://unpkg.com/@vbenjs/static-source@0.1.7/source/logo-v1.webp",
    search: {
      options: {
        locales: {
          ...search
        }
      },
      provider: "local"
    },
    siteTitle: "Vben Admin",
    socialLinks: [
      { icon: "github", link: "https://github.com/vbenjs/vue-vben-admin" }
    ]
  },
  title: "Vben Admin",
  vite: {
    build: {
      chunkSizeWarningLimit: Infinity,
      minify: "terser"
    },
    css: {
      postcss: {
        plugins: [
          tailwind(),
          postcssIsolateStyles({ includeFiles: [/vp-doc\.css/] })
        ]
      },
      preprocessorOptions: {
        scss: {
          api: "modern"
        }
      }
    },
    json: {
      stringify: true
    },
    plugins: [
      GitChangelog({
        mapAuthors: [
          {
            mapByNameAliases: ["Vben"],
            name: "vben",
            username: "anncwb"
          },
          {
            name: "vince",
            username: "vince292007"
          },
          {
            name: "Li Kui",
            username: "likui628"
          }
        ],
        repoURL: () => "https://github.com/vbenjs/vue-vben-admin"
      }),
      GitChangelogMarkdownSection(),
      viteArchiverPlugin({ outputDir: ".vitepress" }),
      groupIconVitePlugin(),
      await viteVxeTableImportsPlugin()
    ],
    server: {
      fs: {
        allow: ["../.."]
      },
      host: true,
      port: 6173
    },
    ssr: {
      external: ["@vue/repl"]
    }
  }
});
function head() {
  return [
    ["meta", { content: "Vbenjs Team", name: "author" }],
    [
      "meta",
      {
        content: "vben, vitejs, vite, shacdn-ui, vue",
        name: "keywords"
      }
    ],
    ["link", { href: "/favicon.ico", rel: "icon", type: "image/svg+xml" }],
    [
      "meta",
      {
        content: "width=device-width,initial-scale=1,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no",
        name: "viewport"
      }
    ],
    ["meta", { content: "vben admin docs", name: "keywords" }],
    ["link", { href: "/favicon.ico", rel: "icon" }]
    // [
    //   'script',
    //   {
    //     src: 'https://cdn.tailwindcss.com',
    //   },
    // ],
  ];
}
function pwa() {
  return {
    includeManifestIcons: false,
    manifest: {
      description: "Vben Admin is a modern admin dashboard template based on Vue 3. ",
      icons: [
        {
          sizes: "192x192",
          src: "https://unpkg.com/@vbenjs/static-source@0.1.7/source/pwa-icon-192.png",
          type: "image/png"
        },
        {
          sizes: "512x512",
          src: "https://unpkg.com/@vbenjs/static-source@0.1.7/source/pwa-icon-512.png",
          type: "image/png"
        }
      ],
      id: "/",
      name: "Vben Admin Doc",
      short_name: "vben_admin_doc",
      theme_color: "#ffffff"
    },
    outDir: resolve(process.cwd(), ".vitepress/dist"),
    registerType: "autoUpdate",
    workbox: {
      globPatterns: ["**/*.{css,js,html,svg,png,ico,txt,woff2}"],
      maximumFileSizeToCacheInBytes: 5 * 1024 * 1024
    }
  };
}

// .vitepress/config/index.mts
var config_default = withPwa(
  defineConfigWithTheme({
    ...shared,
    locales: {
      en: {
        label: "English",
        lang: "en",
        link: "/en/",
        ...en
      },
      root: {
        label: "\u7B80\u4F53\u4E2D\u6587",
        lang: "zh-CN",
        ...zh
      }
    }
  })
);
export {
  config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsiLnZpdGVwcmVzcy9jb25maWcvaW5kZXgubXRzIiwgIi52aXRlcHJlc3MvY29uZmlnL2VuLm10cyIsICIuLi9wYWNrYWdlLmpzb24iLCAiLnZpdGVwcmVzcy9jb25maWcvc2hhcmVkLm10cyIsICIudml0ZXByZXNzL2NvbmZpZy9wbHVnaW5zL2RlbW8tcHJldmlldy50cyIsICIudml0ZXByZXNzL2NvbmZpZy96aC5tdHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFxUYXJlLXdvcmtzcGFjZVxcXFxwbS1kaXJlY3RvclxcXFx1aS12YmVuXFxcXGRvY3NcXFxcLnZpdGVwcmVzc1xcXFxjb25maWdcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIkQ6XFxcXFRhcmUtd29ya3NwYWNlXFxcXHBtLWRpcmVjdG9yXFxcXHVpLXZiZW5cXFxcZG9jc1xcXFwudml0ZXByZXNzXFxcXGNvbmZpZ1xcXFxpbmRleC5tdHNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL0Q6L1RhcmUtd29ya3NwYWNlL3BtLWRpcmVjdG9yL3VpLXZiZW4vZG9jcy8udml0ZXByZXNzL2NvbmZpZy9pbmRleC5tdHNcIjtpbXBvcnQgeyB3aXRoUHdhIH0gZnJvbSAnQHZpdGUtcHdhL3ZpdGVwcmVzcyc7XG5pbXBvcnQgeyBkZWZpbmVDb25maWdXaXRoVGhlbWUgfSBmcm9tICd2aXRlcHJlc3MnO1xuXG5pbXBvcnQgeyBlbiB9IGZyb20gJy4vZW4ubXRzJztcbmltcG9ydCB7IHNoYXJlZCB9IGZyb20gJy4vc2hhcmVkLm10cyc7XG5pbXBvcnQgeyB6aCB9IGZyb20gJy4vemgubXRzJztcblxuZXhwb3J0IGRlZmF1bHQgd2l0aFB3YShcbiAgZGVmaW5lQ29uZmlnV2l0aFRoZW1lKHtcbiAgICAuLi5zaGFyZWQsXG4gICAgbG9jYWxlczoge1xuICAgICAgZW46IHtcbiAgICAgICAgbGFiZWw6ICdFbmdsaXNoJyxcbiAgICAgICAgbGFuZzogJ2VuJyxcbiAgICAgICAgbGluazogJy9lbi8nLFxuICAgICAgICAuLi5lbixcbiAgICAgIH0sXG4gICAgICByb290OiB7XG4gICAgICAgIGxhYmVsOiAnXHU3QjgwXHU0RjUzXHU0RTJEXHU2NTg3JyxcbiAgICAgICAgbGFuZzogJ3poLUNOJyxcbiAgICAgICAgLi4uemgsXG4gICAgICB9LFxuICAgIH0sXG4gIH0pLFxuKTtcbiIsICJjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZGlybmFtZSA9IFwiRDpcXFxcVGFyZS13b3Jrc3BhY2VcXFxccG0tZGlyZWN0b3JcXFxcdWktdmJlblxcXFxkb2NzXFxcXC52aXRlcHJlc3NcXFxcY29uZmlnXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJEOlxcXFxUYXJlLXdvcmtzcGFjZVxcXFxwbS1kaXJlY3RvclxcXFx1aS12YmVuXFxcXGRvY3NcXFxcLnZpdGVwcmVzc1xcXFxjb25maWdcXFxcZW4ubXRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9EOi9UYXJlLXdvcmtzcGFjZS9wbS1kaXJlY3Rvci91aS12YmVuL2RvY3MvLnZpdGVwcmVzcy9jb25maWcvZW4ubXRzXCI7aW1wb3J0IHR5cGUgeyBEZWZhdWx0VGhlbWUgfSBmcm9tICd2aXRlcHJlc3MnO1xuXG5pbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlcHJlc3MnO1xuXG5pbXBvcnQgeyB2ZXJzaW9uIH0gZnJvbSAnLi4vLi4vLi4vcGFja2FnZS5qc29uJztcblxuZXhwb3J0IGNvbnN0IGVuID0gZGVmaW5lQ29uZmlnKHtcbiAgZGVzY3JpcHRpb246ICdWYmVuIEFkbWluICYgRW50ZXJwcmlzZSBsZXZlbCBtYW5hZ2VtZW50IHN5c3RlbSBmcmFtZXdvcmsnLFxuICBsYW5nOiAnZW4tVVMnLFxuICB0aGVtZUNvbmZpZzoge1xuICAgIGRhcmtNb2RlU3dpdGNoTGFiZWw6ICdUaGVtZScsXG4gICAgZGFya01vZGVTd2l0Y2hUaXRsZTogJ1N3aXRjaCB0byBEYXJrIE1vZGUnLFxuICAgIGRvY0Zvb3Rlcjoge1xuICAgICAgbmV4dDogJ05leHQgUGFnZScsXG4gICAgICBwcmV2OiAnUHJldmlvdXMgUGFnZScsXG4gICAgfSxcbiAgICBlZGl0TGluazoge1xuICAgICAgcGF0dGVybjpcbiAgICAgICAgJ2h0dHBzOi8vZ2l0aHViLmNvbS92YmVuanMvdnVlLXZiZW4tYWRtaW4vZWRpdC9tYWluL2RvY3Mvc3JjLzpwYXRoJyxcbiAgICAgIHRleHQ6ICdFZGl0IHRoaXMgcGFnZSBvbiBHaXRIdWInLFxuICAgIH0sXG4gICAgZm9vdGVyOiB7XG4gICAgICBjb3B5cmlnaHQ6IGBDb3B5cmlnaHQgXHUwMEE5IDIwMjAtJHtuZXcgRGF0ZSgpLmdldEZ1bGxZZWFyKCl9IFZiZW5gLFxuICAgICAgbWVzc2FnZTogJ1JlbGVhc2VkIHVuZGVyIHRoZSBNSVQgTGljZW5zZS4nLFxuICAgIH0sXG4gICAgbGFuZ01lbnVMYWJlbDogJ0xhbmd1YWdlJyxcbiAgICBsYXN0VXBkYXRlZDoge1xuICAgICAgZm9ybWF0T3B0aW9uczoge1xuICAgICAgICBkYXRlU3R5bGU6ICdzaG9ydCcsXG4gICAgICAgIHRpbWVTdHlsZTogJ21lZGl1bScsXG4gICAgICB9LFxuICAgICAgdGV4dDogJ0xhc3QgdXBkYXRlZCBvbicsXG4gICAgfSxcbiAgICBsaWdodE1vZGVTd2l0Y2hUaXRsZTogJ1N3aXRjaCB0byBMaWdodCBNb2RlJyxcbiAgICBuYXY6IG5hdigpLFxuICAgIG91dGxpbmU6IHtcbiAgICAgIGxhYmVsOiAnTmF2aWdhdGUnLFxuICAgIH0sXG4gICAgcmV0dXJuVG9Ub3BMYWJlbDogJ0JhY2sgdG8gdG9wJyxcbiAgICBzaWRlYmFyOiB7XG4gICAgICAnL2VuL2NvbW1lcmNpYWwvJzoge1xuICAgICAgICBiYXNlOiAnL2VuL2NvbW1lcmNpYWwvJyxcbiAgICAgICAgaXRlbXM6IHNpZGViYXJDb21tZXJjaWFsKCksXG4gICAgICB9LFxuICAgICAgJy9lbi9ndWlkZS8nOiB7IGJhc2U6ICcvZW4vZ3VpZGUvJywgaXRlbXM6IHNpZGViYXJHdWlkZSgpIH0sXG4gICAgfSxcbiAgfSxcbn0pO1xuXG5mdW5jdGlvbiBzaWRlYmFyR3VpZGUoKTogRGVmYXVsdFRoZW1lLlNpZGViYXJJdGVtW10ge1xuICByZXR1cm4gW1xuICAgIHtcbiAgICAgIGNvbGxhcHNlZDogZmFsc2UsXG4gICAgICB0ZXh0OiAnSW50cm9kdWN0aW9uJyxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBsaW5rOiAnaW50cm9kdWN0aW9uL3ZiZW4nLFxuICAgICAgICAgIHRleHQ6ICdBYm91dCBWYmVuIEFkbWluJyxcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIGxpbms6ICdpbnRyb2R1Y3Rpb24vd2h5JyxcbiAgICAgICAgICB0ZXh0OiAnV2h5IENob29zZSBVcz8nLFxuICAgICAgICB9LFxuICAgICAgICB7IGxpbms6ICdpbnRyb2R1Y3Rpb24vcXVpY2stc3RhcnQnLCB0ZXh0OiAnUXVpY2sgU3RhcnQnIH0sXG4gICAgICAgIHsgbGluazogJ2ludHJvZHVjdGlvbi90aGluJywgdGV4dDogJ0xpdGUgVmVyc2lvbicgfSxcbiAgICAgIF0sXG4gICAgfSxcbiAgICB7XG4gICAgICB0ZXh0OiAnQmFzaWNzJyxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHsgbGluazogJ2Vzc2VudGlhbHMvY29uY2VwdCcsIHRleHQ6ICdCYXNpYyBDb25jZXB0cycgfSxcbiAgICAgICAgeyBsaW5rOiAnZXNzZW50aWFscy9kZXZlbG9wbWVudCcsIHRleHQ6ICdMb2NhbCBEZXZlbG9wbWVudCcgfSxcbiAgICAgICAgeyBsaW5rOiAnZXNzZW50aWFscy9yb3V0ZScsIHRleHQ6ICdSb3V0aW5nIGFuZCBNZW51JyB9LFxuICAgICAgICB7IGxpbms6ICdlc3NlbnRpYWxzL3NldHRpbmdzJywgdGV4dDogJ0NvbmZpZ3VyYXRpb24nIH0sXG4gICAgICAgIHsgbGluazogJ2Vzc2VudGlhbHMvaWNvbnMnLCB0ZXh0OiAnSWNvbnMnIH0sXG4gICAgICAgIHsgbGluazogJ2Vzc2VudGlhbHMvc3R5bGVzJywgdGV4dDogJ1N0eWxlcycgfSxcbiAgICAgICAgeyBsaW5rOiAnZXNzZW50aWFscy9leHRlcm5hbC1tb2R1bGUnLCB0ZXh0OiAnRXh0ZXJuYWwgTW9kdWxlcycgfSxcbiAgICAgICAgeyBsaW5rOiAnZXNzZW50aWFscy9idWlsZCcsIHRleHQ6ICdCdWlsZCBhbmQgRGVwbG95bWVudCcgfSxcbiAgICAgICAgeyBsaW5rOiAnZXNzZW50aWFscy9zZXJ2ZXInLCB0ZXh0OiAnU2VydmVyIEludGVyYWN0aW9uIGFuZCBEYXRhIE1vY2snIH0sXG4gICAgICBdLFxuICAgIH0sXG4gICAge1xuICAgICAgdGV4dDogJ0FkdmFuY2VkJyxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHsgbGluazogJ2luLWRlcHRoL2xvZ2luJywgdGV4dDogJ0xvZ2luJyB9LFxuICAgICAgICB7IGxpbms6ICdpbi1kZXB0aC90aGVtZScsIHRleHQ6ICdUaGVtZScgfSxcbiAgICAgICAgeyBsaW5rOiAnaW4tZGVwdGgvYWNjZXNzJywgdGV4dDogJ0FjY2VzcyBDb250cm9sJyB9LFxuICAgICAgICB7IGxpbms6ICdpbi1kZXB0aC9sb2NhbGUnLCB0ZXh0OiAnSW50ZXJuYXRpb25hbGl6YXRpb24nIH0sXG4gICAgICAgIHsgbGluazogJ2luLWRlcHRoL2ZlYXR1cmVzJywgdGV4dDogJ0NvbW1vbiBGZWF0dXJlcycgfSxcbiAgICAgICAgeyBsaW5rOiAnaW4tZGVwdGgvY2hlY2stdXBkYXRlcycsIHRleHQ6ICdDaGVjayBVcGRhdGVzJyB9LFxuICAgICAgICB7IGxpbms6ICdpbi1kZXB0aC9sb2FkaW5nJywgdGV4dDogJ0dsb2JhbCBMb2FkaW5nJyB9LFxuICAgICAgICB7IGxpbms6ICdpbi1kZXB0aC91aS1mcmFtZXdvcmsnLCB0ZXh0OiAnVUkgRnJhbWV3b3JrIFN3aXRjaGluZycgfSxcbiAgICAgIF0sXG4gICAgfSxcbiAgICB7XG4gICAgICB0ZXh0OiAnRW5naW5lZXJpbmcnLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAgeyBsaW5rOiAncHJvamVjdC9zdGFuZGFyZCcsIHRleHQ6ICdTdGFuZGFyZHMnIH0sXG4gICAgICAgIHsgbGluazogJ3Byb2plY3QvY2xpJywgdGV4dDogJ0NMSScgfSxcbiAgICAgICAgeyBsaW5rOiAncHJvamVjdC9kaXInLCB0ZXh0OiAnRGlyZWN0b3J5IEV4cGxhbmF0aW9uJyB9LFxuICAgICAgICB7IGxpbms6ICdwcm9qZWN0L3Rlc3QnLCB0ZXh0OiAnVW5pdCBUZXN0aW5nJyB9LFxuICAgICAgICB7IGxpbms6ICdwcm9qZWN0L3RhaWx3aW5kY3NzJywgdGV4dDogJ1RhaWx3aW5kIENTUycgfSxcbiAgICAgICAgeyBsaW5rOiAncHJvamVjdC9jaGFuZ2VzZXQnLCB0ZXh0OiAnQ2hhbmdlc2V0JyB9LFxuICAgICAgICB7IGxpbms6ICdwcm9qZWN0L3ZpdGUnLCB0ZXh0OiAnVml0ZSBDb25maWcnIH0sXG4gICAgICBdLFxuICAgIH0sXG4gICAge1xuICAgICAgdGV4dDogJ090aGVycycsXG4gICAgICBpdGVtczogW1xuICAgICAgICB7IGxpbms6ICdvdGhlci9wcm9qZWN0LXVwZGF0ZScsIHRleHQ6ICdQcm9qZWN0IFVwZGF0ZScgfSxcbiAgICAgICAgeyBsaW5rOiAnb3RoZXIvcmVtb3ZlLWNvZGUnLCB0ZXh0OiAnUmVtb3ZlIENvZGUnIH0sXG4gICAgICAgIHsgbGluazogJ290aGVyL2ZhcScsIHRleHQ6ICdGQVEnIH0sXG4gICAgICBdLFxuICAgIH0sXG4gIF07XG59XG5cbmZ1bmN0aW9uIHNpZGViYXJDb21tZXJjaWFsKCk6IERlZmF1bHRUaGVtZS5TaWRlYmFySXRlbVtdIHtcbiAgcmV0dXJuIFtcbiAgICB7XG4gICAgICBsaW5rOiAnY29tbXVuaXR5JyxcbiAgICAgIHRleHQ6ICdDb21tdW5pdHknLFxuICAgIH0sXG4gICAge1xuICAgICAgbGluazogJ3RlY2huaWNhbC1zdXBwb3J0JyxcbiAgICAgIHRleHQ6ICdUZWNobmljYWwtc3VwcG9ydCcsXG4gICAgfSxcbiAgICB7XG4gICAgICBsaW5rOiAnY3VzdG9taXplZCcsXG4gICAgICB0ZXh0OiAnQ3VzdG9taXplZCcsXG4gICAgfSxcbiAgXTtcbn1cblxuZnVuY3Rpb24gbmF2KCk6IERlZmF1bHRUaGVtZS5OYXZJdGVtW10ge1xuICByZXR1cm4gW1xuICAgIHtcbiAgICAgIGFjdGl2ZU1hdGNoOiAnXi9lbi8oZ3VpZGV8Y29tcG9uZW50cykvJyxcbiAgICAgIHRleHQ6ICdEb2MnLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAge1xuICAgICAgICAgIGFjdGl2ZU1hdGNoOiAnXi9lbi9ndWlkZS8nLFxuICAgICAgICAgIGxpbms6ICcvZW4vZ3VpZGUvaW50cm9kdWN0aW9uL3ZiZW4nLFxuICAgICAgICAgIHRleHQ6ICdHdWlkZScsXG4gICAgICAgIH0sXG4gICAgICAgIC8vIHtcbiAgICAgICAgLy8gICBhY3RpdmVNYXRjaDogJ14vZW4vY29tcG9uZW50cy8nLFxuICAgICAgICAvLyAgIGxpbms6ICcvZW4vY29tcG9uZW50cy9pbnRyb2R1Y3Rpb24nLFxuICAgICAgICAvLyAgIHRleHQ6ICdDb21wb25lbnRzJyxcbiAgICAgICAgLy8gfSxcbiAgICAgICAge1xuICAgICAgICAgIHRleHQ6ICdIaXN0b3JpY2FsIFZlcnNpb25zJyxcbiAgICAgICAgICBpdGVtczogW1xuICAgICAgICAgICAge1xuICAgICAgICAgICAgICBsaW5rOiAnaHR0cHM6Ly9kb2MudnZiaW4uY24nLFxuICAgICAgICAgICAgICB0ZXh0OiAnMi54IFZlcnNpb24gRG9jdW1lbnRhdGlvbicsXG4gICAgICAgICAgICB9LFxuICAgICAgICAgIF0sXG4gICAgICAgIH0sXG4gICAgICBdLFxuICAgIH0sXG4gICAge1xuICAgICAgdGV4dDogJ0RlbW8nLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAge1xuICAgICAgICAgIHRleHQ6ICdWYmVuIEFkbWluJyxcbiAgICAgICAgICBpdGVtczogW1xuICAgICAgICAgICAge1xuICAgICAgICAgICAgICBsaW5rOiAnaHR0cHM6Ly93d3cudmJlbi5wcm8nLFxuICAgICAgICAgICAgICB0ZXh0OiAnRGVtbyBWZXJzaW9uJyxcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgIGxpbms6ICdodHRwczovL2FudC52YmVuLnBybycsXG4gICAgICAgICAgICAgIHRleHQ6ICdBbnQgRGVzaWduIFZ1ZSBWZXJzaW9uJyxcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgIGxpbms6ICdodHRwczovL25haXZlLnZiZW4ucHJvJyxcbiAgICAgICAgICAgICAgdGV4dDogJ05haXZlIFZlcnNpb24nLFxuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgbGluazogJ2h0dHBzOi8vZWxlLnZiZW4ucHJvJyxcbiAgICAgICAgICAgICAgdGV4dDogJ0VsZW1lbnQgUGx1cyBWZXJzaW9uJyxcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgXSxcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIHRleHQ6ICdPdGhlcnMnLFxuICAgICAgICAgIGl0ZW1zOiBbXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgIGxpbms6ICdodHRwczovL3ZiZW4udnZiaW4uY24nLFxuICAgICAgICAgICAgICB0ZXh0OiAnVmJlbiBBZG1pbiAyLngnLFxuICAgICAgICAgICAgfSxcbiAgICAgICAgICBdLFxuICAgICAgICB9LFxuICAgICAgXSxcbiAgICB9LFxuICAgIHtcbiAgICAgIHRleHQ6IHZlcnNpb24sXG4gICAgICBpdGVtczogW1xuICAgICAgICB7XG4gICAgICAgICAgbGluazogJ2h0dHBzOi8vZ2l0aHViLmNvbS92YmVuanMvdnVlLXZiZW4tYWRtaW4vcmVsZWFzZXMnLFxuICAgICAgICAgIHRleHQ6ICdDaGFuZ2Vsb2cnLFxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgbGluazogJ2h0dHBzOi8vZ2l0aHViLmNvbS9vcmdzL3ZiZW5qcy9wcm9qZWN0cy81JyxcbiAgICAgICAgICB0ZXh0OiAnUm9hZG1hcCcsXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBsaW5rOiAnaHR0cHM6Ly9naXRodWIuY29tL3ZiZW5qcy92dWUtdmJlbi1hZG1pbi9ibG9iL21haW4vLmdpdGh1Yi9jb250cmlidXRpbmcubWQnLFxuICAgICAgICAgIHRleHQ6ICdDb250cmlidXRpb24nLFxuICAgICAgICB9LFxuICAgICAgXSxcbiAgICB9LFxuICAgIHtcbiAgICAgIGxpbms6ICcvY29tbWVyY2lhbC90ZWNobmljYWwtc3VwcG9ydCcsXG4gICAgICB0ZXh0OiAnXHVEODNFXHVERDg0IFRlY2ggU3VwcG9ydCcsXG4gICAgfSxcbiAgICB7XG4gICAgICBsaW5rOiAnL3Nwb25zb3IvcGVyc29uYWwnLFxuICAgICAgdGV4dDogJ1x1MjcyOCBTcG9uc29yJyxcbiAgICB9LFxuICAgIHtcbiAgICAgIGxpbms6ICcvY29tbWVyY2lhbC9jb21tdW5pdHknLFxuICAgICAgdGV4dDogJ1x1RDgzRFx1REM2OFx1MjAwRFx1RDgzRFx1REM2Nlx1MjAwRFx1RDgzRFx1REM2NiBDb21tdW5pdHknLFxuICAgIH0sXG4gICAgLy8ge1xuICAgIC8vICAgbGluazogJy9mcmllbmQtbGlua3MvJyxcbiAgICAvLyAgIHRleHQ6ICdcdUQ4M0VcdUREMUQgRnJpZW5kIExpbmtzJyxcbiAgICAvLyB9LFxuICBdO1xufVxuIiwgIntcbiAgXCJuYW1lXCI6IFwidmJlbi1hZG1pbi1tb25vcmVwb1wiLFxuICBcInZlcnNpb25cIjogXCI1LjUuOVwiLFxuICBcInByaXZhdGVcIjogdHJ1ZSxcbiAgXCJrZXl3b3Jkc1wiOiBbXG4gICAgXCJtb25vcmVwb1wiLFxuICAgIFwidHVyYm9cIixcbiAgICBcInZiZW5cIixcbiAgICBcInZiZW4gYWRtaW5cIixcbiAgICBcInZiZW4gcHJvXCIsXG4gICAgXCJ2dWVcIixcbiAgICBcInZ1ZSBhZG1pblwiLFxuICAgIFwidnVlIHZiZW4gYWRtaW5cIixcbiAgICBcInZ1ZSB2YmVuIGFkbWluIHByb1wiLFxuICAgIFwidnVlM1wiXG4gIF0sXG4gIFwiaG9tZXBhZ2VcIjogXCJodHRwczovL2dpdGh1Yi5jb20vdmJlbmpzL3Z1ZS12YmVuLWFkbWluXCIsXG4gIFwiYnVnc1wiOiBcImh0dHBzOi8vZ2l0aHViLmNvbS92YmVuanMvdnVlLXZiZW4tYWRtaW4vaXNzdWVzXCIsXG4gIFwicmVwb3NpdG9yeVwiOiBcInZiZW5qcy92dWUtdmJlbi1hZG1pbi5naXRcIixcbiAgXCJsaWNlbnNlXCI6IFwiTUlUXCIsXG4gIFwiYXV0aG9yXCI6IHtcbiAgICBcIm5hbWVcIjogXCJ2YmVuXCIsXG4gICAgXCJlbWFpbFwiOiBcImFubi52YmVuQGdtYWlsLmNvbVwiLFxuICAgIFwidXJsXCI6IFwiaHR0cHM6Ly9naXRodWIuY29tL2FubmN3YlwiXG4gIH0sXG4gIFwidHlwZVwiOiBcIm1vZHVsZVwiLFxuICBcInNjcmlwdHNcIjoge1xuICAgIFwiYnVpbGRcIjogXCJjcm9zcy1lbnYgTk9ERV9PUFRJT05TPS0tbWF4LW9sZC1zcGFjZS1zaXplPTgxOTIgdHVyYm8gYnVpbGRcIixcbiAgICBcImJ1aWxkOmFuYWx5emVcIjogXCJ0dXJibyBidWlsZDphbmFseXplXCIsXG4gICAgXCJidWlsZDphbnRkXCI6IFwicG5wbSBydW4gYnVpbGQgLS1maWx0ZXI9QHZiZW4vd2ViLWFudGRcIixcbiAgICBcImJ1aWxkOmRvY2tlclwiOiBcIi4vc2NyaXB0cy9kZXBsb3kvYnVpbGQtbG9jYWwtZG9ja2VyLWltYWdlLnNoXCIsXG4gICAgXCJidWlsZDpkb2NzXCI6IFwicG5wbSBydW4gYnVpbGQgLS1maWx0ZXI9QHZiZW4vZG9jc1wiLFxuICAgIFwiYnVpbGQ6ZWxlXCI6IFwicG5wbSBydW4gYnVpbGQgLS1maWx0ZXI9QHZiZW4vd2ViLWVsZVwiLFxuICAgIFwiYnVpbGQ6bmFpdmVcIjogXCJwbnBtIHJ1biBidWlsZCAtLWZpbHRlcj1AdmJlbi93ZWItbmFpdmVcIixcbiAgICBcImJ1aWxkOnRkZXNpZ25cIjogXCJwbnBtIHJ1biBidWlsZCAtLWZpbHRlcj1AdmJlbi93ZWItdGRlc2lnblwiLFxuICAgIFwiY2hhbmdlc2V0XCI6IFwicG5wbSBleGVjIGNoYW5nZXNldFwiLFxuICAgIFwiY2hlY2tcIjogXCJwbnBtIHJ1biBjaGVjazpjaXJjdWxhciAmJiBwbnBtIHJ1biBjaGVjazpkZXAgJiYgcG5wbSBydW4gY2hlY2s6dHlwZSAmJiBwbnBtIGNoZWNrOmNzcGVsbFwiLFxuICAgIFwiY2hlY2s6Y2lyY3VsYXJcIjogXCJ2c2ggY2hlY2stY2lyY3VsYXJcIixcbiAgICBcImNoZWNrOmNzcGVsbFwiOiBcImNzcGVsbCBsaW50ICoqLyoudHMgKiovUkVBRE1FLm1kIC5jaGFuZ2VzZXQvKi5tZCAtLW5vLXByb2dyZXNzXCIsXG4gICAgXCJjaGVjazpkZXBcIjogXCJ2c2ggY2hlY2stZGVwXCIsXG4gICAgXCJjaGVjazp0eXBlXCI6IFwidHVyYm8gcnVuIHR5cGVjaGVja1wiLFxuICAgIFwiY2xlYW5cIjogXCJub2RlIC4vc2NyaXB0cy9jbGVhbi5tanNcIixcbiAgICBcImNvbW1pdFwiOiBcImN6Z1wiLFxuICAgIFwiZGV2XCI6IFwidHVyYm8tcnVuIGRldlwiLFxuICAgIFwiZGV2OmFudGRcIjogXCJwbnBtIC1GIEB2YmVuL3dlYi1hbnRkIHJ1biBkZXZcIixcbiAgICBcImRldjphbnRkdi1uZXh0XCI6IFwicG5wbSAtRiBAdmJlbi93ZWItYW50ZHYtbmV4dCBydW4gZGV2XCIsXG4gICAgXCJkZXY6ZG9jc1wiOiBcInBucG0gLUYgQHZiZW4vZG9jcyBydW4gZGV2XCIsXG4gICAgXCJkZXY6ZWxlXCI6IFwicG5wbSAtRiBAdmJlbi93ZWItZWxlIHJ1biBkZXZcIixcbiAgICBcImRldjpuYWl2ZVwiOiBcInBucG0gLUYgQHZiZW4vd2ViLW5haXZlIHJ1biBkZXZcIixcbiAgICBcImRldjp0ZGVzaWduXCI6IFwicG5wbSAtRiBAdmJlbi93ZWItdGRlc2lnbiBydW4gZGV2XCIsXG4gICAgXCJmb3JtYXRcIjogXCJ2c2ggbGludCAtLWZvcm1hdFwiLFxuICAgIFwibGludFwiOiBcInZzaCBsaW50XCIsXG4gICAgXCJwb3N0aW5zdGFsbFwiOiBcInBucG0gLXIgcnVuIHN0dWIgLS1pZi1wcmVzZW50XCIsXG4gICAgXCJwcmVpbnN0YWxsXCI6IFwibnB4IG9ubHktYWxsb3cgcG5wbVwiLFxuICAgIFwicHJldmlld1wiOiBcInR1cmJvLXJ1biBwcmV2aWV3XCIsXG4gICAgXCJwdWJsaW50XCI6IFwidnNoIHB1YmxpbnRcIixcbiAgICBcInJlaW5zdGFsbFwiOiBcInBucG0gY2xlYW4gLS1kZWwtbG9jayAmJiBwbnBtIGluc3RhbGxcIixcbiAgICBcInRlc3Q6dW5pdFwiOiBcInZpdGVzdCBydW4gLS1kb21cIixcbiAgICBcInRlc3Q6ZTJlXCI6IFwidHVyYm8gcnVuIHRlc3Q6ZTJlXCIsXG4gICAgXCJ1cGRhdGU6ZGVwc1wiOiBcIm5weCB0YXplIC1yIC13XCIsXG4gICAgXCJ2ZXJzaW9uXCI6IFwicG5wbSBleGVjIGNoYW5nZXNldCB2ZXJzaW9uICYmIHBucG0gaW5zdGFsbCAtLW5vLWZyb3plbi1sb2NrZmlsZVwiLFxuICAgIFwiY2F0YWxvZ1wiOiBcInBucHggY29kZW1vZCBwbnBtL2NhdGFsb2dcIlxuICB9LFxuICBcImRldkRlcGVuZGVuY2llc1wiOiB7XG4gICAgXCJAY2hhbmdlc2V0cy9jaGFuZ2Vsb2ctZ2l0aHViXCI6IFwiY2F0YWxvZzpcIixcbiAgICBcIkBjaGFuZ2VzZXRzL2NsaVwiOiBcImNhdGFsb2c6XCIsXG4gICAgXCJAcGxheXdyaWdodC90ZXN0XCI6IFwiY2F0YWxvZzpcIixcbiAgICBcIkB0eXBlcy9ub2RlXCI6IFwiY2F0YWxvZzpcIixcbiAgICBcIkB2YmVuL2NvbW1pdGxpbnQtY29uZmlnXCI6IFwid29ya3NwYWNlOipcIixcbiAgICBcIkB2YmVuL2VzbGludC1jb25maWdcIjogXCJ3b3Jrc3BhY2U6KlwiLFxuICAgIFwiQHZiZW4vcHJldHRpZXItY29uZmlnXCI6IFwid29ya3NwYWNlOipcIixcbiAgICBcIkB2YmVuL3N0eWxlbGludC1jb25maWdcIjogXCJ3b3Jrc3BhY2U6KlwiLFxuICAgIFwiQHZiZW4vdGFpbHdpbmQtY29uZmlnXCI6IFwid29ya3NwYWNlOipcIixcbiAgICBcIkB2YmVuL3RzY29uZmlnXCI6IFwid29ya3NwYWNlOipcIixcbiAgICBcIkB2YmVuL3R1cmJvLXJ1blwiOiBcIndvcmtzcGFjZToqXCIsXG4gICAgXCJAdmJlbi92aXRlLWNvbmZpZ1wiOiBcIndvcmtzcGFjZToqXCIsXG4gICAgXCJAdmJlbi92c2hcIjogXCJ3b3Jrc3BhY2U6KlwiLFxuICAgIFwiQHZpdGVqcy9wbHVnaW4tdnVlXCI6IFwiY2F0YWxvZzpcIixcbiAgICBcIkB2aXRlanMvcGx1Z2luLXZ1ZS1qc3hcIjogXCJjYXRhbG9nOlwiLFxuICAgIFwiQHZ1ZS90ZXN0LXV0aWxzXCI6IFwiY2F0YWxvZzpcIixcbiAgICBcImF1dG9wcmVmaXhlclwiOiBcImNhdGFsb2c6XCIsXG4gICAgXCJjcm9zcy1lbnZcIjogXCJjYXRhbG9nOlwiLFxuICAgIFwiY3NwZWxsXCI6IFwiY2F0YWxvZzpcIixcbiAgICBcImhhcHB5LWRvbVwiOiBcImNhdGFsb2c6XCIsXG4gICAgXCJpZHNcIjogXCIzLjAuMVwiLFxuICAgIFwiaXMtY2lcIjogXCJjYXRhbG9nOlwiLFxuICAgIFwiaml0aVwiOiBcIjIuNi4xXCIsXG4gICAgXCJsZWZ0aG9va1wiOiBcImNhdGFsb2c6XCIsXG4gICAgXCJwbGF5d3JpZ2h0XCI6IFwiY2F0YWxvZzpcIixcbiAgICBcInJpbXJhZlwiOiBcImNhdGFsb2c6XCIsXG4gICAgXCJzYXNzXCI6IFwiMS44MC42XCIsXG4gICAgXCJ0YWlsd2luZGNzc1wiOiBcImNhdGFsb2c6XCIsXG4gICAgXCJ0dXJib1wiOiBcImNhdGFsb2c6XCIsXG4gICAgXCJ0eXBlc2NyaXB0XCI6IFwiY2F0YWxvZzpcIixcbiAgICBcInVuYnVpbGRcIjogXCJjYXRhbG9nOlwiLFxuICAgIFwidml0ZVwiOiBcImNhdGFsb2c6XCIsXG4gICAgXCJ2aXRlc3RcIjogXCJjYXRhbG9nOlwiLFxuICAgIFwidnVlXCI6IFwiY2F0YWxvZzpcIixcbiAgICBcInZ1ZS10c2NcIjogXCJjYXRhbG9nOlwiXG4gIH0sXG4gIFwiZW5naW5lc1wiOiB7XG4gICAgXCJub2RlXCI6IFwiPj0yMC4xOS4wXCIsXG4gICAgXCJwbnBtXCI6IFwiPj0xMC4wLjBcIlxuICB9LFxuICBcInBhY2thZ2VNYW5hZ2VyXCI6IFwicG5wbUAxMC4yOC4yXCIsXG4gIFwicG5wbVwiOiB7XG4gICAgXCJvbmx5QnVpbHREZXBlbmRlbmNpZXNcIjogW1xuICAgICAgXCJAY2FyYm9uL2ljb25zXCIsXG4gICAgICBcIkBwYXJjZWwvd2F0Y2hlclwiLFxuICAgICAgXCJjb3JlLWpzXCIsXG4gICAgICBcImNvcmUtanMtcHVyZVwiLFxuICAgICAgXCJlc2J1aWxkXCIsXG4gICAgICBcImxlZnRob29rXCIsXG4gICAgICBcImxlc3NcIixcbiAgICAgIFwidW5ycy1yZXNvbHZlclwiXG4gICAgXSxcbiAgICBcIm92ZXJyaWRlc1wiOiB7XG4gICAgICBcImlkc1wiOiBcIjMuMC4xXCIsXG4gICAgICBcInNhc3NcIjogXCIxLjgwLjZcIlxuICAgIH1cbiAgfVxufSIsICJjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZGlybmFtZSA9IFwiRDpcXFxcVGFyZS13b3Jrc3BhY2VcXFxccG0tZGlyZWN0b3JcXFxcdWktdmJlblxcXFxkb2NzXFxcXC52aXRlcHJlc3NcXFxcY29uZmlnXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJEOlxcXFxUYXJlLXdvcmtzcGFjZVxcXFxwbS1kaXJlY3RvclxcXFx1aS12YmVuXFxcXGRvY3NcXFxcLnZpdGVwcmVzc1xcXFxjb25maWdcXFxcc2hhcmVkLm10c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vRDovVGFyZS13b3Jrc3BhY2UvcG0tZGlyZWN0b3IvdWktdmJlbi9kb2NzLy52aXRlcHJlc3MvY29uZmlnL3NoYXJlZC5tdHNcIjtpbXBvcnQgdHlwZSB7IFB3YU9wdGlvbnMgfSBmcm9tICdAdml0ZS1wd2Evdml0ZXByZXNzJztcbmltcG9ydCB0eXBlIHsgSGVhZENvbmZpZyB9IGZyb20gJ3ZpdGVwcmVzcyc7XG5cbmltcG9ydCB7IHJlc29sdmUgfSBmcm9tICdub2RlOnBhdGgnO1xuXG5pbXBvcnQge1xuICB2aXRlQXJjaGl2ZXJQbHVnaW4sXG4gIHZpdGVWeGVUYWJsZUltcG9ydHNQbHVnaW4sXG59IGZyb20gJ0B2YmVuL3ZpdGUtY29uZmlnJztcblxuaW1wb3J0IHtcbiAgR2l0Q2hhbmdlbG9nLFxuICBHaXRDaGFuZ2Vsb2dNYXJrZG93blNlY3Rpb24sXG59IGZyb20gJ0Bub2xlYmFzZS92aXRlcHJlc3MtcGx1Z2luLWdpdC1jaGFuZ2Vsb2cvdml0ZSc7XG5pbXBvcnQgdGFpbHdpbmQgZnJvbSAndGFpbHdpbmRjc3MnO1xuaW1wb3J0IHsgZGVmaW5lQ29uZmlnLCBwb3N0Y3NzSXNvbGF0ZVN0eWxlcyB9IGZyb20gJ3ZpdGVwcmVzcyc7XG5pbXBvcnQge1xuICBncm91cEljb25NZFBsdWdpbixcbiAgZ3JvdXBJY29uVml0ZVBsdWdpbixcbn0gZnJvbSAndml0ZXByZXNzLXBsdWdpbi1ncm91cC1pY29ucyc7XG5cbmltcG9ydCB7IGRlbW9QcmV2aWV3UGx1Z2luIH0gZnJvbSAnLi9wbHVnaW5zL2RlbW8tcHJldmlldyc7XG5pbXBvcnQgeyBzZWFyY2ggYXMgemhTZWFyY2ggfSBmcm9tICcuL3poLm10cyc7XG5cbmV4cG9ydCBjb25zdCBzaGFyZWQgPSBkZWZpbmVDb25maWcoe1xuICBhcHBlYXJhbmNlOiAnZGFyaycsXG4gIGhlYWQ6IGhlYWQoKSxcbiAgbWFya2Rvd246IHtcbiAgICBwcmVDb25maWcobWQpIHtcbiAgICAgIG1kLnVzZShkZW1vUHJldmlld1BsdWdpbik7XG4gICAgICBtZC51c2UoZ3JvdXBJY29uTWRQbHVnaW4pO1xuICAgIH0sXG4gIH0sXG4gIHB3YTogcHdhKCksXG4gIHNyY0RpcjogJ3NyYycsXG4gIHRoZW1lQ29uZmlnOiB7XG4gICAgaTE4blJvdXRpbmc6IHRydWUsXG4gICAgbG9nbzogJ2h0dHBzOi8vdW5wa2cuY29tL0B2YmVuanMvc3RhdGljLXNvdXJjZUAwLjEuNy9zb3VyY2UvbG9nby12MS53ZWJwJyxcbiAgICBzZWFyY2g6IHtcbiAgICAgIG9wdGlvbnM6IHtcbiAgICAgICAgbG9jYWxlczoge1xuICAgICAgICAgIC4uLnpoU2VhcmNoLFxuICAgICAgICB9LFxuICAgICAgfSxcbiAgICAgIHByb3ZpZGVyOiAnbG9jYWwnLFxuICAgIH0sXG4gICAgc2l0ZVRpdGxlOiAnVmJlbiBBZG1pbicsXG4gICAgc29jaWFsTGlua3M6IFtcbiAgICAgIHsgaWNvbjogJ2dpdGh1YicsIGxpbms6ICdodHRwczovL2dpdGh1Yi5jb20vdmJlbmpzL3Z1ZS12YmVuLWFkbWluJyB9LFxuICAgIF0sXG4gIH0sXG4gIHRpdGxlOiAnVmJlbiBBZG1pbicsXG4gIHZpdGU6IHtcbiAgICBidWlsZDoge1xuICAgICAgY2h1bmtTaXplV2FybmluZ0xpbWl0OiBJbmZpbml0eSxcbiAgICAgIG1pbmlmeTogJ3RlcnNlcicsXG4gICAgfSxcbiAgICBjc3M6IHtcbiAgICAgIHBvc3Rjc3M6IHtcbiAgICAgICAgcGx1Z2luczogW1xuICAgICAgICAgIHRhaWx3aW5kKCksXG4gICAgICAgICAgcG9zdGNzc0lzb2xhdGVTdHlsZXMoeyBpbmNsdWRlRmlsZXM6IFsvdnAtZG9jXFwuY3NzL10gfSksXG4gICAgICAgIF0sXG4gICAgICB9LFxuICAgICAgcHJlcHJvY2Vzc29yT3B0aW9uczoge1xuICAgICAgICBzY3NzOiB7XG4gICAgICAgICAgYXBpOiAnbW9kZXJuJyxcbiAgICAgICAgfSxcbiAgICAgIH0sXG4gICAgfSxcbiAgICBqc29uOiB7XG4gICAgICBzdHJpbmdpZnk6IHRydWUsXG4gICAgfSxcbiAgICBwbHVnaW5zOiBbXG4gICAgICBHaXRDaGFuZ2Vsb2coe1xuICAgICAgICBtYXBBdXRob3JzOiBbXG4gICAgICAgICAge1xuICAgICAgICAgICAgbWFwQnlOYW1lQWxpYXNlczogWydWYmVuJ10sXG4gICAgICAgICAgICBuYW1lOiAndmJlbicsXG4gICAgICAgICAgICB1c2VybmFtZTogJ2FubmN3YicsXG4gICAgICAgICAgfSxcbiAgICAgICAgICB7XG4gICAgICAgICAgICBuYW1lOiAndmluY2UnLFxuICAgICAgICAgICAgdXNlcm5hbWU6ICd2aW5jZTI5MjAwNycsXG4gICAgICAgICAgfSxcbiAgICAgICAgICB7XG4gICAgICAgICAgICBuYW1lOiAnTGkgS3VpJyxcbiAgICAgICAgICAgIHVzZXJuYW1lOiAnbGlrdWk2MjgnLFxuICAgICAgICAgIH0sXG4gICAgICAgIF0sXG4gICAgICAgIHJlcG9VUkw6ICgpID0+ICdodHRwczovL2dpdGh1Yi5jb20vdmJlbmpzL3Z1ZS12YmVuLWFkbWluJyxcbiAgICAgIH0pLFxuICAgICAgR2l0Q2hhbmdlbG9nTWFya2Rvd25TZWN0aW9uKCksXG4gICAgICB2aXRlQXJjaGl2ZXJQbHVnaW4oeyBvdXRwdXREaXI6ICcudml0ZXByZXNzJyB9KSxcbiAgICAgIGdyb3VwSWNvblZpdGVQbHVnaW4oKSxcbiAgICAgIGF3YWl0IHZpdGVWeGVUYWJsZUltcG9ydHNQbHVnaW4oKSxcbiAgICBdLFxuICAgIHNlcnZlcjoge1xuICAgICAgZnM6IHtcbiAgICAgICAgYWxsb3c6IFsnLi4vLi4nXSxcbiAgICAgIH0sXG4gICAgICBob3N0OiB0cnVlLFxuICAgICAgcG9ydDogNjE3MyxcbiAgICB9LFxuXG4gICAgc3NyOiB7XG4gICAgICBleHRlcm5hbDogWydAdnVlL3JlcGwnXSxcbiAgICB9LFxuICB9LFxufSk7XG5cbmZ1bmN0aW9uIGhlYWQoKTogSGVhZENvbmZpZ1tdIHtcbiAgcmV0dXJuIFtcbiAgICBbJ21ldGEnLCB7IGNvbnRlbnQ6ICdWYmVuanMgVGVhbScsIG5hbWU6ICdhdXRob3InIH1dLFxuICAgIFtcbiAgICAgICdtZXRhJyxcbiAgICAgIHtcbiAgICAgICAgY29udGVudDogJ3ZiZW4sIHZpdGVqcywgdml0ZSwgc2hhY2RuLXVpLCB2dWUnLFxuICAgICAgICBuYW1lOiAna2V5d29yZHMnLFxuICAgICAgfSxcbiAgICBdLFxuICAgIFsnbGluaycsIHsgaHJlZjogJy9mYXZpY29uLmljbycsIHJlbDogJ2ljb24nLCB0eXBlOiAnaW1hZ2Uvc3ZnK3htbCcgfV0sXG4gICAgW1xuICAgICAgJ21ldGEnLFxuICAgICAge1xuICAgICAgICBjb250ZW50OlxuICAgICAgICAgICd3aWR0aD1kZXZpY2Utd2lkdGgsaW5pdGlhbC1zY2FsZT0xLG1pbmltdW0tc2NhbGU9MS4wLG1heGltdW0tc2NhbGU9MS4wLHVzZXItc2NhbGFibGU9bm8nLFxuICAgICAgICBuYW1lOiAndmlld3BvcnQnLFxuICAgICAgfSxcbiAgICBdLFxuICAgIFsnbWV0YScsIHsgY29udGVudDogJ3ZiZW4gYWRtaW4gZG9jcycsIG5hbWU6ICdrZXl3b3JkcycgfV0sXG4gICAgWydsaW5rJywgeyBocmVmOiAnL2Zhdmljb24uaWNvJywgcmVsOiAnaWNvbicgfV0sXG4gICAgLy8gW1xuICAgIC8vICAgJ3NjcmlwdCcsXG4gICAgLy8gICB7XG4gICAgLy8gICAgIHNyYzogJ2h0dHBzOi8vY2RuLnRhaWx3aW5kY3NzLmNvbScsXG4gICAgLy8gICB9LFxuICAgIC8vIF0sXG4gIF07XG59XG5cbmZ1bmN0aW9uIHB3YSgpOiBQd2FPcHRpb25zIHtcbiAgcmV0dXJuIHtcbiAgICBpbmNsdWRlTWFuaWZlc3RJY29uczogZmFsc2UsXG4gICAgbWFuaWZlc3Q6IHtcbiAgICAgIGRlc2NyaXB0aW9uOlxuICAgICAgICAnVmJlbiBBZG1pbiBpcyBhIG1vZGVybiBhZG1pbiBkYXNoYm9hcmQgdGVtcGxhdGUgYmFzZWQgb24gVnVlIDMuICcsXG4gICAgICBpY29uczogW1xuICAgICAgICB7XG4gICAgICAgICAgc2l6ZXM6ICcxOTJ4MTkyJyxcbiAgICAgICAgICBzcmM6ICdodHRwczovL3VucGtnLmNvbS9AdmJlbmpzL3N0YXRpYy1zb3VyY2VAMC4xLjcvc291cmNlL3B3YS1pY29uLTE5Mi5wbmcnLFxuICAgICAgICAgIHR5cGU6ICdpbWFnZS9wbmcnLFxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgc2l6ZXM6ICc1MTJ4NTEyJyxcbiAgICAgICAgICBzcmM6ICdodHRwczovL3VucGtnLmNvbS9AdmJlbmpzL3N0YXRpYy1zb3VyY2VAMC4xLjcvc291cmNlL3B3YS1pY29uLTUxMi5wbmcnLFxuICAgICAgICAgIHR5cGU6ICdpbWFnZS9wbmcnLFxuICAgICAgICB9LFxuICAgICAgXSxcbiAgICAgIGlkOiAnLycsXG4gICAgICBuYW1lOiAnVmJlbiBBZG1pbiBEb2MnLFxuICAgICAgc2hvcnRfbmFtZTogJ3ZiZW5fYWRtaW5fZG9jJyxcbiAgICAgIHRoZW1lX2NvbG9yOiAnI2ZmZmZmZicsXG4gICAgfSxcbiAgICBvdXREaXI6IHJlc29sdmUocHJvY2Vzcy5jd2QoKSwgJy52aXRlcHJlc3MvZGlzdCcpLFxuICAgIHJlZ2lzdGVyVHlwZTogJ2F1dG9VcGRhdGUnLFxuICAgIHdvcmtib3g6IHtcbiAgICAgIGdsb2JQYXR0ZXJuczogWycqKi8qLntjc3MsanMsaHRtbCxzdmcscG5nLGljbyx0eHQsd29mZjJ9J10sXG4gICAgICBtYXhpbXVtRmlsZVNpemVUb0NhY2hlSW5CeXRlczogNSAqIDEwMjQgKiAxMDI0LFxuICAgIH0sXG4gIH07XG59XG4iLCAiY29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2Rpcm5hbWUgPSBcIkQ6XFxcXFRhcmUtd29ya3NwYWNlXFxcXHBtLWRpcmVjdG9yXFxcXHVpLXZiZW5cXFxcZG9jc1xcXFwudml0ZXByZXNzXFxcXGNvbmZpZ1xcXFxwbHVnaW5zXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJEOlxcXFxUYXJlLXdvcmtzcGFjZVxcXFxwbS1kaXJlY3RvclxcXFx1aS12YmVuXFxcXGRvY3NcXFxcLnZpdGVwcmVzc1xcXFxjb25maWdcXFxccGx1Z2luc1xcXFxkZW1vLXByZXZpZXcudHNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL0Q6L1RhcmUtd29ya3NwYWNlL3BtLWRpcmVjdG9yL3VpLXZiZW4vZG9jcy8udml0ZXByZXNzL2NvbmZpZy9wbHVnaW5zL2RlbW8tcHJldmlldy50c1wiO2ltcG9ydCB0eXBlIHsgTWFya2Rvd25FbnYsIE1hcmtkb3duUmVuZGVyZXIgfSBmcm9tICd2aXRlcHJlc3MnO1xuXG5pbXBvcnQgY3J5cHRvIGZyb20gJ25vZGU6Y3J5cHRvJztcbmltcG9ydCB7IHJlYWRkaXJTeW5jIH0gZnJvbSAnbm9kZTpmcyc7XG5pbXBvcnQgeyBqb2luIH0gZnJvbSAnbm9kZTpwYXRoJztcblxuZXhwb3J0IGNvbnN0IHJhd1BhdGhSZWdleHAgPVxuICAvLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgcmVnZXhwL25vLXN1cGVyLWxpbmVhci1iYWNrdHJhY2tpbmcsIHJlZ2V4cC9zdHJpY3RcbiAgL14oLis/KD86XFwuKFtcXGRhLXpdKykpPykoI1tcXHctXSspPyg/OiA/eyhcXGQrKD86WywtXVxcZCspKik/ID8oXFxTKyk/fSk/ID8oPzpcXFsoLispXSk/JC87XG5cbmZ1bmN0aW9uIHJhd1BhdGhUb1Rva2VuKHJhd1BhdGg6IHN0cmluZykge1xuICBjb25zdCBbXG4gICAgZmlsZXBhdGggPSAnJyxcbiAgICBleHRlbnNpb24gPSAnJyxcbiAgICByZWdpb24gPSAnJyxcbiAgICBsaW5lcyA9ICcnLFxuICAgIGxhbmcgPSAnJyxcbiAgICByYXdUaXRsZSA9ICcnLFxuICBdID0gKHJhd1BhdGhSZWdleHAuZXhlYyhyYXdQYXRoKSB8fCBbXSkuc2xpY2UoMSk7XG5cbiAgY29uc3QgdGl0bGUgPSByYXdUaXRsZSB8fCBmaWxlcGF0aC5zcGxpdCgnLycpLnBvcCgpIHx8ICcnO1xuXG4gIHJldHVybiB7IGV4dGVuc2lvbiwgZmlsZXBhdGgsIGxhbmcsIGxpbmVzLCByZWdpb24sIHRpdGxlIH07XG59XG5cbmV4cG9ydCBjb25zdCBkZW1vUHJldmlld1BsdWdpbiA9IChtZDogTWFya2Rvd25SZW5kZXJlcikgPT4ge1xuICBtZC5jb3JlLnJ1bGVyLmFmdGVyKCdpbmxpbmUnLCAnZGVtby1wcmV2aWV3JywgKHN0YXRlKSA9PiB7XG4gICAgY29uc3QgaW5zZXJ0Q29tcG9uZW50SW1wb3J0ID0gKGltcG9ydFN0cmluZzogc3RyaW5nKSA9PiB7XG4gICAgICBjb25zdCBpbmRleCA9IHN0YXRlLnRva2Vucy5maW5kSW5kZXgoXG4gICAgICAgIChpKSA9PiBpLnR5cGUgPT09ICdodG1sX2Jsb2NrJyAmJiBpLmNvbnRlbnQubWF0Y2goLzxzY3JpcHQgc2V0dXA+L2cpLFxuICAgICAgKTtcbiAgICAgIGlmIChpbmRleCA9PT0gLTEpIHtcbiAgICAgICAgY29uc3QgaW1wb3J0Q29tcG9uZW50ID0gbmV3IHN0YXRlLlRva2VuKCdodG1sX2Jsb2NrJywgJycsIDApO1xuICAgICAgICBpbXBvcnRDb21wb25lbnQuY29udGVudCA9IGA8c2NyaXB0IHNldHVwPlxcbiR7aW1wb3J0U3RyaW5nfVxcbjwvc2NyaXB0PlxcbmA7XG4gICAgICAgIHN0YXRlLnRva2Vucy5zcGxpY2UoMCwgMCwgaW1wb3J0Q29tcG9uZW50KTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIGlmIChzdGF0ZS50b2tlbnNbaW5kZXhdKSB7XG4gICAgICAgICAgY29uc3QgY29udGVudCA9IHN0YXRlLnRva2Vuc1tpbmRleF0uY29udGVudDtcbiAgICAgICAgICBzdGF0ZS50b2tlbnNbaW5kZXhdLmNvbnRlbnQgPSBjb250ZW50LnJlcGxhY2UoXG4gICAgICAgICAgICAnPC9zY3JpcHQ+JyxcbiAgICAgICAgICAgIGAke2ltcG9ydFN0cmluZ31cXG48L3NjcmlwdD5gLFxuICAgICAgICAgICk7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9O1xuICAgIC8vIERlZmluZSB0aGUgcmVndWxhciBleHByZXNzaW9uIHRvIG1hdGNoIHRoZSBkZXNpcmVkIHBhdHRlcm5cbiAgICBjb25zdCByZWdleCA9IC88RGVtb1ByZXZpZXdbXj5dKlxcc2Rpcj1cIihbXlwiXSopXCIvZztcbiAgICAvLyBJdGVyYXRlIHRocm91Z2ggdGhlIE1hcmtkb3duIGNvbnRlbnQgYW5kIHJlcGxhY2UgdGhlIHBhdHRlcm5cbiAgICBzdGF0ZS5zcmMgPSBzdGF0ZS5zcmMucmVwbGFjZUFsbChyZWdleCwgKF9tYXRjaCwgZGlyKSA9PiB7XG4gICAgICBjb25zdCBjb21wb25lbnREaXIgPSBqb2luKHByb2Nlc3MuY3dkKCksICdzcmMnLCBkaXIpLnJlcGxhY2VBbGwoXG4gICAgICAgICdcXFxcJyxcbiAgICAgICAgJy8nLFxuICAgICAgKTtcblxuICAgICAgbGV0IGNoaWxkRmlsZXM6IHN0cmluZ1tdID0gW107XG4gICAgICBsZXQgZGlyRXhpc3RzID0gdHJ1ZTtcblxuICAgICAgdHJ5IHtcbiAgICAgICAgY2hpbGRGaWxlcyA9XG4gICAgICAgICAgcmVhZGRpclN5bmMoY29tcG9uZW50RGlyLCB7XG4gICAgICAgICAgICBlbmNvZGluZzogJ3V0ZjgnLFxuICAgICAgICAgICAgcmVjdXJzaXZlOiBmYWxzZSxcbiAgICAgICAgICAgIHdpdGhGaWxlVHlwZXM6IGZhbHNlLFxuICAgICAgICAgIH0pIHx8IFtdO1xuICAgICAgfSBjYXRjaCB7XG4gICAgICAgIGRpckV4aXN0cyA9IGZhbHNlO1xuICAgICAgfVxuXG4gICAgICBpZiAoIWRpckV4aXN0cykge1xuICAgICAgICByZXR1cm4gJyc7XG4gICAgICB9XG5cbiAgICAgIGNvbnN0IHVuaXF1ZVdvcmQgPSBnZW5lcmF0ZUNvbnRlbnRIYXNoKGNvbXBvbmVudERpcik7XG5cbiAgICAgIGNvbnN0IENvbXBvbmVudE5hbWUgPSBgRGVtb0NvbXBvbmVudF8ke3VuaXF1ZVdvcmR9YDtcbiAgICAgIGluc2VydENvbXBvbmVudEltcG9ydChcbiAgICAgICAgYGltcG9ydCAke0NvbXBvbmVudE5hbWV9IGZyb20gJyR7Y29tcG9uZW50RGlyfS9pbmRleC52dWUnYCxcbiAgICAgICk7XG4gICAgICBjb25zdCB7IHBhdGg6IF9wYXRoIH0gPSBzdGF0ZS5lbnYgYXMgTWFya2Rvd25FbnY7XG5cbiAgICAgIGNvbnN0IGluZGV4ID0gc3RhdGUudG9rZW5zLmZpbmRJbmRleCgoaSkgPT4gaS5jb250ZW50Lm1hdGNoKHJlZ2V4KSk7XG5cbiAgICAgIGlmICghc3RhdGUudG9rZW5zW2luZGV4XSkge1xuICAgICAgICByZXR1cm4gJyc7XG4gICAgICB9XG4gICAgICBjb25zdCBmaXJzdFN0cmluZyA9ICdpbmRleC52dWUnO1xuICAgICAgY2hpbGRGaWxlcyA9IGNoaWxkRmlsZXMudG9Tb3J0ZWQoKGEsIGIpID0+IHtcbiAgICAgICAgaWYgKGEgPT09IGZpcnN0U3RyaW5nKSByZXR1cm4gLTE7XG4gICAgICAgIGlmIChiID09PSBmaXJzdFN0cmluZykgcmV0dXJuIDE7XG4gICAgICAgIHJldHVybiBhLmxvY2FsZUNvbXBhcmUoYiwgJ2VuJywgeyBzZW5zaXRpdml0eTogJ2Jhc2UnIH0pO1xuICAgICAgfSk7XG4gICAgICBzdGF0ZS50b2tlbnNbaW5kZXhdLmNvbnRlbnQgPVxuICAgICAgICBgPERlbW9QcmV2aWV3IGZpbGVzPVwiJHtlbmNvZGVVUklDb21wb25lbnQoSlNPTi5zdHJpbmdpZnkoY2hpbGRGaWxlcykpfVwiID48JHtDb21wb25lbnROYW1lfS8+XG4gICAgICAgIGA7XG5cbiAgICAgIGNvbnN0IF9kdW1teVRva2VuID0gbmV3IHN0YXRlLlRva2VuKCcnLCAnJywgMCk7XG4gICAgICBjb25zdCB0b2tlbkFycmF5OiBBcnJheTx0eXBlb2YgX2R1bW15VG9rZW4+ID0gW107XG4gICAgICBjaGlsZEZpbGVzLmZvckVhY2goKGZpbGVuYW1lKSA9PiB7XG4gICAgICAgIC8vIGNvbnN0IHNsb3ROYW1lID0gZmlsZW5hbWUucmVwbGFjZShleHRuYW1lKGZpbGVuYW1lKSwgJycpO1xuXG4gICAgICAgIGNvbnN0IHRlbXBsYXRlU3RhcnQgPSBuZXcgc3RhdGUuVG9rZW4oJ2h0bWxfaW5saW5lJywgJycsIDApO1xuICAgICAgICB0ZW1wbGF0ZVN0YXJ0LmNvbnRlbnQgPSBgPHRlbXBsYXRlICMke2ZpbGVuYW1lfT5gO1xuICAgICAgICB0b2tlbkFycmF5LnB1c2godGVtcGxhdGVTdGFydCk7XG5cbiAgICAgICAgY29uc3QgcmVzb2x2ZWRQYXRoID0gam9pbihjb21wb25lbnREaXIsIGZpbGVuYW1lKTtcblxuICAgICAgICBjb25zdCB7IGV4dGVuc2lvbiwgZmlsZXBhdGgsIGxhbmcsIGxpbmVzLCB0aXRsZSB9ID1cbiAgICAgICAgICByYXdQYXRoVG9Ub2tlbihyZXNvbHZlZFBhdGgpO1xuICAgICAgICAvLyBBZGQgY29kZSB0b2tlbnMgZm9yIGVhY2ggbGluZVxuICAgICAgICBjb25zdCB0b2tlbiA9IG5ldyBzdGF0ZS5Ub2tlbignZmVuY2UnLCAnY29kZScsIDApO1xuICAgICAgICB0b2tlbi5pbmZvID0gYCR7bGFuZyB8fCBleHRlbnNpb259JHtsaW5lcyA/IGB7JHtsaW5lc319YCA6ICcnfSR7XG4gICAgICAgICAgdGl0bGUgPyBgWyR7dGl0bGV9XWAgOiAnJ1xuICAgICAgICB9YDtcblxuICAgICAgICB0b2tlbi5jb250ZW50ID0gYDw8PCAke2ZpbGVwYXRofWA7XG4gICAgICAgICh0b2tlbiBhcyBhbnkpLnNyYyA9IFtyZXNvbHZlZFBhdGhdO1xuICAgICAgICB0b2tlbkFycmF5LnB1c2godG9rZW4pO1xuXG4gICAgICAgIGNvbnN0IHRlbXBsYXRlRW5kID0gbmV3IHN0YXRlLlRva2VuKCdodG1sX2lubGluZScsICcnLCAwKTtcbiAgICAgICAgdGVtcGxhdGVFbmQuY29udGVudCA9ICc8L3RlbXBsYXRlPic7XG4gICAgICAgIHRva2VuQXJyYXkucHVzaCh0ZW1wbGF0ZUVuZCk7XG4gICAgICB9KTtcbiAgICAgIGNvbnN0IGVuZFRhZyA9IG5ldyBzdGF0ZS5Ub2tlbignaHRtbF9pbmxpbmUnLCAnJywgMCk7XG4gICAgICBlbmRUYWcuY29udGVudCA9ICc8L0RlbW9QcmV2aWV3Pic7XG4gICAgICB0b2tlbkFycmF5LnB1c2goZW5kVGFnKTtcblxuICAgICAgc3RhdGUudG9rZW5zLnNwbGljZShpbmRleCArIDEsIDAsIC4uLnRva2VuQXJyYXkpO1xuXG4gICAgICAvLyBjb25zb2xlLmxvZyhcbiAgICAgIC8vICAgc3RhdGUubWQucmVuZGVyZXIucmVuZGVyKHN0YXRlLnRva2Vucywgc3RhdGU/Lm9wdGlvbnMgPz8gW10sIHN0YXRlLmVudiksXG4gICAgICAvLyApO1xuICAgICAgcmV0dXJuICcnO1xuICAgIH0pO1xuICB9KTtcbn07XG5cbmZ1bmN0aW9uIGdlbmVyYXRlQ29udGVudEhhc2goaW5wdXQ6IHN0cmluZywgbGVuZ3RoOiBudW1iZXIgPSAxMCk6IHN0cmluZyB7XG4gIC8vIFx1NEY3Rlx1NzUyOCBTSEEtMjU2IFx1NzUxRlx1NjIxMFx1NTRDOFx1NUUwQ1x1NTAzQ1xuICBjb25zdCBoYXNoID0gY3J5cHRvLmNyZWF0ZUhhc2goJ3NoYTI1NicpLnVwZGF0ZShpbnB1dCkuZGlnZXN0KCdoZXgnKTtcblxuICAvLyBcdTVDMDZcdTU0QzhcdTVFMENcdTUwM0NcdThGNkNcdTYzNjJcdTRFM0EgQmFzZTM2IFx1N0YxNlx1NzgwMVx1RkYwQ1x1NUU3Nlx1NTNENlx1NjMwN1x1NUI5QVx1OTU3Rlx1NUVBNlx1NzY4NFx1NUI1N1x1N0IyNlx1NEY1Q1x1NEUzQVx1N0VEM1x1Njc5Q1xuICByZXR1cm4gTnVtYmVyLnBhcnNlSW50KGhhc2gsIDE2KS50b1N0cmluZygzNikuc2xpY2UoMCwgbGVuZ3RoKTtcbn1cbiIsICJjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZGlybmFtZSA9IFwiRDpcXFxcVGFyZS13b3Jrc3BhY2VcXFxccG0tZGlyZWN0b3JcXFxcdWktdmJlblxcXFxkb2NzXFxcXC52aXRlcHJlc3NcXFxcY29uZmlnXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJEOlxcXFxUYXJlLXdvcmtzcGFjZVxcXFxwbS1kaXJlY3RvclxcXFx1aS12YmVuXFxcXGRvY3NcXFxcLnZpdGVwcmVzc1xcXFxjb25maWdcXFxcemgubXRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9EOi9UYXJlLXdvcmtzcGFjZS9wbS1kaXJlY3Rvci91aS12YmVuL2RvY3MvLnZpdGVwcmVzcy9jb25maWcvemgubXRzXCI7aW1wb3J0IHR5cGUgeyBEZWZhdWx0VGhlbWUgfSBmcm9tICd2aXRlcHJlc3MnO1xuXG5pbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlcHJlc3MnO1xuXG5pbXBvcnQgeyB2ZXJzaW9uIH0gZnJvbSAnLi4vLi4vLi4vcGFja2FnZS5qc29uJztcblxuZXhwb3J0IGNvbnN0IHpoID0gZGVmaW5lQ29uZmlnKHtcbiAgZGVzY3JpcHRpb246ICdWYmVuIEFkbWluICYgXHU0RjAxXHU0RTFBXHU3RUE3XHU3QkExXHU3NDA2XHU3Q0ZCXHU3RURGXHU2ODQ2XHU2N0I2JyxcbiAgbGFuZzogJ3poLUhhbnMnLFxuICB0aGVtZUNvbmZpZzoge1xuICAgIGRhcmtNb2RlU3dpdGNoTGFiZWw6ICdcdTRFM0JcdTk4OTgnLFxuICAgIGRhcmtNb2RlU3dpdGNoVGl0bGU6ICdcdTUyMDdcdTYzNjJcdTUyMzBcdTZERjFcdTgyNzJcdTZBMjFcdTVGMEYnLFxuICAgIGRvY0Zvb3Rlcjoge1xuICAgICAgbmV4dDogJ1x1NEUwQlx1NEUwMFx1OTg3NScsXG4gICAgICBwcmV2OiAnXHU0RTBBXHU0RTAwXHU5ODc1JyxcbiAgICB9LFxuICAgIGVkaXRMaW5rOiB7XG4gICAgICBwYXR0ZXJuOlxuICAgICAgICAnaHR0cHM6Ly9naXRodWIuY29tL3ZiZW5qcy92dWUtdmJlbi1hZG1pbi9lZGl0L21haW4vZG9jcy9zcmMvOnBhdGgnLFxuICAgICAgdGV4dDogJ1x1NTcyOCBHaXRIdWIgXHU0RTBBXHU3RjE2XHU4RjkxXHU2QjY0XHU5ODc1XHU5NzYyJyxcbiAgICB9LFxuICAgIGZvb3Rlcjoge1xuICAgICAgY29weXJpZ2h0OiBgQ29weXJpZ2h0IFx1MDBBOSAyMDIwLSR7bmV3IERhdGUoKS5nZXRGdWxsWWVhcigpfSBWYmVuYCxcbiAgICAgIG1lc3NhZ2U6ICdcdTU3RkFcdTRFOEUgTUlUIFx1OEJCOFx1NTNFRlx1NTNEMVx1NUUwMy4nLFxuICAgIH0sXG4gICAgbGFuZ01lbnVMYWJlbDogJ1x1NTkxQVx1OEJFRFx1OEEwMCcsXG4gICAgbGFzdFVwZGF0ZWQ6IHtcbiAgICAgIGZvcm1hdE9wdGlvbnM6IHtcbiAgICAgICAgZGF0ZVN0eWxlOiAnc2hvcnQnLFxuICAgICAgICB0aW1lU3R5bGU6ICdtZWRpdW0nLFxuICAgICAgfSxcbiAgICAgIHRleHQ6ICdcdTY3MDBcdTU0MEVcdTY2RjRcdTY1QjBcdTRFOEUnLFxuICAgIH0sXG4gICAgbGlnaHRNb2RlU3dpdGNoVGl0bGU6ICdcdTUyMDdcdTYzNjJcdTUyMzBcdTZENDVcdTgyNzJcdTZBMjFcdTVGMEYnLFxuICAgIG5hdjogbmF2KCksXG5cbiAgICBvdXRsaW5lOiB7XG4gICAgICBsYWJlbDogJ1x1OTg3NVx1OTc2Mlx1NUJGQ1x1ODIyQScsXG4gICAgfSxcbiAgICByZXR1cm5Ub1RvcExhYmVsOiAnXHU1NkRFXHU1MjMwXHU5ODc2XHU5MEU4JyxcblxuICAgIHNpZGViYXI6IHtcbiAgICAgICcvY29tbWVyY2lhbC8nOiB7IGJhc2U6ICcvY29tbWVyY2lhbC8nLCBpdGVtczogc2lkZWJhckNvbW1lcmNpYWwoKSB9LFxuICAgICAgJy9jb21wb25lbnRzLyc6IHsgYmFzZTogJy9jb21wb25lbnRzLycsIGl0ZW1zOiBzaWRlYmFyQ29tcG9uZW50cygpIH0sXG4gICAgICAnL2d1aWRlLyc6IHsgYmFzZTogJy9ndWlkZS8nLCBpdGVtczogc2lkZWJhckd1aWRlKCkgfSxcbiAgICB9LFxuICAgIHNpZGViYXJNZW51TGFiZWw6ICdcdTgzRENcdTUzNTUnLFxuICB9LFxufSk7XG5cbmZ1bmN0aW9uIHNpZGViYXJHdWlkZSgpOiBEZWZhdWx0VGhlbWUuU2lkZWJhckl0ZW1bXSB7XG4gIHJldHVybiBbXG4gICAge1xuICAgICAgY29sbGFwc2VkOiBmYWxzZSxcbiAgICAgIHRleHQ6ICdcdTdCODBcdTRFQ0InLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAge1xuICAgICAgICAgIGxpbms6ICdpbnRyb2R1Y3Rpb24vdmJlbicsXG4gICAgICAgICAgdGV4dDogJ1x1NTE3M1x1NEU4RSBWYmVuIEFkbWluJyxcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIGxpbms6ICdpbnRyb2R1Y3Rpb24vd2h5JyxcbiAgICAgICAgICB0ZXh0OiAnXHU0RTNBXHU0RUMwXHU0RTQ4XHU5MDA5XHU2MkU5XHU2MjExXHU0RUVDPycsXG4gICAgICAgIH0sXG4gICAgICAgIHsgbGluazogJ2ludHJvZHVjdGlvbi9xdWljay1zdGFydCcsIHRleHQ6ICdcdTVGRUJcdTkwMUZcdTVGMDBcdTU5Q0InIH0sXG4gICAgICAgIHsgbGluazogJ2ludHJvZHVjdGlvbi90aGluJywgdGV4dDogJ1x1N0NCRVx1N0I4MFx1NzI0OFx1NjcyQycgfSxcbiAgICAgICAge1xuICAgICAgICAgIGJhc2U6ICcvJyxcbiAgICAgICAgICBsaW5rOiAnY29tcG9uZW50cy9pbnRyb2R1Y3Rpb24nLFxuICAgICAgICAgIHRleHQ6ICdcdTdFQzRcdTRFRjZcdTY1ODdcdTY4NjMnLFxuICAgICAgICB9LFxuICAgICAgXSxcbiAgICB9LFxuICAgIHtcbiAgICAgIHRleHQ6ICdcdTU3RkFcdTc4NDAnLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAgeyBsaW5rOiAnZXNzZW50aWFscy9jb25jZXB0JywgdGV4dDogJ1x1NTdGQVx1Nzg0MFx1Njk4Mlx1NUZGNScgfSxcbiAgICAgICAgeyBsaW5rOiAnZXNzZW50aWFscy9kZXZlbG9wbWVudCcsIHRleHQ6ICdcdTY3MkNcdTU3MzBcdTVGMDBcdTUzRDEnIH0sXG4gICAgICAgIHsgbGluazogJ2Vzc2VudGlhbHMvcm91dGUnLCB0ZXh0OiAnXHU4REVGXHU3NTMxXHU1NDhDXHU4M0RDXHU1MzU1JyB9LFxuICAgICAgICB7IGxpbms6ICdlc3NlbnRpYWxzL3NldHRpbmdzJywgdGV4dDogJ1x1OTE0RFx1N0Y2RScgfSxcbiAgICAgICAgeyBsaW5rOiAnZXNzZW50aWFscy9pY29ucycsIHRleHQ6ICdcdTU2RkVcdTY4MDcnIH0sXG4gICAgICAgIHsgbGluazogJ2Vzc2VudGlhbHMvc3R5bGVzJywgdGV4dDogJ1x1NjgzN1x1NUYwRicgfSxcbiAgICAgICAgeyBsaW5rOiAnZXNzZW50aWFscy9leHRlcm5hbC1tb2R1bGUnLCB0ZXh0OiAnXHU1OTE2XHU5MEU4XHU2QTIxXHU1NzU3JyB9LFxuICAgICAgICB7IGxpbms6ICdlc3NlbnRpYWxzL2J1aWxkJywgdGV4dDogJ1x1Njc4NFx1NUVGQVx1NEUwRVx1OTBFOFx1N0Y3MicgfSxcbiAgICAgICAgeyBsaW5rOiAnZXNzZW50aWFscy9zZXJ2ZXInLCB0ZXh0OiAnXHU2NzBEXHU1MkExXHU3QUVGXHU0RUE0XHU0RTkyXHU0RTBFXHU2NTcwXHU2MzZFTW9jaycgfSxcbiAgICAgIF0sXG4gICAgfSxcbiAgICB7XG4gICAgICB0ZXh0OiAnXHU2REYxXHU1MTY1JyxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHsgbGluazogJ2luLWRlcHRoL2xvZ2luJywgdGV4dDogJ1x1NzY3Qlx1NUY1NScgfSxcbiAgICAgICAgLy8geyBsaW5rOiAnaW4tZGVwdGgvbGF5b3V0JywgdGV4dDogJ1x1NUUwM1x1NUM0MCcgfSxcbiAgICAgICAgeyBsaW5rOiAnaW4tZGVwdGgvdGhlbWUnLCB0ZXh0OiAnXHU0RTNCXHU5ODk4JyB9LFxuICAgICAgICB7IGxpbms6ICdpbi1kZXB0aC9hY2Nlc3MnLCB0ZXh0OiAnXHU2NzQzXHU5NjUwJyB9LFxuICAgICAgICB7IGxpbms6ICdpbi1kZXB0aC9sb2NhbGUnLCB0ZXh0OiAnXHU1NkZEXHU5NjQ1XHU1MzE2JyB9LFxuICAgICAgICB7IGxpbms6ICdpbi1kZXB0aC9mZWF0dXJlcycsIHRleHQ6ICdcdTVFMzhcdTc1MjhcdTUyOUZcdTgwRkQnIH0sXG4gICAgICAgIHsgbGluazogJ2luLWRlcHRoL2NoZWNrLXVwZGF0ZXMnLCB0ZXh0OiAnXHU2OEMwXHU2N0U1XHU2NkY0XHU2NUIwJyB9LFxuICAgICAgICB7IGxpbms6ICdpbi1kZXB0aC9sb2FkaW5nJywgdGV4dDogJ1x1NTE2OFx1NUM0MGxvYWRpbmcnIH0sXG4gICAgICAgIHsgbGluazogJ2luLWRlcHRoL3VpLWZyYW1ld29yaycsIHRleHQ6ICdcdTdFQzRcdTRFRjZcdTVFOTNcdTUyMDdcdTYzNjInIH0sXG4gICAgICBdLFxuICAgIH0sXG4gICAge1xuICAgICAgdGV4dDogJ1x1NURFNVx1N0EwQicsXG4gICAgICBpdGVtczogW1xuICAgICAgICB7IGxpbms6ICdwcm9qZWN0L3N0YW5kYXJkJywgdGV4dDogJ1x1ODlDNFx1ODMwMycgfSxcbiAgICAgICAgeyBsaW5rOiAncHJvamVjdC9jbGknLCB0ZXh0OiAnQ0xJJyB9LFxuICAgICAgICB7IGxpbms6ICdwcm9qZWN0L2RpcicsIHRleHQ6ICdcdTc2RUVcdTVGNTVcdThCRjRcdTY2MEUnIH0sXG4gICAgICAgIHsgbGluazogJ3Byb2plY3QvdGVzdCcsIHRleHQ6ICdcdTUzNTVcdTUxNDNcdTZENEJcdThCRDUnIH0sXG4gICAgICAgIHsgbGluazogJ3Byb2plY3QvdGFpbHdpbmRjc3MnLCB0ZXh0OiAnVGFpbHdpbmQgQ1NTJyB9LFxuICAgICAgICB7IGxpbms6ICdwcm9qZWN0L2NoYW5nZXNldCcsIHRleHQ6ICdDaGFuZ2VzZXQnIH0sXG4gICAgICAgIHsgbGluazogJ3Byb2plY3Qvdml0ZScsIHRleHQ6ICdWaXRlIENvbmZpZycgfSxcbiAgICAgIF0sXG4gICAgfSxcbiAgICB7XG4gICAgICB0ZXh0OiAnXHU1MTc2XHU0RUQ2JyxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHsgbGluazogJ290aGVyL3Byb2plY3QtdXBkYXRlJywgdGV4dDogJ1x1OTg3OVx1NzZFRVx1NjZGNFx1NjVCMCcgfSxcbiAgICAgICAgeyBsaW5rOiAnb3RoZXIvcmVtb3ZlLWNvZGUnLCB0ZXh0OiAnXHU3OUZCXHU5NjY0XHU0RUUzXHU3ODAxJyB9LFxuICAgICAgICB7IGxpbms6ICdvdGhlci9mYXEnLCB0ZXh0OiAnXHU1RTM4XHU4OUMxXHU5NUVFXHU5ODk4JyB9LFxuICAgICAgXSxcbiAgICB9LFxuICBdO1xufVxuXG5mdW5jdGlvbiBzaWRlYmFyQ29tbWVyY2lhbCgpOiBEZWZhdWx0VGhlbWUuU2lkZWJhckl0ZW1bXSB7XG4gIHJldHVybiBbXG4gICAge1xuICAgICAgbGluazogJ2NvbW11bml0eScsXG4gICAgICB0ZXh0OiAnXHU0RUE0XHU2RDQxXHU3RkE0JyxcbiAgICB9LFxuICAgIHtcbiAgICAgIGxpbms6ICd0ZWNobmljYWwtc3VwcG9ydCcsXG4gICAgICB0ZXh0OiAnXHU2MjgwXHU2NzJGXHU2NTJGXHU2MzAxJyxcbiAgICB9LFxuICAgIHtcbiAgICAgIGxpbms6ICdjdXN0b21pemVkJyxcbiAgICAgIHRleHQ6ICdcdTVCOUFcdTUyMzZcdTVGMDBcdTUzRDEnLFxuICAgIH0sXG4gIF07XG59XG5cbmZ1bmN0aW9uIHNpZGViYXJDb21wb25lbnRzKCk6IERlZmF1bHRUaGVtZS5TaWRlYmFySXRlbVtdIHtcbiAgcmV0dXJuIFtcbiAgICB7XG4gICAgICB0ZXh0OiAnXHU3RUM0XHU0RUY2JyxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBsaW5rOiAnaW50cm9kdWN0aW9uJyxcbiAgICAgICAgICB0ZXh0OiAnXHU0RUNCXHU3RUNEJyxcbiAgICAgICAgfSxcbiAgICAgIF0sXG4gICAgfSxcbiAgICB7XG4gICAgICBjb2xsYXBzZWQ6IGZhbHNlLFxuICAgICAgdGV4dDogJ1x1NUUwM1x1NUM0MFx1N0VDNFx1NEVGNicsXG4gICAgICBpdGVtczogW1xuICAgICAgICB7XG4gICAgICAgICAgbGluazogJ2xheW91dC11aS9wYWdlJyxcbiAgICAgICAgICB0ZXh0OiAnUGFnZSBcdTk4NzVcdTk3NjInLFxuICAgICAgICB9LFxuICAgICAgXSxcbiAgICB9LFxuICAgIHtcbiAgICAgIGNvbGxhcHNlZDogZmFsc2UsXG4gICAgICB0ZXh0OiAnXHU5MDFBXHU3NTI4XHU3RUM0XHU0RUY2JyxcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBsaW5rOiAnY29tbW9uLXVpL3ZiZW4tYXBpLWNvbXBvbmVudCcsXG4gICAgICAgICAgdGV4dDogJ0FwaUNvbXBvbmVudCBBcGlcdTdFQzRcdTRFRjZcdTUzMDVcdTg4QzVcdTU2NjgnLFxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgbGluazogJ2NvbW1vbi11aS92YmVuLWFsZXJ0JyxcbiAgICAgICAgICB0ZXh0OiAnQWxlcnQgXHU4RjdCXHU5MUNGXHU2M0QwXHU3OTNBXHU2ODQ2JyxcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIGxpbms6ICdjb21tb24tdWkvdmJlbi1tb2RhbCcsXG4gICAgICAgICAgdGV4dDogJ01vZGFsIFx1NkEyMVx1NjAwMVx1Njg0NicsXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBsaW5rOiAnY29tbW9uLXVpL3ZiZW4tZHJhd2VyJyxcbiAgICAgICAgICB0ZXh0OiAnRHJhd2VyIFx1NjJCRFx1NUM0OScsXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBsaW5rOiAnY29tbW9uLXVpL3ZiZW4tZm9ybScsXG4gICAgICAgICAgdGV4dDogJ0Zvcm0gXHU4ODY4XHU1MzU1JyxcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIGxpbms6ICdjb21tb24tdWkvdmJlbi12eGUtdGFibGUnLFxuICAgICAgICAgIHRleHQ6ICdWeGUgVGFibGUgXHU4ODY4XHU2ODNDJyxcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIGxpbms6ICdjb21tb24tdWkvdmJlbi1jb3VudC10by1hbmltYXRvcicsXG4gICAgICAgICAgdGV4dDogJ0NvdW50VG9BbmltYXRvciBcdTY1NzBcdTVCNTdcdTUyQThcdTc1M0InLFxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgbGluazogJ2NvbW1vbi11aS92YmVuLWVsbGlwc2lzLXRleHQnLFxuICAgICAgICAgIHRleHQ6ICdFbGxpcHNpc1RleHQgXHU3NzAxXHU3NTY1XHU2NTg3XHU2NzJDJyxcbiAgICAgICAgfSxcbiAgICAgIF0sXG4gICAgfSxcbiAgXTtcbn1cblxuZnVuY3Rpb24gbmF2KCk6IERlZmF1bHRUaGVtZS5OYXZJdGVtW10ge1xuICByZXR1cm4gW1xuICAgIHtcbiAgICAgIGFjdGl2ZU1hdGNoOiAnXi8oZ3VpZGV8Y29tcG9uZW50cykvJyxcbiAgICAgIHRleHQ6ICdcdTY1ODdcdTY4NjMnLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAge1xuICAgICAgICAgIGFjdGl2ZU1hdGNoOiAnXi9ndWlkZS8nLFxuICAgICAgICAgIGxpbms6ICcvZ3VpZGUvaW50cm9kdWN0aW9uL3ZiZW4nLFxuICAgICAgICAgIHRleHQ6ICdcdTYzMDdcdTUzNTcnLFxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgYWN0aXZlTWF0Y2g6ICdeL2NvbXBvbmVudHMvJyxcbiAgICAgICAgICBsaW5rOiAnL2NvbXBvbmVudHMvaW50cm9kdWN0aW9uJyxcbiAgICAgICAgICB0ZXh0OiAnXHU3RUM0XHU0RUY2JyxcbiAgICAgICAgfSxcbiAgICAgICAge1xuICAgICAgICAgIHRleHQ6ICdcdTUzODZcdTUzRjJcdTcyNDhcdTY3MkMnLFxuICAgICAgICAgIGl0ZW1zOiBbXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgIGxpbms6ICdodHRwczovL2RvYy52dmJpbi5jbicsXG4gICAgICAgICAgICAgIHRleHQ6ICcyLnhcdTcyNDhcdTY3MkNcdTY1ODdcdTY4NjMnLFxuICAgICAgICAgICAgfSxcbiAgICAgICAgICBdLFxuICAgICAgICB9LFxuICAgICAgXSxcbiAgICB9LFxuICAgIHtcbiAgICAgIHRleHQ6ICdcdTZGMTRcdTc5M0EnLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAge1xuICAgICAgICAgIHRleHQ6ICdWYmVuIEFkbWluJyxcbiAgICAgICAgICBpdGVtczogW1xuICAgICAgICAgICAge1xuICAgICAgICAgICAgICBsaW5rOiAnaHR0cHM6Ly93d3cudmJlbi5wcm8nLFxuICAgICAgICAgICAgICB0ZXh0OiAnXHU2RjE0XHU3OTNBXHU3MjQ4XHU2NzJDJyxcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgIGxpbms6ICdodHRwczovL2FudC52YmVuLnBybycsXG4gICAgICAgICAgICAgIHRleHQ6ICdBbnQgRGVzaWduIFZ1ZSBcdTcyNDhcdTY3MkMnLFxuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgbGluazogJ2h0dHBzOi8vbmFpdmUudmJlbi5wcm8nLFxuICAgICAgICAgICAgICB0ZXh0OiAnTmFpdmUgXHU3MjQ4XHU2NzJDJyxcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgIGxpbms6ICdodHRwczovL2VsZS52YmVuLnBybycsXG4gICAgICAgICAgICAgIHRleHQ6ICdFbGVtZW50IFBsdXNcdTcyNDhcdTY3MkMnLFxuICAgICAgICAgICAgfSxcbiAgICAgICAgICBdLFxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgdGV4dDogJ1x1NTE3Nlx1NEVENicsXG4gICAgICAgICAgaXRlbXM6IFtcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgbGluazogJ2h0dHBzOi8vdmJlbi52dmJpbi5jbicsXG4gICAgICAgICAgICAgIHRleHQ6ICdWYmVuIEFkbWluIDIueCcsXG4gICAgICAgICAgICB9LFxuICAgICAgICAgIF0sXG4gICAgICAgIH0sXG4gICAgICBdLFxuICAgIH0sXG4gICAge1xuICAgICAgdGV4dDogdmVyc2lvbixcbiAgICAgIGl0ZW1zOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBsaW5rOiAnaHR0cHM6Ly9naXRodWIuY29tL3ZiZW5qcy92dWUtdmJlbi1hZG1pbi9yZWxlYXNlcycsXG4gICAgICAgICAgdGV4dDogJ1x1NjZGNFx1NjVCMFx1NjVFNVx1NUZENycsXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBsaW5rOiAnaHR0cHM6Ly9naXRodWIuY29tL29yZ3MvdmJlbmpzL3Byb2plY3RzLzUnLFxuICAgICAgICAgIHRleHQ6ICdcdThERUZcdTdFQkZcdTU2RkUnLFxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgbGluazogJ2h0dHBzOi8vZ2l0aHViLmNvbS92YmVuanMvdnVlLXZiZW4tYWRtaW4vYmxvYi9tYWluLy5naXRodWIvY29udHJpYnV0aW5nLm1kJyxcbiAgICAgICAgICB0ZXh0OiAnXHU4RDIxXHU3MzJFJyxcbiAgICAgICAgfSxcbiAgICAgIF0sXG4gICAgfSxcbiAgICB7XG4gICAgICBsaW5rOiAnL2NvbW1lcmNpYWwvdGVjaG5pY2FsLXN1cHBvcnQnLFxuICAgICAgdGV4dDogJ1x1RDgzRVx1REQ4NCBcdTYyODBcdTY3MkZcdTY1MkZcdTYzMDEnLFxuICAgIH0sXG4gICAge1xuICAgICAgbGluazogJy9zcG9uc29yL3BlcnNvbmFsJyxcbiAgICAgIHRleHQ6ICdcdTI3MjggXHU4RDVFXHU1MkE5JyxcbiAgICB9LFxuICAgIHtcbiAgICAgIGxpbms6ICcvY29tbWVyY2lhbC9jb21tdW5pdHknLFxuICAgICAgdGV4dDogJ1x1RDgzRFx1REM2OFx1MjAwRFx1RDgzRFx1REM2Nlx1MjAwRFx1RDgzRFx1REM2NiBcdTRFQTRcdTZENDFcdTdGQTQnLFxuICAgICAgLy8gaXRlbXM6IFtcbiAgICAgIC8vICAge1xuICAgICAgLy8gICAgIGxpbms6ICdodHRwczovL3F1bi5xcS5jb20vcXF3ZWIvcXVucHJvL3NoYXJlP193dj0zJl93d3Y9MTI4JmFwcENoYW5uZWw9c2hhcmUmaW52aXRlQ29kZT0yMnlTemo3cEtpdyZidXNpbmVzc1R5cGU9OSZmcm9tPTI0NjYxMCZiaXo9a2EmbWFpblNvdXJjZUlkPXNoYXJlJnN1YlNvdXJjZUlkPW90aGVycyZqdW1wc291cmNlPXNob3J0dXJsIy9wYycsXG4gICAgICAvLyAgICAgdGV4dDogJ1FRXHU5ODkxXHU5MDUzJyxcbiAgICAgIC8vICAgfSxcbiAgICAgIC8vICAge1xuICAgICAgLy8gICAgIGxpbms6ICdodHRwczovL3FtLnFxLmNvbS9jZ2ktYmluL3FtL3FyP193dj0xMDI3Jms9bWpabWxoZ1Z6elV4dmR4bGxCNkMxdkhwWDhPOFFSTDAmYXV0aEtleT1EQmRGYkJ3RVJtZmFLWTk1SnZSV3FMQ0pJUkdKQW1LeVpicnB6WjQxRUtETVo1U1I2TWZiak9CYWFOUk43M2ZyJm5vdmVyaWZ5PTAmZ3JvdXBfY29kZT00Mjg2MTA5JyxcbiAgICAgIC8vICAgICB0ZXh0OiAnUVFcdTdGQTQnLFxuICAgICAgLy8gICB9LFxuICAgICAgLy8gICB7XG4gICAgICAvLyAgICAgbGluazogJ2h0dHBzOi8vZGlzY29yZC5nZy9WVTYyalRlY2FkJyxcbiAgICAgIC8vICAgICB0ZXh0OiAnRGlzY29yZCcsXG4gICAgICAvLyAgIH0sXG4gICAgICAvLyBdLFxuICAgIH0sXG4gICAgLy8ge1xuICAgIC8vICAgbGluazogJy9mcmllbmQtbGlua3MvJyxcbiAgICAvLyAgIHRleHQ6ICdcdUQ4M0VcdUREMUQgXHU1M0NCXHU2MEM1XHU5NEZFXHU2M0E1JyxcbiAgICAvLyB9LFxuICBdO1xufVxuXG5leHBvcnQgY29uc3Qgc2VhcmNoOiBEZWZhdWx0VGhlbWUuQWxnb2xpYVNlYXJjaE9wdGlvbnNbJ2xvY2FsZXMnXSA9IHtcbiAgcm9vdDoge1xuICAgIHBsYWNlaG9sZGVyOiAnXHU2NDFDXHU3RDIyXHU2NTg3XHU2ODYzJyxcbiAgICB0cmFuc2xhdGlvbnM6IHtcbiAgICAgIGJ1dHRvbjoge1xuICAgICAgICBidXR0b25BcmlhTGFiZWw6ICdcdTY0MUNcdTdEMjJcdTY1ODdcdTY4NjMnLFxuICAgICAgICBidXR0b25UZXh0OiAnXHU2NDFDXHU3RDIyXHU2NTg3XHU2ODYzJyxcbiAgICAgIH0sXG4gICAgICBtb2RhbDoge1xuICAgICAgICBlcnJvclNjcmVlbjoge1xuICAgICAgICAgIGhlbHBUZXh0OiAnXHU0RjYwXHU1M0VGXHU4MEZEXHU5NzAwXHU4OTgxXHU2OEMwXHU2N0U1XHU0RjYwXHU3Njg0XHU3RjUxXHU3RURDXHU4RkRFXHU2M0E1JyxcbiAgICAgICAgICB0aXRsZVRleHQ6ICdcdTY1RTBcdTZDRDVcdTgzQjdcdTUzRDZcdTdFRDNcdTY3OUMnLFxuICAgICAgICB9LFxuICAgICAgICBmb290ZXI6IHtcbiAgICAgICAgICBjbG9zZVRleHQ6ICdcdTUxNzNcdTk1RUQnLFxuICAgICAgICAgIG5hdmlnYXRlVGV4dDogJ1x1NTIwN1x1NjM2MicsXG4gICAgICAgICAgc2VhcmNoQnlUZXh0OiAnXHU2NDFDXHU3RDIyXHU2M0QwXHU0RjlCXHU4MDA1JyxcbiAgICAgICAgICBzZWxlY3RUZXh0OiAnXHU5MDA5XHU2MkU5JyxcbiAgICAgICAgfSxcbiAgICAgICAgbm9SZXN1bHRzU2NyZWVuOiB7XG4gICAgICAgICAgbm9SZXN1bHRzVGV4dDogJ1x1NjVFMFx1NkNENVx1NjI3RVx1NTIzMFx1NzZGOFx1NTE3M1x1N0VEM1x1Njc5QycsXG4gICAgICAgICAgcmVwb3J0TWlzc2luZ1Jlc3VsdHNMaW5rVGV4dDogJ1x1NzBCOVx1NTFGQlx1NTNDRFx1OTk4OCcsXG4gICAgICAgICAgcmVwb3J0TWlzc2luZ1Jlc3VsdHNUZXh0OiAnXHU0RjYwXHU4QkE0XHU0RTNBXHU4QkU1XHU2N0U1XHU4QkUyXHU1RTk0XHU4QkU1XHU2NzA5XHU3RUQzXHU2NzlDXHVGRjFGJyxcbiAgICAgICAgICBzdWdnZXN0ZWRRdWVyeVRleHQ6ICdcdTRGNjBcdTUzRUZcdTRFRTVcdTVDMURcdThCRDVcdTY3RTVcdThCRTInLFxuICAgICAgICB9LFxuICAgICAgICBzZWFyY2hCb3g6IHtcbiAgICAgICAgICBjYW5jZWxCdXR0b25BcmlhTGFiZWw6ICdcdTUzRDZcdTZEODgnLFxuICAgICAgICAgIGNhbmNlbEJ1dHRvblRleHQ6ICdcdTUzRDZcdTZEODgnLFxuICAgICAgICAgIHJlc2V0QnV0dG9uQXJpYUxhYmVsOiAnXHU2RTA1XHU5NjY0XHU2N0U1XHU4QkUyXHU2NzYxXHU0RUY2JyxcbiAgICAgICAgICByZXNldEJ1dHRvblRpdGxlOiAnXHU2RTA1XHU5NjY0XHU2N0U1XHU4QkUyXHU2NzYxXHU0RUY2JyxcbiAgICAgICAgfSxcbiAgICAgICAgc3RhcnRTY3JlZW46IHtcbiAgICAgICAgICBmYXZvcml0ZVNlYXJjaGVzVGl0bGU6ICdcdTY1MzZcdTg1Q0YnLFxuICAgICAgICAgIG5vUmVjZW50U2VhcmNoZXNUZXh0OiAnXHU2Q0ExXHU2NzA5XHU2NDFDXHU3RDIyXHU1Mzg2XHU1M0YyJyxcbiAgICAgICAgICByZWNlbnRTZWFyY2hlc1RpdGxlOiAnXHU2NDFDXHU3RDIyXHU1Mzg2XHU1M0YyJyxcbiAgICAgICAgICByZW1vdmVGYXZvcml0ZVNlYXJjaEJ1dHRvblRpdGxlOiAnXHU0RUNFXHU2NTM2XHU4NUNGXHU0RTJEXHU3OUZCXHU5NjY0JyxcbiAgICAgICAgICByZW1vdmVSZWNlbnRTZWFyY2hCdXR0b25UaXRsZTogJ1x1NEVDRVx1NjQxQ1x1N0QyMlx1NTM4Nlx1NTNGMlx1NEUyRFx1NzlGQlx1OTY2NCcsXG4gICAgICAgICAgc2F2ZVJlY2VudFNlYXJjaEJ1dHRvblRpdGxlOiAnXHU0RkREXHU1QjU4XHU4MUYzXHU2NDFDXHU3RDIyXHU1Mzg2XHU1M0YyJyxcbiAgICAgICAgfSxcbiAgICAgIH0sXG4gICAgfSxcbiAgfSxcbn07XG4iXSwKICAibWFwcGluZ3MiOiAiO0FBQTBXLFNBQVMsZUFBZTtBQUNsWSxTQUFTLDZCQUE2Qjs7O0FDQ3RDLFNBQVMsb0JBQW9COzs7QUNBM0IsY0FBVzs7O0FESU4sSUFBTSxLQUFLLGFBQWE7QUFBQSxFQUM3QixhQUFhO0FBQUEsRUFDYixNQUFNO0FBQUEsRUFDTixhQUFhO0FBQUEsSUFDWCxxQkFBcUI7QUFBQSxJQUNyQixxQkFBcUI7QUFBQSxJQUNyQixXQUFXO0FBQUEsTUFDVCxNQUFNO0FBQUEsTUFDTixNQUFNO0FBQUEsSUFDUjtBQUFBLElBQ0EsVUFBVTtBQUFBLE1BQ1IsU0FDRTtBQUFBLE1BQ0YsTUFBTTtBQUFBLElBQ1I7QUFBQSxJQUNBLFFBQVE7QUFBQSxNQUNOLFdBQVcsd0JBQW9CLG9CQUFJLEtBQUssR0FBRSxZQUFZLENBQUM7QUFBQSxNQUN2RCxTQUFTO0FBQUEsSUFDWDtBQUFBLElBQ0EsZUFBZTtBQUFBLElBQ2YsYUFBYTtBQUFBLE1BQ1gsZUFBZTtBQUFBLFFBQ2IsV0FBVztBQUFBLFFBQ1gsV0FBVztBQUFBLE1BQ2I7QUFBQSxNQUNBLE1BQU07QUFBQSxJQUNSO0FBQUEsSUFDQSxzQkFBc0I7QUFBQSxJQUN0QixLQUFLLElBQUk7QUFBQSxJQUNULFNBQVM7QUFBQSxNQUNQLE9BQU87QUFBQSxJQUNUO0FBQUEsSUFDQSxrQkFBa0I7QUFBQSxJQUNsQixTQUFTO0FBQUEsTUFDUCxtQkFBbUI7QUFBQSxRQUNqQixNQUFNO0FBQUEsUUFDTixPQUFPLGtCQUFrQjtBQUFBLE1BQzNCO0FBQUEsTUFDQSxjQUFjLEVBQUUsTUFBTSxjQUFjLE9BQU8sYUFBYSxFQUFFO0FBQUEsSUFDNUQ7QUFBQSxFQUNGO0FBQ0YsQ0FBQztBQUVELFNBQVMsZUFBMkM7QUFDbEQsU0FBTztBQUFBLElBQ0w7QUFBQSxNQUNFLFdBQVc7QUFBQSxNQUNYLE1BQU07QUFBQSxNQUNOLE9BQU87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O0FBQUEsVUFDYixNQUFNO0FBQUEsVUFDTixNQUFNO0FBQUEsUUFDUjtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQSxRQU1BO0FBQUEsVUFDRSxNQUFNO0FBQUEsVUFDTixPQUFPO0FBQUEsWUFDTDtBQUFBLGNBQ0UsTUFBTTtBQUFBLGNBQ04sTUFBTTtBQUFBLFlBQ1I7QUFBQSxVQUNGO0FBQUEsUUFDRjtBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUEsSUFDQTtBQUFBLE1BQ0UsTUFBTTtBQUFBLE1BQ04sT0FBTztBQUFBLFFBQ0w7QUFBQSxVQUNFLE1BQU07QUFBQSxVQUNOLE9BQU87QUFBQSxZQUNMO0FBQUEsY0FDRSxNQUFNO0FBQUEsY0FDTixNQUFNO0FBQUEsWUFDUjtBQUFBLFlBQ0E7QUFBQSxjQUNFLE1BQU07QUFBQSxjQUNOLE1BQU07QUFBQSxZQUNSO0FBQUEsWUFDQTtBQUFBLGNBQ0UsTUFBTTtBQUFBLGNBQ04sTUFBTTtBQUFBLFlBQ1I7QUFBQSxZQUNBO0FBQUEsY0FDRSxNQUFNO0FBQUEsY0FDTixNQUFNO0FBQUEsWUFDUjtBQUFBLFVBQ0Y7QUFBQSxRQUNGO0FBQUEsUUFDQTtBQUFBLFVBQ0UsTUFBTTtBQUFBLFVBQ04sT0FBTztBQUFBLFlBQ0w7QUFBQSxjQUNFLE1BQU07QUFBQSxjQUNOLE1BQU07QUFBQSxZQUNSO0FBQUEsVUFDRjtBQUFBLFFBQ0Y7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLE1BQU07QUFBQSxNQUNOLE9BQU87QUFBQSxRQUNMO0FBQUEsVUFDRSxNQUFNO0FBQUEsVUFDTixNQUFNO0FBQUEsUUFDUjtBQUFBLFFBQ0E7QUFBQSxVQUNFLE1BQU07QUFBQSxVQUNOLE1BQU07QUFBQSxRQUNSO0FBQUEsUUFDQTtBQUFBLFVBQ0UsTUFBTTtBQUFBLFVBQ04sTUFBTTtBQUFBLFFBQ1I7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLE1BQU07QUFBQSxNQUNOLE1BQU07QUFBQSxJQUNSO0FBQUEsSUFDQTtBQUFB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QUFNO0FBQUEsVUFDTixNQUFNO0FBQUEsUUFDUjtBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUNGO0FBRUEsU0FBU0QsT0FBOEI7QUFDckMsU0FBTztBQUFBLElBQ0w7QUFBQSxNQUNFLGFBQWE7QUFBQSxNQUNiLE1BQU07QUFBQSxNQUNOLE9BQU87QUFBQSxRQUNMO0FBQUEsVUFDRSxhQUFhO0FBQUEsVUFDYixNQUFNO0FBQUEsVUFDTixNQUFNO0FBQUEsUUFDUjtBQUFBLFFBQ0E7QUFBQSxVQUNFLGFBQWE7QUFBQSxVQUNiLE1BQU07QUFBQSxVQUNOLE1BQU07QUFBQSxRQUNSO0FBQUEsUUFDQTtBQUFBLFVBQ0UsTUFBTTtBQUFBLFVBQ04sT0FBTztBQUFBLFlBQ0w7QUFBQSxjQUNFLE1BQU07QUFBQSxjQUNOLE1BQU07QUFBQSxZQUNSO0FBQUEsVUFDRjtBQUFBLFFBQ0Y7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0E7QUFBQSxNQUNFLE1BQU07QUFBQSxNQUNOLE9BQU87QUFBQSxRQUNMO0FBQUEsVUFDRSxNQUFNO0FBQUEsVUFDTixPQUFPO0FBQUEsWUFDTDtBQUFBLGNBQ0UsTUFBTTtBQUFBLGNBQ04sTUFBTTtBQUFBLFlBQ1I7QUFBQSxZQUNBO0FBQUEsY0FDRSxNQUFNO0FBQUEsY0FDTixNQUFNO0FBQUEsWUFDUjtBQUFBLFlBQ0E7QUFBQSxjQUNFLE1BQU07QUFBQSxjQUNOLE1BQU07QUFBQSxZQUNSO0FBQUEsWUFDQTtBQUFBLGNBQ0UsTUFBTTtBQUFBLGNBQ04sTUFBTTtBQUFBLFlBQ1I7QUFBQSxVQUNGO0FBQUEsUUFDRjtBQUFBLFFBQ0E7QUFBQSxVQUNFLE1BQU07QUFBQSxVQUNOLE9BQU87QUFBQSxZQUNMO0FBQUEsY0FDRSxNQUFNO0FBQUEsY0FDTixNQUFNO0FBQUEsWUFDUjtBQUFBLFVBQ0Y7QUFBQSxRQUNGO0FBQUEsTUFDRjtBQUFBLElBQ0Y7QUFBQSxJQUNBO0FBQUEsTUFDRSxNQUFNO0FBQUEsTUFDTixPQUFPO0FBQUEsUUFDTDtBQUFBLFVBQ0UsTUFB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QUFNLFdBQVcsQ0FBQztBQUFBLElBQ3pELENBQUMsUUFBUSxFQUFFLE1BQU0sZ0JBQWdCLEtBQUssT0FBTyxDQUFDO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUEsRUFPaEQ7QUFDRjtBQUVBLFNBQVMsTUFBa0I7QUFDekIsU0FBTztBQUFBLElBQ0wsc0JBQXNCO0FBQUEsSUFDdEIsVUFBVTtBQUFBLE1BQ1IsYUFDRTtBQUFBLE1BQ0YsT0FBTztBQUFBLFFBQ0w7QUFBQSxVQUNFLE9BQU87QUFBQSxVQUNQLEtBQUs7QUFBQSxVQUNMLE1BQU07QUFBQSxRQUNSO0FBQUEsUUFDQTtBQUFBLFVBQ0UsT0FBTztBQUFBLFVBQ1AsS0FBSztBQUFBLFVBQ0wsTUFBTTtBQUFBLFFBQ1I7QUFBQSxNQUNGO0FBQUEsTUFDQSxJQUFJO0FBQUEsTUFDSixNQUFNO0FBQUEsTUFDTixZQUFZO0FBQUEsTUFDWixhQUFhO0FBQUEsSUFDZjtBQUFBLElBQ0EsUUFBUSxRQUFRLFFBQVEsSUFBSSxHQUFHLGlCQUFpQjtBQUFBLElBQ2hELGNBQWM7QUFBQSxJQUNkLFNBQVM7QUFBQSxNQUNQLGNBQWMsQ0FBQywwQ0FBMEM7QUFBQSxNQUN6RCwrQkFBK0IsSUFBSSxPQUFPO0FBQUEsSUFDNUM7QUFBQSxFQUNGO0FBQ0Y7OztBSHBLQSxJQUFPLGlCQUFRO0FBQUEsRUFDYixzQkFBc0I7QUFBQSxJQUNwQixHQUFHO0FBQUEsSUFDSCxTQUFTO0FBQUEsTUFDUCxJQUFJO0FBQUEsUUFDRixPQUFPO0FBQUEsUUFDUCxNQUFNO0FBQUEsUUFDTixNQUFNO0FBQUEsUUFDTixHQUFHO0FBQUEsTUFDTDtBQUFBLE1BQ0EsTUFBTTtBQUFBLFFBQ0osT0FBTztBQUFBLFFBQ1AsTUFBTTtBQUFBLFFBQ04sR0FBRztBQUFBLE1BQ0w7QUFBQSxJQUNGO0FBQUEsRUFDRixDQUFDO0FBQ0g7IiwKICAibmFtZXMiOiBbImRlZmluZUNvbmZpZyIsICJkZWZpbmVDb25maWciLCAiZGVmaW5lQ29uZmlnIiwgIm5hdiIsICJzaWRlYmFyQ29tbWVyY2lhbCIsICJzaWRlYmFyR3VpZGUiLCAiZGVmaW5lQ29uZmlnIl0KfQo=
