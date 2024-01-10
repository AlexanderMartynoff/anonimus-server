class WebSocketError extends Error {}
class WebSocketOpenError extends WebSocketError {}


class WebSocketService {
  constructor(url) {
    this.url = url
    this.listeners = []
    this.messages = []
  }

  get state () {
    return this.socket ? this.socket.readyState : WebSocket.CLOSED
  }

  connect() {
    this.socket = new WebSocket(this.url)

    this.socket.onopen = response => {
      this.dispatch('open')
    }

    this.socket.onerror = error => {
      console.log(error)
      this.dispatch('error')
    }

    this.socket.onmessage = ({data}) => {
      try {
        this.receive(JSON.parse(data))
      } catch (error) {
        console.error(error)
      }
    }

    this.socket.onclose = response => {
      this.dispatch('onclose')
    }
  }

  execute(onOpen, onError) {
    this.on('open', () => {
      onOpen()
      this.off(onError)
    })

    this.on('error', () => {
      onError()
      this.off(onOpen)
    })

    if (this.state == WebSocket.CLOSED) {
      this.connect()
    } else if (this.state == WebSocket.OPEN) {
      this.dispatch('open')
    }
  }

  receive(message) {}

  watch() {
    const repeat = () => {
      setTimeout(() => {
        this.watch()
      }, 1000)
    }

    this.execute(() => {
      while (this.messages.length) {
        this.socket.send(this.messages.pop())
      }
      repeat()
    }, repeat)
  }

  push(message) {
    this.messages.push(JSON.stringify(message))
  }

  on(type, execute, once = true) {
    this.listeners.push({
      type,
      execute,
      once,
    })
  }

  off(listener) {
    const index = this.listeners.indexOf(listener)

    if (index > -1) {
      this.listeners.splice(index, 1)
    }
  }

  dispatch(type) {
    for (const listener of this.listeners.slice()) {
      if (listener.type == type) {
        listener.execute()
      }

      if (listener.once) {
        this.off(listener)
      }
    }
  }

  subscribe(message) {
    this.push(message)
  }
  unsubscribe() {}
}

export {
  WebSocketService,
}
