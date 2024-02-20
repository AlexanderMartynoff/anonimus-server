<template>
  <q-layout view="hHh lpr fFf">
    <q-header elevated>
      <header-toolbar/>
    </q-header>

    <q-page-container>
      <q-page class="column flex-center">
        <user-list :users="users"/>
      </q-page>
    </q-page-container>
  </q-layout>
</template>


<script>
import { ref, computed } from 'vue'
import { useStore as useUserStore } from '../stores/user.js'
import UserList from '../components/user/UserList.vue'
import HeaderToolbar from '../components/layout/HeaderToolbar.vue'


export default {
  name: 'IndexPage',
  components: {
    UserList,
    HeaderToolbar,
  },

  setup() {
    const userStore = useUserStore()

    return {
      slide: ref('style'),
      users: computed(() => userStore.users),
    }
  },
}
</script>
