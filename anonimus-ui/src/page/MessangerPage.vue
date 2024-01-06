<template>
  <messanger/>
</template>

<script>
import { ref, computed } from 'vue'
import Messanger from '../components/messanger/Messanger.vue'

export default {
  name: 'IndexPage',
  components: {
    Messanger,
  },
  props: {
    container: Boolean,
  },

  setup(props) {
    const tab = ref('mails')
    const container = computed(() => props.container)

    return {
      tab,
      container,
    }
  },
}
</script>
