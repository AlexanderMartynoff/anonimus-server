<template>
  <div class="q-pa-md">
    <q-list bordered class="rounded-borders">
      <q-item-label header>Chats</q-item-label>

      <q-item clickable v-ripple v-for="onlineUser in onlineUsers" @click="onSelect(onlineUser)">
        <q-item-section avatar>
          <q-avatar>
            <img src="/static/user.png">
          </q-avatar>
        </q-item-section>

        <q-item-section>
          <q-item-label>{{onlineUser.name}}</q-item-label>
        </q-item-section>
        <q-item-section side>
          1 min ago
        </q-item-section>
      </q-item>

    </q-list>
  </div>
</template>

<script>

export default {
  name: 'OnlineUserList',
  emits: ['select'],

  props: {
    onlineUsers: {
      type: Array,
    },
  },

  setup(_, ctx) {
    return {
      onSelect(onlineUser) {
        ctx.emit('select', onlineUser)
      },
    }
  },
}
</script>
