import { ref, computed, reactive, watch } from 'vue'
import { defineStore } from "pinia"
import { LocalStorage } from 'quasar'
import { fetchAs } from '../api/fetch.js'


const useStore = defineStore('user', () => {
    // users
    const users = ref([])

    async function fetchUsers() {
        users.value = await fetchAs('/api/connection')
    }

    // user
    const user = reactive({})

    watch(user, ({name}) => {
        LocalStorage.set('user', {
            name,
        })
    })

    async function fetchUser() {
        const value = LocalStorage.getItem('user')

        if (value) {
            updateUser(value)
        }
    }

    async function updateUser({name}) {
        user.name = name
    }

    fetchUser()

    return {
        users,
        fetchUsers,
        user,
        updateUser,
    }
})

export {
    useStore,
}
