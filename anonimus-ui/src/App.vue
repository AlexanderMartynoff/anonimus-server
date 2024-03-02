<template>
  <router-view/>
</template>

<script>
import { useQuasar } from 'quasar'
import { onUnmounted, provide, watch } from 'vue'
import { WebSocketQueue } from './api/websocket.js'
import { useStore as useUserStore } from './stores/user.js'

export default {
  name: 'App',

  setup () {
    const quasar = useQuasar()
    const userStore = useUserStore()

    let ref = quasar.localStorage.getItem('ref')

    if (!ref) {
      ref = '0-0'
    }

    const websocket = new WebSocketQueue(`ws://${location.host}/api/messanger/connect?ref=${ref}`)

    const onConnectionsChange = () => {
      userStore.fetchUsers()
    }

    const onUserChange = (user) => {
      quasar.cookies.set('uuid', user.name, {sameSite: 'Lax'})

      if (websocket.active) {
        websocket.stop()
        websocket.on('Close', () => {
          websocket.start()
        })
        return
      }

      websocket.start()
    }

    watch(userStore.user, (user) => {
      onUserChange(user)
    }, {immediate: true})

    onUnmounted(() => {
      websocket.off(onConnectionsChange)
      websocket.stop()
    })

    websocket.on('Open', () => {
      websocket.subscribe(['Message', 'Online'])
    }, false)

    websocket.on('Any', (record) => {
        if (record.id) {
          quasar.localStorage.set('ref', record.id)
        }
      }, false)

    websocket.on('Online', onConnectionsChange, false)

    provide('websocket', websocket)
  },
}
</script>
