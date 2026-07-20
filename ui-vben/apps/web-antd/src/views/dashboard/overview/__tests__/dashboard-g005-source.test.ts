import { existsSync, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const rootSource = readFileSync(
  fileURLToPath(new URL('../index.vue', import.meta.url)),
  'utf8',
)
const typeSource = readFileSync(
  fileURLToPath(new URL('../dashboard-types.ts', import.meta.url)),
  'utf8',
)
const tabsSource = readFileSync(
  fileURLToPath(new URL('../components/dashboard-tabs.vue', import.meta.url)),
  'utf8',
)
const allViewSource = readFileSync(
  fileURLToPath(new URL('../components/all-view.vue', import.meta.url)),
  'utf8',
)
const verificationViewSource = readFileSync(
  fileURLToPath(new URL('../components/DataVerificationView.vue', import.meta.url)),
  'utf8',
)

function componentPath(name: string): string {
  return fileURLToPath(new URL(`../components/${name}`, import.meta.url))
}

describe('G005 dashboard boundary', () => {
  it('keeps the production route independent from the review demo and exposes five views', () => {
    expect(rootSource).not.toContain('Phase3Review')
    expect(rootSource).not.toContain('review=phase3')
    expect(rootSource).not.toContain('phase3-review')

    for (const view of ['all', 'management', 'projects', 'finance']) {
      expect(rootSource).toContain(`activeView === '${view}'`)
      expect(tabsSource).toContain(`key: '${view}'`)
    }
    expect(rootSource).toContain('DataVerificationView v-else')
    expect(typeSource).toContain("'verification'")
    expect(tabsSource).toContain("key: 'verification'")
    expect(rootSource).toContain('window.history.replaceState')
    expect(rootSource).not.toContain('router.replace')
  })

  it('orders the first overview as tasks, risks, credibility, roles, and changes', () => {
    const orderedSections = [
      'DashboardActionQueue',
      'DashboardActionQueue',
      'DashboardDataContract',
      'DashboardRoleSummary',
      'DashboardRecentChanges',
    ]
    let cursor = -1
    for (const section of orderedSections) {
      cursor = allViewSource.indexOf(section, cursor + 1)
      expect(cursor, `${section} was not arranged in the required first-view order`).toBeGreaterThan(-1)
    }

    expect(verificationViewSource).toContain('overview.verification_actions')
    expect(verificationViewSource).toContain('overview.data_contract.metrics')
    expect(readFileSync(componentPath('management-view.vue'), 'utf8')).toContain('overview.risk_actions')
    expect(readFileSync(componentPath('finance-view.vue'), 'utf8')).toContain('financeActions')
  })

  it('owns action queues, data contracts, and recent changes in dedicated production components', () => {
    for (const component of [
      'DashboardActionQueue.vue',
      'DashboardDataContract.vue',
      'DashboardRecentChanges.vue',
      'DashboardRoleSummary.vue',
      'DataVerificationView.vue',
    ]) {
      expect(existsSync(componentPath(component))).toBe(true)
    }
  })
})
