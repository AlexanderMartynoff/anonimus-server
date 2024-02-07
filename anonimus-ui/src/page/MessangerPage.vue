<template>
  <messanger/>
</template>

<script>
import { ref, computed, onMounted, inject } from 'vue'
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
    const websocket = inject('websocket')

    const tab = ref('mails')
    const container = computed(() => props.container)

    onMounted(async () => {
    })

    return {
      tab,
      container,
    }
  },
}
</script>
