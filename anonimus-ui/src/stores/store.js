import { ref, reactive, inject } from 'vue'
import { defineStore } from 'pinia'
import { fetchAs } from '../api/fetch.js'


const useStore = defineStore('user', () => {
  const database = inject('database')

  // online users
  const onlineUsers = ref([])

  async function fetchOnlineUsers() {
    onlineUsers.value = await fetchAs('/api/online-user')
  }

  // user
  const user = reactive({
    id: 0,
    name: null,
  })

  async function fetchUser() {
    await database.users.toCollection().first().then((values) => {
      Object.assign(user, values, {ready: true})
    })
  }

  async function saveUser(values, options={}) {
    await database.users.put(values).then(() => {
      Object.assign(user, values)
    })
  }

  fetchUser()

  return {
    // user
    user,
    saveUser,

    // online users
    onlineUsers,
    fetchOnlineUsers,
  }
})

export {
  useStore,
}
