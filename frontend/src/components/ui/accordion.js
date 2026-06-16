/**
 * Accordion Component
 *
 * Collapsible accordion — single or multi-open.
 * Usage: <div x-data="accordion()">
 *
 * @module components/ui/accordion
 */

export function accordion(allowMultiple = false) {
  return {
    activeItems: [],
    allowMultiple,

    toggle(id) {
      const index = this.activeItems.indexOf(id)
      if (index > -1) {
        this.activeItems.splice(index, 1)
      } else {
        if (!this.allowMultiple) this.activeItems = []
        this.activeItems.push(id)
      }
    },

    open(id) {
      if (this.activeItems.includes(id)) return
      if (!this.allowMultiple) this.activeItems = []
      this.activeItems.push(id)
    },

    close(id) {
      const index = this.activeItems.indexOf(id)
      if (index > -1) this.activeItems.splice(index, 1)
    },

    isActive(id) { return this.activeItems.includes(id) },
    closeAll()   { this.activeItems = [] },
  }
}

/**
 * Tabs Component
 *
 * Tab interface with active-tab tracking.
 * Usage: <div x-data="tabs('description')">
 *
 * @module components/ui/tabs
 */
export function tabs(defaultTab = 0) {
  return {
    activeTab: defaultTab,

    selectTab(id)    { this.activeTab = id },
    isActive(id)     { return this.activeTab === id },
    get activeTabId(){ return this.activeTab },
  }
}
