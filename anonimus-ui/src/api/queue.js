export default class Queue {
  constructor(executer, predicat) {
    this.sleep = 1000
    this.interval = null
    this.elements = []
    this.executer = executer
    this.predicat = predicat
  }

  push(element, force = true) {
    this.elements.push(element)

    if (force) {
      this.execute()
    }
  }

  start() {
    this.interval = setInterval(() => {
      this.execute()
    }, this.sleep)
  }

  stop() {
    if (this.interval) {
      clearInterval(this.interval)
    }
  }

  execute() {
    while (this.elements.length) {
      const element = this.elements.pop()

      try {
        this.executer(element)
      } catch (error) {}
    }
  }
}
