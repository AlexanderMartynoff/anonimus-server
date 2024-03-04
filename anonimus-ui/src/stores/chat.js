import { reactive } from 'vue'
import { defineStore } from 'pinia'


const useStore = defineStore('chat', () => {
  const chats = reactive({})

  return {
    addChat(name) {
      if (name in chats) {
        throw Error('Chat exists')
      }

      chats[name] = {
        name,
        letter: name.substring(0, 1),
        messages: [],
      }
    },

    removeChat(name) {
      delete chats[name]
    },

    pushChatMessage(name, message) {
      chats[name].messages.push(message)
    },

    hasChat(name) {
      return name in chats
    },

    chats,
  }
}, {
  persist: {
    paths: ['chats']
  },
})

export {
  useStore,
}
