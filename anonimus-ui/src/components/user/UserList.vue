<template>
  <div class="q-pa-md">
    <q-list bordered class="rounded-borders">
      <q-item-label header>Members</q-item-label>

      <q-item clickable v-ripple v-for="user in users" @click="onUserClick(user)">
        <q-item-section avatar>
          <q-avatar>
            <img src="https://cdn.quasar.dev/img/avatar2.jpg">
          </q-avatar>
        </q-item-section>

        <q-item-section>
          <q-item-label lines="1">{{user.name}}</q-item-label>
          <q-item-label caption lines="2">
            <span class="text-weight-bold">
              <span v-if="user.name == uuid">Me</span>
            </span> ///
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
import { useRouter } from 'vue-router'
import { inject } from 'vue'


export default {
  name: 'UsersList',

  props: {
    users: {
      type: Array,
      default: [],
    },
  },

  setup(props) {
    const uuid = inject('uuid')
    const router = useRouter()

    return {
      uuid,
      onUserClick(user) {
        router.push({name: 'messanger', params: {chat: user.name}})
      },
    }
  },
}
</script>
