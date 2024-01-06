<template>
  <div class="q-pa-md messanger__writer messanger__writer--responsive">
      <q-chat-message name="Me" avatar="https://cdn.quasar.dev/img/avatar3.jpg" stamp="7 minutes ago" sent text-color="white" bg-color="primary" v-for="n in 5">
        <div>
          Hey there!
        </div>
        <div>
          Have you seen Quasar?
        </div>
      </q-chat-message>

      <q-chat-message name="Jane" avatar="https://cdn.quasar.dev/img/avatar5.jpg" bg-color="amber" v-for="n in 5">
        <q-spinner-dots size="2rem" />
      </q-chat-message>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'MessangerChat',
  components: {
  },
  props: {
    container: {
      type: Boolean,
    },
    members: {
      default: [],
      type: Array,
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
  width: 60%;
}
.screen--md .messanger__writer--responsive {
  width: 80%;
}
</style>
