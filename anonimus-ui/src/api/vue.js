import { ref, watch, onUnmounted } from 'vue'
import { liveQuery } from 'dexie'


function useLiveQuery(querier, {value=[], depends=[]}={}) {
  let subscriber

  const query = liveQuery(querier)
  const output = ref(value)

  watch(depends, () => {  
    subscriber?.unsubscribe()
    subscriber = query.subscribe(value => {
      output.value = value
    })
  }, {immediate: true})

  onUnmounted(() => {
    subscriber?.unsubscribe()
  })

  return output
}

export {
  useLiveQuery,
}
