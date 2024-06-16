package anonimus

import "encoding/json"

type User struct {
	Id     string `json:"id"`
	Name   string `json:"name"`
	DeviceId string `json:"deviceId"`
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
	ChatSubjects []string `json:"chatSubjects"`
}

type Operation struct {
	Source  string          `json:"source"`
	Time    float32         `json:"time"`
	Type    string          `json:"type"`
	Message json.RawMessage `json:"message"`
}
