import { boot } from 'quasar/wrappers'
import { WebSocketQueue } from '../api/websocket.js'


export default boot(({ app }) => {
    app.provide('websocket', new WebSocketQueue(`ws://${location.host}/api/messanger/connect`))
})
