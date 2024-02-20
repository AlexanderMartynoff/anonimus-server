<template>
  <q-toolbar>
    <slot />
    <q-btn flat dense icon="home" @click="onHomeClick" />
    <q-space />
    <q-btn flat dense icon="person" @click="onPersonClick" />
  </q-toolbar>
</template>


<script>
	import { useRouter } from 'vue-router'
	import { useQuasar } from 'quasar'
	import { useStore as useUserStore } from '../../stores/user.js'
	import UserFormDialog from '../user/UserFormDialog.vue'

	export default {
		name: 'HeaderToolbar',

		setup(props, ctx) {
			const quasar = useQuasar()
			const router = useRouter()

			const userStore = useUserStore()

			return {
				onHomeClick() {
					router.push({ name: 'index' })
				},

				onPersonClick() {
					quasar.dialog({
						component: UserFormDialog,
						componentProps: {
							user: userStore.user,
						},
					}).onOk(user => {
            userStore.updateUser(user)
					})
				},
			}
		},
	}
</script>
