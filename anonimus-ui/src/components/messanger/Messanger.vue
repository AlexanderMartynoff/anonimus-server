<template>
  <q-layout view="lHh Lpr lFf" class="bg-white">
    <q-header>
      <toolbar-header>
        <q-btn flat icon="menu" class="q-mr-sm" @click="onBtnMenuClick"/>
      </toolbar-header>
    </q-header>

    <q-drawer bordered side="left" :width="leftBarWidth" :breakpoint="leftBarBreakpoint" v-model="showLeftBar">
      <q-toolbar class="bg-primary text-white">
        <q-toolbar-title>[ c.o.n.t.a.c.t.s ]</q-toolbar-title>
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
import { v4 } from 'uuid'
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
  },

  setup(props, context) {
    const websocket = inject('websocket')
    const uuid = v4()

    const showLeftBar = ref(true)
    const leftBarWidth = computed(() => props.leftBarWidth)
    const leftBarBreakpoint = computed(() => props.leftBarBreakpoint)

    const messages = ref([])

    onMounted(() => {
      websocket.subscribe('message::income', () => {}, uuid)
    })

    onUnmounted(() => {
      websocket.unsubscribe(uuid)
    })

    return {
      showLeftBar,
      leftBarWidth,
      leftBarBreakpoint,
      messages,

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
