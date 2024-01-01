<template>
  <div :class="`messanger__message messanger__message-${type}`">
    <div class="messanger__icon theme-border">

    </div>
    <div class="messanger__text theme-border">
      {{ message }}
    </div>
  </div>
</template>

<script>
  import { computed } from 'vue'
  import { useThemeVars } from 'naive-ui'

  export default {
    name: 'MessangerMessage',
    props: {
      type: {
        type: String,
        required: true,
        validator: (value) => ['out', 'in'].includes(value)
      },
      message: {
        type: String,
        required: true,
      },
    },

    setup(props) {
      const vars = useThemeVars()
      const type = computed(() => props.type)
      const message = computed(() => props.message)

      return {
        vars,
        type,
        message,
      }
    },
  }
</script>

<style lang="scss">
.messanger__message {
  display: flex;
  align-items: center;
  justify-content: stretch;
  padding: 5px;
  margin-bottom: 5px;

  &-out {
    flex-direction: row;
  }

  &-in {
    flex-direction: row-reverse
  }
}

.messanger__icon {
  width: 25px;
  height: 25px;
  margin: 0 5px;
}

.messanger__text {
  flex: 1;
  margin: 0 5px;
  padding: 5px;
}
</style>
