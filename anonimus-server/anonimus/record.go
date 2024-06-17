package anonimus

import "encoding/json"

type User struct {
	Id       string `json:"id"`
	Name     string `json:"name"`
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
	Id             string `json:"id"`
	Sequence       int    `json:"sequence"`
	Chat           string `json:"chat"`
	Text           string `json:"text"`
	SenderName     string `json:"senderName"`
	SenderId       string `json:"senderId"`
	SenderDeviceId string `json:"senderDeviceId"`
}

type BroadcastMessage struct {
	Message
	ChatSubjects []string `json:"chatSubjects"`
}

type Command struct {
	Source  string          `json:"source"`
	Time    float32         `json:"time"`
	Type    string          `json:"type"`
	Message json.RawMessage `json:"message"`
}
