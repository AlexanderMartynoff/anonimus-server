<template>
  <q-layout view="lHh Lpr lFf" class="bg-white">
    <q-header>
      <q-toolbar>
        <q-btn flat icon="menu" class="q-mr-sm" @click="onBtnMenuClick"/>
        <q-toolbar-title>Anonimus</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-drawer bordered side="left" :width="leftBarWidth" :breakpoint="leftBarBreakpoint" v-model="showLeftBar">
      <q-toolbar class="bg-primary text-white">
        <q-toolbar-title>Contacts</q-toolbar-title>
      </q-toolbar>
      <messanger-contact-list @select="onContactSelect"/>
    </q-drawer>

    <q-page-container>
      <messanger-chat :messages="messages"/>
    </q-page-container>

    <q-footer>
      <q-toolbar>
        <messanger-message-toolbar @send="onBtnSendClick"/>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script>
import { ref, computed, inject, reactive, onMounted, onUnmounted } from 'vue'
import MessangerChat from './MessangerChat.vue'
import MessangerMessageToolbar from './MessangerMessageToolbar.vue'
import MessangerContactList from './MessangerContactList.vue'


export default {
  name: 'Messanger',
  components: {
    MessangerChat,
    MessangerMessageToolbar,
    MessangerContactList,
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
  },

  setup(props) {
    const websocket = inject('websocket')
    const uuid = inject('uuid')

    const showLeftBar = ref(true)
    const leftBarWidth = computed(() => props.leftBarWidth)
    const leftBarBreakpoint = computed(() => props.leftBarBreakpoint)

    const messages = reactive([])

    let chanel = null

    onMounted(() => {
      chanel = websocket.subscribe({
        type: 'Subscription',
        id: uuid,
      })
    })

    onUnmounted(() => {
      websocket.unsubscribe(chanel)
    })

    return {
      showLeftBar,
      leftBarWidth,
      leftBarBreakpoint,
      messages,

      onContactSelect(contact) {
        messages = []
      },

      onBtnMenuClick() {
        showLeftBar.value = !showLeftBar.value
      },

      onBtnSendClick(message) {
        messages.push(message)
        websocket.push(message)
      },
    }
  },
}
</script>
