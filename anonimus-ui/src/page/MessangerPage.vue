<template>
  <messanger/>
</template>

<script>
import Messanger from '../component/Messanger.vue'

export default {
  name: 'MessangerPage',
  props: {
    msg: String,
  },
  components: {
    Messanger,
  },
}
</script>
