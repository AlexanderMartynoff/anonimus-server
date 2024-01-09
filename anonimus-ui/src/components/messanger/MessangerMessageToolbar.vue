<template>
  <q-toolbar class="bg-grey-3 text-black row">
    <q-input outlined dense autogrow class="col-grow q-mr-sm" bg-color="white" placeholder="Type a message" v-model="text"/>
    <q-btn flat icon="send" padding="5px" @click="onBtnSendClick"/>
  </q-toolbar>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'MessangerMessageToolbar',
  emits: ['send'],
  props: {
    container: {
      type: Boolean,
    },
    members: {
      default: [],
      type: Array,
    },
  },

  setup(props, ctx) {
    const text = ref(null)

    return {
      text,
      onBtnSendClick() {
        if (!text.value) {
          return
        }

        ctx.emit('send', {
          text: text.value,
        })

        text.value = null
      },
    }
  },
}

</script>
