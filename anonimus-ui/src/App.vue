<template>
  <router-view/>
</template>

<script>
import cookie from 'js-cookie'
import { onMounted, onUnmounted, provide } from 'vue'
import { WebSocketQueue } from './api/websocket.js'
import { v4 } from 'uuid'

export default {
  name: 'App',

  setup () {
    const websocket = new WebSocketQueue(`ws://${location.host}/api/messanger/connect`)

    if (!cookie.get('uuid')) {
      cookie.set('uuid', v4())
    }

    const uuid = cookie.get('uuid')

    onMounted(() => {
      websocket.start()
    })

    onUnmounted(() => {
      websocket.stop()
    })

    websocket.on('Open', () => {
      websocket.subscribe([uuid, 'Message', 'Online'])
    }, false)

    provide('websocket', websocket)
    provide('uuid', uuid)
  },
}
</script>
