<template>
  <q-toolbar>
    <slot />
    <q-space />
    <q-btn flat icon="settings" @click="onSettingsClick()"></q-btn>
  </q-toolbar>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useStore as useUserStore } from '../../stores/user.js'
import UserFormDialog from '../user/UserFormDialog.vue'

export default {
  name: 'HeaderToolbar',

  setup() {
    const quasar = useQuasar()
    const userStore = useUserStore()

    const user = computed(() => userStore.user.name)

    return {
      user,
      onSettingsClick() {
        quasar.dialog({
          component: UserFormDialog,
          componentProps: {
            user: userStore.user,
          },
        }).onOk(user => {
          userStore.updateUser(user)
        })
      },
    }
  },
}
</script>
