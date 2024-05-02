<template>
  <q-toolbar class="bg-primary text-white">
    <q-tabs v-model="tab" align="center">
      <q-tab name="people" icon="people"/>
    </q-tabs>
  </q-toolbar>

  <q-list separator>
    <q-item v-for="chat in chats" :key="chat.id" clickable v-ripple :active="chat.id === activeChatName" active-class="bg-grey-4 text-black" @click="onSelect(chat)">
      <q-item-section avatar>
        <q-avatar color="primary" text-color="white">
          {{chat.letter}}
        </q-avatar>
      </q-item-section>

      <q-item-section>
        {{chat.name}}
      </q-item-section>

      <q-item-section side>
        <q-btn flat dense round icon="delete" @click.stop="onDeleteClick(chat)"/>
      </q-item-section>
    </q-item>
  </q-list>

  <q-dialog v-model="confirm" persistent>
    <q-card class="bg-primary text-white">
      <q-card-section>
        <span class="q-ml-sm">Are you sure?</span>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Yes" color="primary" v-close-popup class="text-white" @click.stop="onDeleteOkClick()"/>
        <q-btn flat label="No" color="primary" v-close-popup class="text-white"/>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import { computed, ref } from 'vue'

export default {
  name: 'MessangerChatList',
  emits: ['select', 'delete'],
  props: {
    chats: {
      type: Object,
    },
    activeChatName: {
      type: String,
    },
  },

  setup(props, ctx) {
    const tab = ref('people')
    const confirm = ref(false)
    const deletedChat = ref(null)

    return {
      confirm,
      tab,

      onSelect(chat) {
        ctx.emit('select', chat)
      },

      onDeleteOkClick() {
        ctx.emit('delete', deletedChat.value)
      },

      onDeleteClick(chat) {
        deletedChat.value = chat
        confirm.value = true
      },
    }
  },
}
</script>
