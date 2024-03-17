import { ref, watch, onUnmounted } from 'vue'
import { liveQuery } from 'dexie'


function useLiveQuery(querier, {value=[], depends=[]}={}) {
  let subscriber

  const query = liveQuery(querier)
  const output = ref(value)

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
