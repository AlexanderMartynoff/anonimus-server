<template>
	<q-toolbar>
		<slot/>
		<q-toolbar-title>[ anonimus ]</q-toolbar-title>
		<q-btn flat dense icon="home" @click="onHomeClick"/>
	</q-toolbar>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
	emits: ['click-home'],
	name: 'Toolbar',
	setup() {
    const router = useRouter()

		return {
			onHomeClick() {
        router.push({name: 'index'})
			}
		}
	},
}
</script>
  