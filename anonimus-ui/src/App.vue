<template>
  <router-view/>
</template>

<script>
import { inject, onMounted, onUnmounted } from 'vue'

export default {
  name: 'App',

  setup () {
    const websocket = inject('websocket')

    onMounted(() => {
      websocket.start()
      websocket.push({type: 'Registration'})
    })

    onUnmounted(() => {
      websocket.stop()
    })
  },
}
</script>
