import { ref, computed } from 'vue'
import { defineStore } from "pinia"
import { fetchAs } from '../api/fetch.js'


const useUserStore = defineStore('user', () => {
    const records = ref([])
    const users = computed(() => records.value)

    async function fetchUsers() {
        const users = await fetchAs('/api/connection', (uuids) => {
            return uuids.map((uuid) => ({name: uuid}))
        })

        records.value = users
    }

    return {
        users,
        fetchUsers,
    }
})

export {
    useUserStore,
}
