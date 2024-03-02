import { reactive } from 'vue'
import { defineStore } from 'pinia'


const useStore = defineStore('chat', () => {
	const chats = reactive({})

	return {
		addChat(name) {
			chats[name] = {
				name,
				letter: name.substring(0, 1),
				messages: [],
			}
		},

		removeChat(name) {
			delete chats[name]
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
