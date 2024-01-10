import { boot } from 'quasar/wrappers'
import { WebSocketService } from '../api/websocket.js'


export default boot(({ app }) => {
    const service = new WebSocketService(
        `ws://${location.host}/api/messanger/connect`,
    )
    service.watch()

    app.provide('websocket', service)
})
