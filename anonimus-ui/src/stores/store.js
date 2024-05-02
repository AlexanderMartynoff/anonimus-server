import { ref, reactive, inject } from 'vue'
import { defineStore } from 'pinia'
import { Cookies } from 'quasar'
import { fetchAs } from '../api/fetch.js'


const useStore = defineStore('user', () => {
  // online users
  const onlineUsers = ref([])

  async function fetchOnlineUsers() {
    onlineUsers.value = await fetchAs('/api/online-user')
  }

  // user
  const user = reactive({})

  async function saveUser(values, options={}) {
    Object.assign(user, values)

    if (options.insecure) {
      Cookies.set('user', values, {expires: 31, sameSite: 'Strict'})
    }
  }

  return {
    // user
    user,
    saveUser,

    // online users
    onlineUsers,
    fetchOnlineUsers,
  }
}, {
  persist: [
    {
      paths: ['user'],
    },
  ],
})

export {
  useStore,
}
