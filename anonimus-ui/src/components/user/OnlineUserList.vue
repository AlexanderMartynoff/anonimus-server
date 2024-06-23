<template>
  <div class="q-pa-md">
    <q-list bordered class="rounded-borders shadow-5">
      <q-item-label header>Who online?</q-item-label>

      <q-item clickable v-ripple v-for="onlineUser in onlineUsers" @click="onSelect(onlineUser)">
        <q-item-section avatar>
          <q-avatar>
            <img src="/static/user.png">
          </q-avatar>
        </q-item-section>

        <q-item-section>
          <q-item-label>{{onlineUser.name}}</q-item-label>
          <q-item-label caption>Device: {{tail(onlineUser.deviceId)}}</q-item-label>
        </q-item-section>
      </q-item>

    </q-list>
  </div>
</template>

<script>
import { tail } from '../../api/functions.js'

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
      tail,
      onSelect(onlineUser) {
        ctx.emit('select', onlineUser)
      },
    }
  },
}
</script>
