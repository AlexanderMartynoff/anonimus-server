<template>
  <q-toolbar class="bg-primary text-white">
    <q-tabs v-model="tab" align="center">
      <q-tab name="people" icon="people"/>
    </q-tabs>
  </q-toolbar>

  <q-list separator>
    <q-item v-for="(chat, name) in chats" clickable v-ripple :active="name === activeChatName" active-class="bg-grey-4 text-black" @click="onSelect(chat)">
      <q-item-section avatar>
        <q-avatar color="primary" text-color="white">
          {{chat.letter}}
        </q-avatar>
      </q-item-section>
      <q-item-section>
        {{chat.name}}
      </q-item-section>
    </q-item>
  </q-list>
</template>

<script>
import { computed, ref } from 'vue'

export default {
  name: 'MessangerContactList',
  emits: ['select'],
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
    return {
      tab,
      activeChatName: computed(() => props.activeChatName),
      onSelect(chat) {
        ctx.emit('select', chat)
      },
    }
  },
}
</script>
