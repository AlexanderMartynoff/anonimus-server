<template>
  <q-layout view="lHh Lpr lFf" class="bg-white">
    <q-header>
      <toolbar-header>
        <q-btn flat icon="menu" class="q-mr-sm" @click="onBtnMenuClick"/>
      </toolbar-header>
    </q-header>

    <q-drawer bordered side="left" :width="leftBarWidth" :breakpoint="leftBarBreakpoint" v-model="showLeftBar">
      <q-toolbar class="bg-primary text-white">
        <q-toolbar-title>[ contacts ]</q-toolbar-title>
      </q-toolbar>
      <messanger-contact-list @select="onContactSelect"/>
    </q-drawer>

    <q-page-container>
      <messanger-chat :messages="messages" :chat="chat"/>
    </q-page-container>

    <q-footer>
      <q-toolbar>
        <messanger-message-toolbar @send="onBtnSendClick" :chat="chat"/>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script>
import { scroll } from 'quasar'
import { ref, computed, inject, watch, onMounted, onUnmounted, nextTick } from 'vue'
import MessangerChat from './MessangerChat.vue'
import MessangerMessageToolbar from './MessangerMessageToolbar.vue'
import MessangerContactList from './MessangerContactList.vue'
import ToolbarHeader from '../layout/ToolbarHeader.vue'


export default {
  name: 'Messanger',
  components: {
    MessangerChat,
    MessangerMessageToolbar,
    MessangerContactList,
    ToolbarHeader,
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

  setup(props, ctx) {
    const websocket = inject('websocket')

    const showLeftBar = ref(true)
    const leftBarWidth = computed(() => props.leftBarWidth)
    const leftBarBreakpoint = computed(() => props.leftBarBreakpoint)

    const messages = ref([])
    const chat = ref(props.chat)

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
        scroll.setVerticalScrollPosition(window, document.body.scrollHeight - window.innerHeight, 500)
      })
    })

    return {
      showLeftBar,
      leftBarWidth,
      leftBarBreakpoint,
      messages,
      chat,

      onContactSelect(contact) {
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
