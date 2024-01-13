<template>
	<q-toolbar>
		<slot/>
		<q-toolbar-title>[ a.n.o.n.i.m.u.s ]</q-toolbar-title>
	</q-toolbar>
</template>

<script>
import { ref, computed } from 'vue'

export default {
	name: 'Toolbar',
	setup(props) {},
}
</script>
  