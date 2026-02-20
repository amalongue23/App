<template>
  <div class="app-logo" :class="{ compact }">
    <img v-if="showImage" :src="logoSrc" alt="Unistats" @error="onImageError" />
    <div v-else class="app-logo-fallback">UL</div>
    <div class="app-logo-text">Unistats</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  compact: { type: Boolean, default: false },
})

const showImage = ref(true)
const logoSrc = new URL('../assets/logo uniluanda apenas.png', import.meta.url).href

function onImageError() {
  showImage.value = false
}
</script>
