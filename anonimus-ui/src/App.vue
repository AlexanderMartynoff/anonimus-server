<template>
  <router-view/>
</template>

<script>
import { useQuasar } from 'quasar'
import { onUnmounted, onMounted, inject, watch } from 'vue'
import { useStore } from './stores/store.js'


export default {
  name: 'App',

  setup() {
    const websocket = inject('websocket')
    const database = inject('database')

    const quasar = useQuasar()
    const store = useStore()

    watch(store.user, (user) => {
      const name = quasar.cookies.get('id')

      if (name && name == user.name) {
        if (!websocket.active) {
          websocket.start()
        }
        return
      }

      quasar.cookies.set('id', user.name, {sameSite: 'Lax'})

      if (websocket.active) {
        websocket.on('close', () => {
          websocket.start()
        })
        websocket.stop()
      } else {
        websocket.start()
      }
    })

    const onOnlineUsersChange = () => {
      store.fetchOnlineUsers()
    }

    const onMessageIncome = (message) => {
      database.messages.put(message)
    }

    onMounted(() => {
      websocket.on('message', onMessageIncome, false)
      websocket.on('online', onOnlineUsersChange, false)
    })

    onUnmounted(() => {
      websocket.off(onMessageIncome)
      websocket.off(onOnlineUsersChange)
      websocket.stop()
    })
  },
}
</script>
