<template>
  <q-layout view="hHh lpr fFf">
    <q-header :elevated="true">
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
import { v5 as uuidv5 } from 'uuid'
import { computed, inject } from 'vue'
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
    const database = inject('database')

    const router = useRouter()
    const store = useStore()

    function generateSortedId(...strings) {
      return uuidv5(strings.sort().join(','), uuidv5.URL)
    }

    return {
      onChatClick() {
        router.push({
          name: 'messanger',
        })
      },

      onUserSelect(onlineUser) {
        const chatId = generateSortedId(onlineUser.name, store.user.name)

        database.chats.put({
          'id': chatId,
          'name': onlineUser.name,
          'users': [
            {id: onlineUser.id, deviceId: onlineUser.deviceId},
          ],
        })

        router.push({
          name: 'messanger',
          params: {
            chat: chatId,
          },
        })
      },

      onlineUsers: computed(() => store.onlineUsers),
    }
  },
}
</script>
