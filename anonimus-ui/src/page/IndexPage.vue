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
import UserList from '../components/user/UserList.vue'
import ToolbarHeader from '../components/layout/ToolbarHeader.vue'
import {fetchAs} from '../api/fetch.js'

export default {
  name: 'WelcomPage',
  components: {
    UserList,
    ToolbarHeader,
  },

  setup(props) {
    const websocket = inject('websocket')
    const users = ref([])

    const onPeopleChange = async () => {
      const uuids = await fetchAs('/api/who-online')

      users.value = uuids.map((uuid) => {
        return {name: uuid}
      })
    }

    onMounted(() => {
      websocket.on('Online', onPeopleChange, false)
      onPeopleChange()
    })

    onUnmounted(() => {
      websocket.off(onPeopleChange)
    })

    return {
      slide: ref('style'),
      users,
    }
  },
}
</script>
