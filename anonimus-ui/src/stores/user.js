import { ref, reactive } from 'vue'
import { defineStore } from "pinia"
import { fetchAs } from '../api/fetch.js'


const useStore = defineStore('user', () => {
  // users
  const users = ref([])

  async function fetchUsers() {
    users.value = await fetchAs('/api/connection')
  }

  // user
  const user = reactive({})

  async function updateUser(values) {
    Object.assign(user, values)
  }

  return {
    users,
    fetchUsers,
    user,
    updateUser,
  }
}, {
  persist: {
    paths: ['user'],
  }
})

export {
  useStore,
}
