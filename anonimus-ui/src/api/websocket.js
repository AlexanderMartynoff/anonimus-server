class WebSocketError extends Error {}
class WebSocketOpenError extends WebSocketError {}


class WebSocketQueue {
  constructor(url, timeout = 5000) {
    this.url = url
    this.timeout = timeout

    this.listeners = []
    this.queue = []
    this.waiters = []

    this.active = false
  }

  connect({ onOpen = () => {}, onClose = () => {} }) {
    if (this.socket && this.socket.readyState != WebSocket.CLOSED) {
      throw new WebSocketOpenError()
    }

    this.socket = new WebSocket(this.url)

    this.socket.onopen = () => {
      onOpen()
      this.dispatch('Open')
    }

    this.socket.onerror = () => {
      this.dispatch('Error')
    }

    this.socket.onclose = () => {
      onClose()
      this.dispatch('Close')
    }

    this.socket.onmessage = (message) => {
      const record = JSON.parse(message.data)

      if (record.type) {
        this.dispatch(record.type, record)
      }

      this.dispatch('Any', record)
    }
  }

  start(force = true) {
    clearTimeout(this.timer)

    if (force) {
      this.active = true
    }

    if (!this.active) {
      return
    }

    if (this.socket == undefined || this.socket.readyState == WebSocket.CLOSED) {
      this.connect({
        onOpen: () => {
          this.start(false)
        },
        onClose: () => {
          clearTimeout(this.timer)

          this.timer = setTimeout(() => {
            this.start(false)
          }, this.timeout)
        },
      })

      return
    }

    if (this.socket.readyState == WebSocket.OPEN) {
      this.flush()
    }

    this.timer = setTimeout(() => {
      this.start(false)
    }, this.timeout)
  }

  stop() {
    this.active = false

    if (this.socket) {
      this.socket.close()
    }
  }

  flush() {
    while (this.queue.length) {
      this.socket.send(this.queue.pop())
    }
  }

  push(message, type = 'Message', flush = true) {
    this.queue.push(JSON.stringify({
      type,
      ...message,
    }))

    if (flush && this.socket.readyState == WebSocket.OPEN) {
      this.flush()
    }
  }

  on(type, execute, once = true) {
    this.listeners.push({
      type,
      execute,
      once,
    })
  }

  off(executer) {
    const index = this.listeners.indexOf(executer)

    if (index > -1) {
      this.listeners.splice(index, 1)
    }
  }

  dispatch(type, event) {
    for (const listener of this.listeners.slice()) {
      if (listener.type == type) {
        listener.execute(event)

        if (listener.once) {
          this.off(listener)
        }
      }
    }
  }

  subscribe(names, callback) {
    for (const name of names) {
      this.push({name}, 'On')
    }
  }

  unsubscribe(names, callback) {
    for (const name of names) {
      this.push({name}, 'Off')
    }
  }
}

export {
  WebSocketQueue,
}
