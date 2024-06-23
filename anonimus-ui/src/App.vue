<template>
  <router-view/>
</template>

<script>
import { Notify } from 'quasar'
import { onUnmounted, onMounted, inject, watch } from 'vue'
import { useStore } from './stores/store.js'


export default {
  name: 'App',

  setup() {
    const websocket = inject('websocket')
    const database = inject('database')

    const store = useStore()

    watch(store.user, user => {
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
      Notify.create({
        message: message.text,
        caption: message.senderName,
        icon: 'mail',
        position: 'top-right',
        multiLine: true,
      })

      database.messages.put(message)
    }

    onMounted(() => {
      websocket.on('message', onMessageIncome, false)
      websocket.on('event', onOnlineUsersChange, false)
    })

    onUnmounted(() => {
      websocket.off(onMessageIncome)
      websocket.off(onOnlineUsersChange)
      websocket.stop()
    })
  },
}
</script>
