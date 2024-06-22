<template>
  <div class="q-pa-md messanger__writer messanger__writer--responsive">
    <q-infinite-scroll @load="onScrollTop" reverse>
      <q-chat-message :name="message.senderName" avatar="/static/user.png" stamp="1 minut ago" :sent="message.senderDeviceId == user.deviceId" text-color="white" bg-color="primary" v-for="message in messages">
        <div class="messanger__message text-caption">
          {{tail(message.id)}} | {{message.sequence}}
        </div>
        <div class="messanger__message">
          {{message.text}}
        </div>
      </q-chat-message>
    </q-infinite-scroll>
  </div>
</template>

<script>
import { computed } from 'vue'
import { tail } from '../../api/functions.js'

export default {
  emits: ['scroll-top'],

  name: 'MessangerChat',
  props: {
    messages: {
      type: Array,
    },
    user: {
      type: Object,
    },
  },

  setup(props, ctx) {
    const user = computed(() => props.user)

    return {
      user,
      tail,
      onScrollTop(index, done) {
        ctx.emit('scroll-top', index, done)
      },
    }
  },
}
</script>

<style lang="scss">
.screen--xl .messanger__writer--responsive {
  width: 30%;
}
.screen--lg .messanger__writer--responsive {
  width: 50%;
}
.screen--md .messanger__writer--responsive {
  width: 70%;
}
.messanger__message {
  white-space: pre-wrap;
}
</style>
