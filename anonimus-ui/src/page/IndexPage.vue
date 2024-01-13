<template>
  <div>
    <q-layout view="hHh lpr fFf">
      <q-header elevated>
        <toolbar-header/>
      </q-header>

      <q-page-container>
        <q-page class="column flex-center">
          <user-list :users="users"/>
        </q-page>
      </q-page-container>
    </q-layout>
  </div>
</template>

<script>
import { ref, inject, onMounted, onUnmounted } from 'vue'
import { v4 } from 'uuid'
import UserList from '../components/user/UserList.vue'
import ToolbarHeader from '../components/layout/ToolbarHeader.vue'

export default {
  name: 'WelcomPage',
  components: {
    UserList,
    ToolbarHeader,
  },

  setup(props) {
    const uuid = v4()

    const websocket = inject('websocket')
    const users = ref([])

    onMounted(() => {
      websocket.subscribe('user-online::change', ({data}) => {
        users.value = data
      }, uuid)
    })

    onUnmounted(() => {
      websocket.unsubscribe(uuid)
    })

    return {
      slide: ref('style'),
      users: [],
    }
  },
}
</script>
