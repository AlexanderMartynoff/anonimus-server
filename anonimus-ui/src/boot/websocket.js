import { boot } from 'quasar/wrappers'
import { WebSocketService } from '../api/socket.js'


export default boot(({ app }) => {
    app.provide('websocket', new WebSocketService('ws://localhost:9090/api/messanger/connect'))
})
