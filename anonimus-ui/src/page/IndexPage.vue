<template>
  <q-layout view="hHh lpr fFf">
    <q-header>
      <header-toolbar>
        <q-btn flat icon="chat" @click="onChatClick()"/>
      </header-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="column flex-center">
        <online-user-list :online-users="onlineUsers" @select="onUserSelect"/>
      </q-page>
    </q-page-container>
  </q-layout>
</template>


<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '../stores/store.js'
import OnlineUserList from '../components/user/OnlineUserList.vue'
import HeaderToolbar from '../components/layout/HeaderToolbar.vue'


export default {
  name: 'IndexPage',
  components: {
    OnlineUserList,
    HeaderToolbar,
  },

  setup() {
    const router = useRouter()
    const store = useStore()

    return {
      onChatClick() {
        router.push({
          name: 'messanger',
        })
      },

      onUserSelect(user) {
        router.push({
          name: 'messanger',
          params: {
            chat: [user.name, store.user.name].sort().join('/'),
          },
        })
      },

      onlineUsers: computed(() => store.onlineUsers),
    }
  },
}
</script>
