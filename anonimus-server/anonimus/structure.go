package anonimus

import "encoding/json"


type User struct {
	Id string
	Name string
}

type Record struct {
	Id string
	Time float32
}

type Subscribtion struct {
	Record
	Name string
}

type Unsubscribtion struct {
	Record
	Name string
}

type Message struct {
	Record
	Text string
}

type Request struct {
	Type string
	Message json.RawMessage
}

type Response struct {
	Type string
	Message json.RawMessage
}
