<template>
  <q-toolbar class="bg-grey-3 text-black row shadow-1">
    <q-input outlined dense autogrow class="col-grow q-mr-sm" bg-color="white" placeholder="Type a message" v-model="text" ref="input"/>
    <q-btn flat icon="send" padding="5px" @click="onBtnSendClick()"/>
  </q-toolbar>
</template>

<script>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'MessangerMessageToolbar',
  emits: ['send'],
  props: {
    container: {
      type: Boolean,
    },
    chat: {
      type: String,
    },
    user: {
      type: Object,
    }
  },

  setup(props, ctx) {
    const input = ref(null)
    const text = ref(null)

    function onBtnSendClick() {
      if (!text.value) {
        return
      }

      ctx.emit(
        'send',
        reactive({
          text: text.value,
          chat: props.chat,
          sender: props.user.name,
        })
      )

      text.value = null
    }

    let shift = false

    function onKeyDown(event) {
      if (event.code == 'ShiftLeft') {
        shift = true
      }

      if (event.code == 'Enter' && !shift) {
        event.preventDefault()
        onBtnSendClick()
      }
    }

    function onKeyUp(event) {
      if (event.code == 'ShiftLeft') {
        shift = false
      }
    }

    onMounted(() => {
      input.value.nativeEl.addEventListener('keydown', onKeyDown)
      input.value.nativeEl.addEventListener('keyup', onKeyUp)
    })

    onBeforeUnmount(() => {
      input.value.nativeEl.removeEventListener('keydown', onKeyDown)
      input.value.nativeEl.removeEventListener('keyup', onKeyUp)
    })

    return {
      input,
      text,
      onBtnSendClick,
    }
  },
}
</script>
