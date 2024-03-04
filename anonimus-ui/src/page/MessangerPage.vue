<template>
  <q-layout view="lHh Lpr lFf" class="bg-white">
    <q-header>
      <header-toolbar>
        <q-btn flat icon="menu" @click="onBtnMenuClick()"/>
        <q-btn flat  icon="home" @click="onHomeClick()"/>
      </header-toolbar>
    </q-header>

    <q-drawer bordered side="left" :breakpoint="leftBarBreakpoint" v-model="leftBar">
      <messanger-contact-list @select="onChatSelect" :chats="chats" :active-chat-name="chat"/>
    </q-drawer>

    <q-page-container>
      <messanger-chat :messages="messages" :chat="chat" :user="user" v-if="chat"/>
    </q-page-container>

    <q-footer>
      <q-toolbar>
        <messanger-message-toolbar @send="onBtnSendClick" :chat="chat" :user="user"/>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script>
import { scroll, useQuasar } from 'quasar'
import { ref, computed, inject, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import MessangerChat from '../components/messanger/MessangerChat.vue'
import MessangerMessageToolbar from '../components/messanger/MessangerMessageToolbar.vue'
import MessangerContactList from '../components/messanger/MessangerContactList.vue'
import HeaderToolbar from '../components/layout/HeaderToolbar.vue'
import { useStore as useUserStore } from '../stores/user.js'
import { useStore as useChatStore } from '../stores/chat.js'


export default {
  name: 'MessangerPage',
  components: {
    MessangerChat,
    MessangerMessageToolbar,
    MessangerContactList,
    HeaderToolbar,
  },
  props: {
    leftBarWidth: {
      type: Number,
      default: 350,
    },
    leftBarBreakpoint: {
      type: Number,
      default: 690,
    },
    chat: {
      type: String,
    },
  },

  setup(props) {
    const router = useRouter()
    const quasar = useQuasar()
    const websocket = inject('websocket')
    const userStore = useUserStore()
    const chatStore = useChatStore()

    const messages = computed(() => chatStore.chats[chat.value]?.messages || [])
    const leftBar = ref(false)

    if (quasar.platform.is.desktop) {
      leftBar.value = true
    }

    const leftBarWidth = computed(() => props.leftBarWidth)
    const leftBarBreakpoint = computed(() => props.leftBarBreakpoint)
    const chat = computed(() => props.chat)

    const user = computed(() => userStore.user)
    const chats = computed(() => chatStore.chats)

    const onMessage = (message) => {
      chatStore.pushChatMessage(chat.value, message)
    }

    onMounted(() => {
      websocket.on('Message', onMessage, false)
    })

    onUnmounted(() => {
      websocket.off(onMessage)
    })

    watch([messages, chat], () => {
      nextTick(() => {
        scroll.setVerticalScrollPosition(window, document.body.scrollHeight - window.innerHeight, 0)
      })
    }, {deep: true, immediate: true})

    return {
      leftBar,
      leftBarWidth,
      leftBarBreakpoint,
      messages,
      chat,
      chats,
      user,

      onHomeClick() {
        router.push({ name: 'index' })
      },

      onChatSelect({name}) {
        router.push({
          name: 'messanger',
          params: {chat: name},
        })
      },

      onBtnMenuClick() {
        leftBar.value = !leftBar.value
      },

      onBtnSendClick(message) {
        websocket.push(message)
        chatStore.pushChatMessage(chat.value, message)
      },
    }
  },
}
</script>
