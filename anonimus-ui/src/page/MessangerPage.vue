<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <header-toolbar>
        <q-btn flat icon="menu" @click="onBtnMenuClick"/>
        <q-btn flat icon="home" @click="onHomeClick"/>
      </header-toolbar>
    </q-header>

    <q-drawer bordered side="left" :breakpoint="690" v-model="showLeftBar" elevated>
      <messanger-chat-list @select="onChatSelect" @delete="onChatDelete" :chats="chats" :online-users="onlineUsers" :active-chat-name="chat.id"/>
    </q-drawer>

    <q-page-container>
      <messanger-chat :messages="messages" :chat="chat.id" :user="user" @scroll-top="onChatScrollTop"/>
    </q-page-container>

    <q-footer>
      <q-toolbar>
        <messanger-message-toolbar @send="onBtnSendClick" :chat="chat.id" :user="user"/>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script>
import { scroll, useQuasar } from 'quasar'
import { ref, toRaw, computed, inject, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '../stores/store.js'
import { useLiveQuery } from '../api/vue.js'
import { v4 } from 'uuid'

import MessangerChat from '../components/messanger/MessangerChat.vue'
import MessangerMessageToolbar from '../components/messanger/MessangerMessageToolbar.vue'
import MessangerChatList from '../components/messanger/MessangerChatList.vue'
import HeaderToolbar from '../components/layout/HeaderToolbar.vue'

export default {
  name: 'MessangerPage',
  components: {
    MessangerChat,
    MessangerMessageToolbar,
    MessangerChatList,
    HeaderToolbar,
  },

  props: {
    chat: {
      type: String,
    },
  },

  setup(props) {
    const websocket = inject('websocket')
    const database = inject('database')

    const router = useRouter()
    const quasar = useQuasar()
    const store = useStore()

    const showLeftBar = ref(quasar.platform.is.desktop)

    const limit = ref(50)

    const chats = useLiveQuery(() => database.chats.toArray())
    const chat = computed(() => chats.value.filter(chat => chat.id == props.chat).pop(0) || {id: 'nil'})

    const messages = useLiveQuery(() => {
      return database.messages.where({chat: chat.value.id})
        .reverse()
        .limit(limit.value)
        .toArray()
        .then(messages => {
          return messages.reverse()
        })
    }, {
      depends: [chat, limit],
    })

    const user = computed(() => store.user)
    const onlineUsers = computed(() => store.onlineUsers)

    watch(messages, () => {
      nextTick(() => {
        scroll.setVerticalScrollPosition(window, document.body.scrollHeight - window.innerHeight, 0)
      })
    }, {immediate: true})

    async function onBtnSendClick({text}) {
      database.transaction('rw', database.messages, async () => {
        let sequence = await database.messages.where({chat: chat.value.id})
          .last()
          .then(message => (message?.sequence || 0) + 1)

        const message = {
          id: v4(),
          sequence,
          text,

          chat: chat.value.id,
          chatSubjects: chat.value.users.map(user => user.deviceId),

          senderDeviceId: store.user.deviceId,
          senderId: store.user.id,
          senderName: store.user.name,
        }

        await database.messages.add(message)

        websocket.push({
          type: 'message',
          message,
        })
      })
    }

    return {
      showLeftBar,
      messages,
      chat,
      chats,
      user,
      onlineUsers,

      onChatScrollTop(index, onDone) {
        // limit.value += 10
        // onDone()
      },

      onHomeClick() {
        router.push({name: 'index' })
      },

      onChatSelect({id}) {
        router.push({
          name: 'messanger',
          params: {chat: id},
        })
      },

      async onChatDelete(chat) {
        await database.messages.where('chat').equals(chat.id).delete()
        await database.chats.where('id').equals(chat.id).delete()
      },

      onBtnMenuClick() {
        showLeftBar.value = !showLeftBar.value
      },

      onBtnSendClick,
    }
  },
}
</script>
