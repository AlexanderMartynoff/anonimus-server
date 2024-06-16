class WebSocketError extends Error {}
class WebSocketOpenError extends WebSocketError {}


class WebSocketQueue {
  constructor(url, timeout = 5000) {
    this.url = url
    this.timeout = timeout

    this.active = false

    this.listeners = []
    this.elements = []
  }

  connect({ onOpen = () => {}, onClose = () => {} }) {
    if (this.socket && this.socket.readyState != WebSocket.CLOSED) {
      throw new WebSocketOpenError()
    }

    this.socket = new WebSocket(this.url)

    this.socket.onopen = () => {
      onOpen()
      this.dispatch('open')
    }

    this.socket.onerror = () => {
      this.dispatch('error')
    }

    this.socket.onclose = () => {
      onClose()
      this.dispatch('close')
    }

    this.socket.onmessage = (wsMessage) => {
      const data = JSON.parse(wsMessage.data)

      if (data.type) {
        this.dispatch(data.type, data)
      }

      this.dispatch('any', data)
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

  stop(onStop = () => {}) {
    if (this.active) {
      this.active = false

      this.on('close', () => {
        onStop()
      })
      this.socket.close()
    } else {
      onStop()
    }
  }

  flush() {
    for (const element of this.elements.slice()) {
      this.socket.send(element.message)

      const index = this.elements.indexOf(element)

      if (index > -1) {
        this.elements.splice(index, 1)
      }
    }
  }

  push(message, flush = true, priority=0) {
    this.elements.push({
      message: JSON.stringify(message),
      priority,
    })

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
    // TODO: Think about it API!
    const index = this.listeners.map(it => it.execute).indexOf(executer)

    if (index > -1) {
      this.listeners.splice(index, 1)
    }
  }

  dispatch(type, event) {
    for (const listener of this.listeners.slice()) {
      if (listener.type == type) {
        listener.execute(event)

        if (listener.once) {
          this.off(listener.execute)
        }
      }
    }
  }

  subscribe(names, callback) {
    for (const name of names) {
      this.push({name}, 'on')
    }
  }

  unsubscribe(names, callback) {
    for (const name of names) {
      this.push({name}, 'off')
    }
  }
}

export {
  WebSocketQueue,
}
