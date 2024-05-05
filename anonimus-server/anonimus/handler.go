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
	SessionService    *SessionService
	OnlineUserService *OnlineUserService
	Settings          *Settings
}

func (hr *MessageHandler) Serve(w http.ResponseWriter, r *http.Request) {
	user, err := hr.SessionService.GetUser(r)

	if err != nil {
		return
	}

	wsConn, err := Upgrader.Upgrade(w, r, map[string][]string{
		"X-Anonimus-Server-Version": {hr.Settings.Version},
	})

	if err != nil {
		log.Printf("Websocket connection opening error: %s\n", err.Error())
	}

	hr.OnlineUserService.Add(user.Id, OnlineUser{User: user})

	for {
		msgType, msgData, err := wsConn.ReadMessage()

		if err != nil {
			log.Printf("Websocket reading error: %s\n", err.Error())
			break
		}

		switch msgType {

		case websocket.PingMessage:
			wsConn.WriteMessage(websocket.PongMessage, []byte{})

		case websocket.PongMessage:
			wsConn.WriteMessage(websocket.PingMessage, []byte{})

		case websocket.TextMessage:
			msg := Request{}

			err := json.Unmarshal(msgData, &msg)

			if err != nil {
				fmt.Printf("Message parsing error: '%s'", err.Error())
			}

			hr.serveMessage(msg.Type, msg.Message)
		}
	}

	err = wsConn.Close()

	if err != nil {
		log.Printf("Websocket closing error: %s\n", err.Error())
	}

	hr.OnlineUserService.Delete(user.Id)
}

func (hr *MessageHandler) serveMessage(msgType string, msgData []byte) {
	switch msgType {

	case "message":
		msg := Message{}

		err := json.Unmarshal(msgData, &msg)

		if err != nil {
			return
		}

		fmt.Printf("Message: %s\r\n", msg.Text)

	case "subscribtion":
		return

	case "unsubscribtion":
		return
	}
}

type OnlineUserHandler struct {
	OnlineUserService *OnlineUserService
	SessionService    *SessionService
	Settings          *Settings
}

func (hr *OnlineUserHandler) List(w http.ResponseWriter, r *http.Request) {
}

type ContactHandler struct {
	Settings *Settings
}

func (hr *ContactHandler) Delete(w http.ResponseWriter, r *http.Request) {
}

func (hr *ContactHandler) Create(w http.ResponseWriter, r *http.Request) {
}
