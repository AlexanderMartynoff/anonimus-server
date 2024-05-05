<template>
  <q-layout view="lHh Lpr lFf" class="bg-white">
    <q-header>
      <header-toolbar>
        <q-btn flat icon="menu" @click="onBtnMenuClick"/>
        <q-btn flat icon="home" @click="onHomeClick"/>
      </header-toolbar>
    </q-header>

    <q-drawer bordered side="left" :breakpoint="690" v-model="leftBar">
      <messanger-chat-list @select="onChatSelect" @delete="onChatDelete" :chats="chats" :active-chat-name="chat.id"/>
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
import { ref, computed, inject, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '../stores/store.js'
import { useLiveQuery } from '../api/vue.js'
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

    const leftBar = ref(quasar.platform.is.desktop)
    const limit = ref(10)

    const chats = useLiveQuery(() => database.chats.toArray())
    const chat = computed(() => chats.value.filter(chat => chat.id == props.chat).pop(0) || {id: 'nil'})

    const messages = useLiveQuery(() => {
      return database.messages
        .orderBy('sequence')
        .filter(message => message.chat == chat.value.id)
        .reverse()
        .limit(limit.value)
        .toArray()
        .then(messages => messages.reverse())
    }, {
      depends: [chat, limit],
    })

    const user = computed(() => store.user)

    watch(messages, () => {
      nextTick(() => {
        scroll.setVerticalScrollPosition(window, document.body.scrollHeight - window.innerHeight, 0)
      })
    }, {immediate: true})

    async function onBtnSendClick(message) {
      const sequence = await database.messages.where('chat')
        .equals(chat.value.id)
        .limit(1)
        .reverse()
        .sortBy('sequence')
        .then(messages => messages.pop(0)?.sequence || 0)

      Object.assign(message, {
        sequence: sequence + 1,
        chat: chat.value.id,
        sender: store.user.name,
        receiver: chat.value.receiver,
      })

      await database.messages.add(message).then(() => {
        websocket.push({
          type: 'message',
          message,
        })
      })
    }

    return {
      leftBar,
      messages,
      chat,
      chats,
      user,

      onChatScrollTop(index, onDone) {
        limit.value += 10
        onDone()
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
        leftBar.value = !leftBar.value
      },

      onBtnSendClick,
    }
  },
}
</script>
