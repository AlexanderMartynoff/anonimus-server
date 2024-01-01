<template>
  <n-card class="messanger">
    <n-tabs>
      <n-tab-pane :name="member.name" v-for="member in members">
        <messanger-message type="out" :message="message"/>
        <messanger-message type="in" :message="message"/>
      </n-tab-pane>
    </n-tabs>
    <template #action>
      <n-input-group size="large">
        <n-input type="textarea" :autosize="true" v-model:value="value"/>
        <n-button type="primary" quaternary size="large" @click="onBtnClick">
          <n-icon size="large">
            <send-round/>
          </n-icon>
        </n-button>
      </n-input-group>
    </template>
  </n-card>
</template>

<script>
import { reactive, ref } from 'vue'
import { SendRound } from '@vicons/material'
import MessangerMessage from './MessangerMessage.vue'

export default {
  name: 'Messanger',
  props: {
    messages: Array,
  },

  components: {
    SendRound,
    MessangerMessage,
  },

  setup(props) {
    const value = ref(null)
    const message = ref('null')

    const members = reactive([
      {name: 'Bob'},
      {name: 'Mikola'},
      {name: 'Alex'},
    ])

    const onBtnClick = () => {
      message.value += value.value
    }

    return {
      members,
      value,
      message,
      onBtnClick,
    }
  },
}
</script>
