<template>
  <q-toolbar>
    <slot/>
    <q-space/>
    <q-btn flat icon="settings" @click="onSettingsClick()"/>
  </q-toolbar>
</template>

<script>
import { toRaw } from 'vue'
import { useQuasar } from 'quasar'
import { useStore } from '../../stores/store.js'
import UserFormDialog from '../user/UserFormDialog.vue'

export default {
  name: 'HeaderToolbar',

  setup() {
    const quasar = useQuasar()
    const store = useStore()

    return {
      onSettingsClick() {
        quasar.dialog({
          component: UserFormDialog,
          componentProps: {
            user: store.user,
          },
        }).onOk(user => {
          store.saveUser(toRaw(user))
        })
      },
    }
  },
}
</script>