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
	ParentId       string `json:"parentId"`
}

type PublishingMessage struct {
	ChatSubjects []string `json:"chatSubjects"`
	Message
}

type ConsumingMessage struct {
	Message
}

type Command struct {
	Source string          `json:"source"`
	Time   int64           `json:"time"`
	Type   string          `json:"type"`
	Data   json.RawMessage `json:"message"`
}
