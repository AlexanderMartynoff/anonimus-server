<template>
  <router-view/>
</template>

<script>
import { onMounted, onUnmounted, provide } from 'vue'
import { WebSocketQueue } from './api/websocket.js'
import { v4 } from 'uuid'

export default {
  name: 'App',

  setup () {
    const websocket = new WebSocketQueue(`ws://${location.host}/api/messanger/connect`)

    onMounted(() => {
      websocket.start()
      websocket.push({
        type: 'Identify',
        name: v4(),
      })
    })

    onUnmounted(() => {
      websocket.stop()
    })

    provide('websocket', websocket)
  },
}
</script>
