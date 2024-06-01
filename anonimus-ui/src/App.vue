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

    const store = useStore()

    watch(store.user, (user) => {
      websocket.stop(() => {
        if (user.id) {
          websocket.start()
        }
      })
    }, {immediate: true})

    const onOnlineUsersChange = (event) => {
      store.fetchOnlineUsers()
    }

    const onMessageIncome = ({message}) => {
      database.messages.put(message)
    }

    onMounted(() => {
      websocket.on('message:response', onMessageIncome, false)
      // websocket.on('event:response', onOnlineUsersChange, false)
      onOnlineUsersChange()
    })

    onUnmounted(() => {
      websocket.off(onMessageIncome)
      websocket.off(onOnlineUsersChange)
      websocket.stop()
    })
  },
}
</script>
