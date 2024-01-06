<template>

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
