<script lang="ts" setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue';

defineOptions({ inheritAttrs: false });

const props = defineProps<{
  /** 为 Ant Design Vue 生成的组合框补充稳定的可访问名称。 */
  label: string;
}>();

const selectRef = ref<null | { $el?: HTMLElement }>(null);
let observer: MutationObserver | undefined;

function updateComboboxAria() {
  const root = selectRef.value?.$el;
  const input = root?.querySelector<HTMLInputElement>(
    '.ant-select-selection-search-input[role="combobox"]',
  );
  if (!root || !input) return;

  const isOpen = root.classList.contains('ant-select-open');
  const listId =
    input.getAttribute('aria-controls') ?? input.getAttribute('aria-owns');
  const list = listId ? document.querySelector(`#${CSS.escape(listId)}`) : null;

  input.setAttribute('aria-label', props.label);
  input.setAttribute('aria-expanded', String(isOpen));
  // Ant Design Vue 4.2.x 在下拉列表未挂载时仍保留引用，
  // 会产生悬空的 aria-controls / aria-activedescendant。
  if (!isOpen || !list) {
    input.removeAttribute('aria-activedescendant');
    input.removeAttribute('aria-controls');
    input.removeAttribute('aria-owns');
    return;
  }

  input.setAttribute('aria-controls', listId!);
  input.removeAttribute('aria-owns');
  const activeId = input.getAttribute('aria-activedescendant');
  if (activeId && !document.querySelector(`#${CSS.escape(activeId)}`)) {
    input.removeAttribute('aria-activedescendant');
  }
}

onMounted(async () => {
  await nextTick();
  updateComboboxAria();
  const root = selectRef.value?.$el;
  if (!root) return;

  observer = new MutationObserver(() => {
    updateComboboxAria();
  });
  observer.observe(root, {
    attributeFilter: ['class'],
    attributes: true,
    childList: true,
    subtree: true,
  });
});

onBeforeUnmount(() => observer?.disconnect());
</script>

<template>
  <a-select ref="selectRef" v-bind="$attrs">
    <slot></slot>
  </a-select>
</template>
