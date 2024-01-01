<template>
  <n-config-provider :theme="theme" abstract>
    <router-view/>
  </n-config-provider>
</template>

<script>
import { ref } from 'vue'
import { darkTheme, lightTheme, useThemeVars } from 'naive-ui'


export default {
  name: 'Root',

  props: {
    msg: String,
  },

  setup(props) {
    const theme = ref(lightTheme)
    const vars = useThemeVars()

    return {
      theme,
      vars,
    }
  },
}
</script>

<style lang="scss">
  .theme-border {
    border: solid 1px v-bind('vars.borderColor');
    border-radius: v-bind('vars.borderRadius');
  }
</style>
