package anonimus

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/websocket"
)

var Upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

type MessageHandler struct {
	Settings      *Settings
	SessionSrv    *SessionService
	MessageSrv    MessageService
}

func (hr *MessageHandler) Serve(w http.ResponseWriter, r *http.Request) {
	user, err := hr.SessionSrv.GetUser(r)

	if err != nil {
		return
	}

	wc, err := Upgrader.Upgrade(w, r, map[string][]string{
		"X-Anonimus-Server-Version": {hr.Settings.Version},
	})

	if err != nil {
		log.Printf("Websocket connection opening error: %s\n", err.Error())
	}

	err = hr.MessageSrv.RegisterOnliner(user, wc)

	if err != nil {
		log.Printf("Can not register connection: %s\n", err.Error())
		return
	}

	defer hr.MessageSrv.UnregisterOnliner(user)

	for {
		msgType, msgData, err := wc.ReadMessage()

		if err != nil {
			log.Printf("Websocket reading error: %s\n", err.Error())
			break
		}

		switch msgType {

		case websocket.PingMessage:
			wc.WriteMessage(websocket.PongMessage, []byte("Pong"))

		case websocket.PongMessage:
			wc.WriteMessage(websocket.PingMessage, []byte("Ping"))

		case websocket.TextMessage:
			msg := Request{}

			err := json.Unmarshal(msgData, &msg)

			if err != nil {
				fmt.Printf("Message parsing error: '%s'", err.Error())
			}
			hr.serveMessage(msg.Type, msg.Message)

		default:
		}
	}

	err = wc.Close()

	if err != nil {
		log.Printf("Websocket closing error: %s\n", err.Error())
	}
}

func (hr *MessageHandler) serveMessage(msgType string, msgData []byte) {
	switch msgType {

	case "message":
		var msg Message

		err := json.Unmarshal(msgData, &msg)

		if err != nil {
			return
		}

		hr.MessageSrv.SendMessage(msg)

	case "onEvent":
		return

	case "offEvent":
		return
	}
}

type OnlineUserHandler struct {
	MessageSrv         MessageService
	SessionSrv    *SessionService
	Settings          *Settings
}

func (hr *OnlineUserHandler) List(w http.ResponseWriter, r *http.Request) {
	v, err := json.Marshal(hr.MessageSrv.ListUsers())

	if err != nil {
		fmt.Println(err.Error())
	}

	w.Write(v)
}

type ContactHandler struct {
	Settings *Settings
}

func (hr *ContactHandler) Delete(w http.ResponseWriter, r *http.Request) {
}

func (hr *ContactHandler) Create(w http.ResponseWriter, r *http.Request) {
}
