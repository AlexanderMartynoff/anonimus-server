<template>
  <div>
    <q-layout view="hHh lpr fFf">
      <q-header elevated>
        <toolbar-header/>
      </q-header>

      <q-page-container>
        <q-page class="column flex-center">
          <user-list :users="userStore.users"/>
        </q-page>
      </q-page-container>
    </q-layout>
  </div>
</template>


<script>
import { ref } from 'vue'
import { useUserStore } from '../stores/user.js'
import UserList from '../components/user/UserList.vue'
import ToolbarHeader from '../components/layout/ToolbarHeader.vue'


export default {
  name: 'WelcomPage',
  components: {
    UserList,
    ToolbarHeader,
  },

  setup(props) {
    const userStore = useUserStore()

    return {
      slide: ref('style'),
      userStore,
    }
  },
}
</script>
