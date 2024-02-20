<template>
  <q-dialog ref="dialogRef" transition-show="flip-down" transition-hide="flip-up">
    <q-card class="bg-primary text-white">
      <q-bar>
        User
        <q-space/>
        <q-btn dense flat icon="close" v-close-popup/>
      </q-bar>

      <q-card-section class="q-pt-none q-pa-md">
        <q-form class="q-gutter-md">
          <q-input filled label="Name" v-model="user.name"/>
          <q-input filled label="Age" v-model="user.age"/>
          <q-input filled label="Sex" v-model="user.sex"/>
        </q-form>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn label="Save" flat v-close-popup @click="onDialogOK(user)"/>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import { onMounted, ref, computed, watch, reactive } from 'vue'
import { useDialogPluginComponent } from 'quasar'

export default {
  name: 'UsersForm',
  emits: [
    ...useDialogPluginComponent.emits,
  ],

  props: {
    user: {
      type: Object,
    }
  },

  setup(props, ctx) {
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

    const user = reactive({})

    watch(props.user, ({name}) => {
      user.name = name
    }, {immediate: true})

    return {
      user,
      dialogRef,
      onDialogHide,
      onDialogOK,
    }
  },
}
</script>
