import { LocalStorage, SessionStorage } from 'quasar'
import Dexie from 'dexie'
import { WebSocketQueue } from '../api/websocket.js'


export default async ({ app, router, store }) => {
  const DB_VERSION = 1
  // WebSocket
  const websocket = new WebSocketQueue(`ws://${location.host}/api/serve`)

  websocket.on('any', ({reference}) => {
    if (reference) {
      LocalStorage.set('ref', reference)
    }
  }, false)

  app.provide('websocket', websocket)

  // Dexie
  const database = new Dexie('database')

  database.version(DB_VERSION).stores({
    users: 'id',
    messages: 'id, [chat+sequence], text',
    chats: 'id, name',
  })

  app.provide('database', database)
}
