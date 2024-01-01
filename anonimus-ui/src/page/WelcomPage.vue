<template>
  <n-layout content-class="flex flex-align-items-center flex-justify-content-center">
    <n-space vertical justify="center">
      <n-card title="Anonumus chat" hoverable>
        Here you can chat with new people one-on-one without registration or SMS, completely anonymously!
        <template #footer>
          <n-button type="primary" @click="onBtnClick">
            <template #icon>
              <n-icon>
                <play-circle-filled-white-outlined/>
              </n-icon>
            </template>
            Run
          </n-button>
        </template>
      </n-card>
      <n-card title="Topics" hoverable>
        <n-space>
          <n-button :type="topic.type" v-for="topic in topics" @click="onTopicBtnClick(topic)">
            {{topic.title}}
          </n-button>
        </n-space>
      </n-card>
    </n-space>
  </n-layout>
</template>

<script>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { PlayCircleFilledWhiteOutlined } from '@vicons/material'

export default {
  name: 'WelcomPage',

  components: {
    PlayCircleFilledWhiteOutlined,
  },

  setup() {
    const router = useRouter()

    const topics = reactive([
      {type: 'default', title: 'Sara'},
      {type: 'info', title: 'Sara'},
      {type: 'success', title: 'Sara'},
      {type: 'error', title: 'Sara'},
      {type: 'warning', title: 'Sara'},
    ])

    return {
      onBtnClick () {
        router.push('/chat')
      },

      onTopicBtnClick (topic) {
        topics.push(topic)
      },

      topics,
    }
  },
}
</script>
