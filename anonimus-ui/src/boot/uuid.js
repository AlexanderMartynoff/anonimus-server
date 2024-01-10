import { boot } from 'quasar/wrappers'
import { v4 } from 'uuid';


export default boot(({ app }) => {
    app.provide('uuid', v4())
})
