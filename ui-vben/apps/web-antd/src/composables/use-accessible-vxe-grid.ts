import type { Ref } from 'vue';

import { nextTick, onBeforeUnmount, onMounted } from 'vue';

/**
 * 让 VxeTable 的水平滚动容器可以由键盘聚焦，避免读屏与键盘用户无法滚动宽表。
 */
export function useAccessibleVxeGrid(
  container: Ref<HTMLElement | undefined>,
  tableLabel: string,
) {
  let observer: MutationObserver | undefined;

  const updateScrollableRegions = () => {
    const element = container.value;
    if (!element) return;

    const scrollableRegions: ReadonlyArray<readonly [string, string]> = [
      [
        '.vxe-table--header-inner-wrapper',
        `${tableLabel}表头，可使用方向键横向滚动`,
      ],
      ['.vxe-table--body-inner-wrapper', `${tableLabel}内容，可使用方向键滚动`],
    ];

    for (const [selector, label] of scrollableRegions) {
      for (const region of element.querySelectorAll<HTMLElement>(selector)) {
        region.setAttribute('aria-label', label);
        region.setAttribute('role', 'region');
        region.setAttribute('tabindex', '0');
      }
    }
  };

  onMounted(async () => {
    await nextTick();
    updateScrollableRegions();
    if (!container.value) return;

    observer = new MutationObserver(updateScrollableRegions);
    observer.observe(container.value, { childList: true, subtree: true });
  });

  onBeforeUnmount(() => observer?.disconnect());
}
