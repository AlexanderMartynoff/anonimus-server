package anonimus

import "encoding/json"

type User struct {
	Id     string `json:"id"`
	Name   string `json:"name"`
	Device string `json:"device"`
}

type Subscribtion struct {
	Name string
}

type Unsubscribtion struct {
	Name string
}

type Event struct {
	Name string `json:"name"`
}

type Message struct {
	Id       string `json:"id"`
	Sequence int    `json:"sequence"`
	Chat     string `json:"chat"`
	Text     string `json:"text"`
}

type BroadcastMessage struct {
	Message
	Subjects []string `json:"subjects"`
}

type Operation struct {
	Id      string          `json:"id"`
	Source  string          `json:"source"`
	Time    float32         `json:"time"`
	Type    string          `json:"type"`
	Message json.RawMessage `json:"message"`
}
