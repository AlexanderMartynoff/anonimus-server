<template>
  <router-view/>
</template>

<script>
import { onMounted, onUnmounted, provide } from 'vue'
import { WebSocketQueue } from './api/websocket.js'

export default {
  name: 'App',

  setup () {
    const websocket = new WebSocketQueue(`ws://${location.host}/api/messanger/connect`)

    onMounted(() => {
      websocket.start()
    })

    onUnmounted(() => {
      websocket.stop()
    })

    provide('websocket', websocket)
  },
}
</script>
