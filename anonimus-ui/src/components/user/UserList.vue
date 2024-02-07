<template>
  <div class="q-pa-md">
    <q-list bordered class="rounded-borders">
      <q-item-label header>Peoples</q-item-label>

      <q-item clickable v-ripple v-for="user in users">
        <q-item-section avatar>
          <q-avatar>
            <img src="https://cdn.quasar.dev/img/avatar2.jpg">
          </q-avatar>
        </q-item-section>

        <q-item-section>
          <q-item-label lines="1">{{user.name}}</q-item-label>
          <q-item-label caption lines="2">
            <span class="text-weight-bold">---</span> ///
          </q-item-label>
        </q-item-section>

        <q-item-section side top>
          1 min ago
        </q-item-section>
      </q-item>

    </q-list>
  </div>
</template>


<script>
import { ref } from 'vue'

export default {
  name: 'UsersList',

  props: {
    users: {
      type: Array,
      default: [],
    },
  },

  setup(props) {
    return {
    }
  },
}
</script>