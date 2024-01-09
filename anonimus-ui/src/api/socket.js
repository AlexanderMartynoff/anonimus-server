class WebSocketService {
  constructor(url) {
    this.url = url

    this.resolves = []
    this.rejects = []
  }

  connect() {
    if (this.socket && this.socket.readyState != WebSocket.CLOSED) {
      throw new Error()
    }

    this.socket = new WebSocket(this.url)

    this.socket.onopen = response => {
      while (this.resolves.length) {
        const resolve = this.resolves.pop()

        try {
          resolve()
        } catch (error) {}
      }
    }

    this.socket.onerror = response => {
      while (this.rejects.length) {
        const reject = this.rejects.pop()

        try {
          reject()
        } catch (error) {}
      }
    }

    this.socket.onmessage = ({data}) => {
      try {
        this.receive(JSON.parse(data))
      } catch (error) {
        console.log(`error while parse msg ${error.toString()}`)
      }
    }

    this.socket.onclose = response => {
      this.retry()
    }
  }

  apply(resolve, reject) {
    if (this.socket?.readyState == WebSocket.OPEN) {
      resolve()
    } else {
      this.resolves.push(resolve)
      this.rejects.push(reject)

      this.connect()
    }
  }

  receive(message) {
  }

  retry() {
    setTimeout(() => {
      this.connect(() => {}, () => {
        this.retry()
      })
    }, 1000)
  }

  send(message) {
    this.apply(() => {
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
