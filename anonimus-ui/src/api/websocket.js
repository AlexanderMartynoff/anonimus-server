class WebSocketError extends Error {}
class WebSocketOpenError extends WebSocketError {}


class WebSocketQueue {
  constructor(url, timeout = 1000) {
    this.url = url
    this.timeout = timeout

    this.listeners = []
    this.queue = []
    this.waiters = []

    this.active = false

    this.push({
      type: 'Ping',
    })
  }

  connect({ onOpen = () => {}, onError = () => {}, onClose = () => {} }) {
    if (this.socket && this.socket.readyState != WebSocket.CLOSED) {
      throw new WebSocketOpenError()
    }

    this.socket = new WebSocket(this.url)

    this.socket.onopen = () => {
      onOpen()
    }

    this.socket.onerror = () => {
      onError()
    }

    this.socket.onclose = () => {
      onClose()
    }

    this.socket.onmessage = () => {
      this.onMessage()
    }
  }

  onMessage({ data }) {
    try {
      const message = JSON.parse(data)
    } catch (error) {
      console.error(error)
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

  push(message) {
    this.queue.push(JSON.stringify(message))
  }

  on(types, execute, once = true) {
  }

  off(listener) {
  }
}

export {
  WebSocketQueue,
}