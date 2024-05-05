import { ref, watch, onUnmounted } from 'vue'
import { liveQuery } from 'dexie'


function useLiveQuery(querier, {value=[], depends=[]}={}) {
  const query = liveQuery(querier)
  const output = ref(value)

  let subscriber

  function setup() {
    subscriber = query.subscribe(value => {
      output.value = value
    })
  }

  setup()

  watch(depends, () => {  
    subscriber?.unsubscribe()
    setup()
  })

  onUnmounted(() => {
    subscriber?.unsubscribe()
  })

  return output
}

export {
  useLiveQuery,
}
