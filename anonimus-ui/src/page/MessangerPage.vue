<template>
  <q-layout view="lHh Lpr lFf" class="bg-white">
    <q-header>
      <header-toolbar>
        <q-btn flat icon="menu" class="q-mr-sm" @click="onBtnMenuClick"/>
      </header-toolbar>
    </q-header>

    <q-drawer bordered side="left" :breakpoint="leftBarBreakpoint" v-model="showLeftBar">
      <messanger-contact-list @select="onChatSelect" :chats="chats" :active-chat-name="chat"/>
    </q-drawer>

    <q-page-container>
      <messanger-chat :messages="messages" :chat="chat" :user="user"/>
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
    const quasar = useQuasar()
    const websocket = inject('websocket')
    const userStore = useUserStore()
    const chatStore = useChatStore()

    const messages = ref([])
    const showLeftBar = ref(false)

    if (quasar.platform.is.desktop) {
      showLeftBar.value = true
    }

    const leftBarWidth = computed(() => props.leftBarWidth)
    const leftBarBreakpoint = computed(() => props.leftBarBreakpoint)
    const chat = ref(props.chat)

    const user = computed(() => userStore.user)
    const chats = computed(() => chatStore.chats)

    const onMessage = (message) => {
      messages.value.push(message)
    }

    onMounted(() => {
      websocket.on('Message', onMessage, false)
    })

    onUnmounted(() => {
      websocket.off(onMessage)
    })

    watch(messages.value, () => {
      nextTick(() => {
        scroll.setVerticalScrollPosition(window, document.body.scrollHeight - window.innerHeight, 300)
      })
    })

    return {
      showLeftBar,
      leftBarWidth,
      leftBarBreakpoint,
      messages,
      chat,
      chats,
      user,

      onChatSelect({name}) {
        chat.value = name
      },

      onBtnMenuClick() {
        showLeftBar.value = !showLeftBar.value
      },

      onBtnSendClick(message) {
        websocket.push(message)
        messages.value.push(message)
      },
    }
  },
}
</script>
