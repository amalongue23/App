<template>
  <main class="admin-layout create-layout">
    <SideNav />

    <section class="content-area create-content">
      <header class="create-topbar">
        <div class="create-top-icons">
          <span class="top-icon"></span>
          <span class="top-icon"></span>
          <span class="top-icon"></span>
        </div>
      </header>

      <section class="create-card">
        <h1 class="create-title">{{ title }}</h1>
        <p class="create-subtitle">{{ subtitle }}</p>
        <slot />
      </section>
    </section>
  </main>
</template>

<script setup>
import SideNav from './SideNav.vue'

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  sectionLabel: { type: String, required: true },
  sectionRoute: { type: String, required: true },
})

// SideNav handles navigation and auth actions.
</script>
