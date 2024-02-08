<template>
	<q-toolbar>
		<slot/>
		<q-toolbar-title>[ chat ]</q-toolbar-title>
	</q-toolbar>
</template>

<script>
import { ref, computed } from 'vue'

export default {
	name: 'Toolbar',
	setup(props) {},
}
</script>
  