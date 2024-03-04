<template>
  <div class="q-pa-md">
    <q-list bordered class="rounded-borders">
      <q-item-label header>Members</q-item-label>

      <q-item clickable v-ripple v-for="user in users" @click="onUserClick(user)">
        <q-item-section avatar>
          <q-avatar>
            <img src="/static/user.png">
          </q-avatar>
        </q-item-section>

        <q-item-section>
          <q-item-label lines="1">{{user.name}}</q-item-label>
          <q-item-label caption lines="2">
            <span class="text-weight-bold">
              <span v-if="user.name == me.name">Me</span>
            </span>
          </q-item-label>
        </q-item-section>

        <q-item-section side top>
          1 min ago
        </q-item-section>
      </q-item>

    </q-list>
  </div>
</template>


<script>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore as useChatStore } from '../../stores/chat.js'

export default {
  name: 'UsersList',

  props: {
    users: {
      type: Array,
    },
    me: {
      type: Object,
    }
  },

  setup(props) {
    const router = useRouter()
    const chatStore = useChatStore()

    const me = computed(() => props.me)

    return {
      me,
      onUserClick(user) {
        router.push({
          name: 'messanger',
          params: {chat: user.name},
        })

        if (!chatStore.hasChat(user.name)) {
          chatStore.addChat(user.name)
        }
      },
    }
  },
}
</script>
