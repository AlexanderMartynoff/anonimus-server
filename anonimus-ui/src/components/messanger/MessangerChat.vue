<template>
  <div class="q-pa-md messanger__writer messanger__writer--responsive">
      <q-chat-message name="Me" avatar="https://cdn.quasar.dev/img/avatar3.jpg" stamp="7 minutes ago" sent text-color="white" bg-color="primary" v-for="message in messages">
        <div class="messanger__message">
          {{message.text}}
        </div>
      </q-chat-message>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'MessangerChat',
  props: {
    messages: {
      type: Array,
      default: [],
    },
  },

  setup(props) {
    
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
