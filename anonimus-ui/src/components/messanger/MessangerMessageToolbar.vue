<template>
  <q-toolbar class="bg-grey-3 text-black row shadow-1">
    <q-input outlined dense autogrow class="col-grow q-mr-sm" bg-color="white" placeholder="Type a message" v-model="text" ref="input"/>
    <q-btn flat icon="send" padding="5px" @click="onBtnSendClick()"/>
  </q-toolbar>
</template>

<script>
import { ref, unref, onMounted, onBeforeUnmount } from 'vue'
import { v4 } from 'uuid'


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
        {
          id: v4(),
          sequence: Date.now(),
          text: text.value,
          chat: props.chat,
          sender: props.user.name,
        }
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
      let {nativeEl} = unref(input)

      nativeEl.addEventListener('keydown', onKeyDown)
      nativeEl.addEventListener('keyup', onKeyUp)
    })

    onBeforeUnmount(() => {
      let {nativeEl} = unref(input)

      nativeEl.removeEventListener('keydown', onKeyDown)
      nativeEl.removeEventListener('keyup', onKeyUp)
    })

    return {
      input,
      text,
      onBtnSendClick,
    }
  },
}
</script>
