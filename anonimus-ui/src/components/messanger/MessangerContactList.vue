<template>
  <q-list>
    <q-item v-for="contact in contacts">
      <q-item-section avatar>
        <q-icon color="primary" name="bluetooth" />
      </q-item-section>
      <q-item-section>
        {{contact.name}}
      </q-item-section>
    </q-item>
  </q-list>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'MessangerContactList',
  props: {
    contacts: {
      default: [],
      type: Array,
    },
  },

  setup(props) {
  },
}
</script>
