import { LocalStorage, SessionStorage } from 'quasar'
import Dexie from 'dexie'
import { WebSocketQueue } from '../api/websocket.js'


export default async ({ app, router, store }) => {
  // WebSocket
  let reference = LocalStorage.getItem('ref')

  if (!reference) {
    reference = '0-0'
  }

  const websocket = new WebSocketQueue(`ws://${location.host}/api/messanger/connect?ref=${reference}`)

  websocket.on('any', ({reference}) => {
    if (reference) {
      LocalStorage.set('ref', reference)
    }
  }, false)

  app.provide('websocket', websocket)

  // Dexie
  const database = new Dexie('database')

  database.version(1).stores({
    users: '++_id',
    messages: '++_id, sequence, chat',
    chats: 'id, name',
  })

  app.provide('database', database)
}
