class WebSocketService {
  constructor(url) {
    this.url = url
  }

  get state() {
    return this.socket?.readyState
  }

  async open(resolve, reject) {
    if (this.socket) {
      return
    }

    this.socket = new WebSocket(this.url)

    this.socket.onopen = response => {
      resolve()
    }

    this.socket.onmessage = ({data}) => {
      try {
        this.receive(JSON.parse(data))
      } catch (error) {
        console.log(`error while parse msg ${error.toString()}`)
      }
    }

    this.socket.onerror = response => {
      reject()
    }

    this.socket.onclose = response => { }
  }

  receive(message) {
  }

  send(message) {
    this.open(() => {
      this.socket.send(JSON.stringify(message));
    })
  }

  on(predicat, callback, data) {
  }

  off(id) {
  }
}

export {
  WebSocketService,
}
