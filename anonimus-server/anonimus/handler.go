package anonimus

import (
	"context"
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

type Connection struct {
	Id     string `json:"id"`
	Name   string `json:"name"`
	Device string `json:"device"`

	WsCnc    *websocket.Conn  `json:"-"`
	Consumer *consumerService `json:"-"`
}

type MessageHandler struct {
	Config          Config
	Session         SessionService
	ConsumerFactory ConsumerFactoryService
	Publisher       PublisherService
	Connections     Registry[string, Connection]
}

func (hr *MessageHandler) Serve(w http.ResponseWriter, r *http.Request) {
	user, err := hr.Session.GetUser(r)

	if err != nil {
		log.Printf("Session parse error: %s\n", err.Error())
		return
	}

	if _, ok := hr.Connections.Get(user.Device); ok {
		log.Printf("User device already connected: %s\n", user.Device)
		return
	}

	wsCnc, err := Upgrader.Upgrade(w, r, http.Header{
		"X-Anonimus-Server-Version": {hr.Config.Version},
	})

	if err != nil {
		log.Printf("Websocket connection upgrade error: %s\n", err.Error())
	}

	defer func() {
		err := wsCnc.Close()

		if err != nil {
			log.Printf("Websocket closing error: %s\n", err.Error())
		}
	}()

	ctx := context.Background()

	consumer, err := hr.ConsumerFactory.Get(ctx, user.Id, user.Device)

	if err != nil {
		log.Printf("Register consumer error: %s. Close connection\n", err.Error())
		return
	}

	consumer.OnMessage = func(data []byte, ack func() error) {
		hr.onReceive(ctx, user, data, ack, wsCnc)
	}

	err = consumer.Start(ctx)

	if err != nil {
		log.Printf("Start consumer error: %s\n", err.Error())
		return
	}

	defer consumer.Stop()

	hr.Connections.Set(user.Device, Connection{
		Id:       user.Id,
		Name:     user.Name,
		Device:   user.Device,
		WsCnc:    wsCnc,
		Consumer: &consumer,
	})

	defer hr.Connections.Delete(user.Device)

	hr.sendForAll("event", Event{
		Name: "connect",
	})

	defer hr.sendForAll("event", Event{
		Name: "disconnect",
	})

	for {
		msgType, msgData, err := wsCnc.ReadMessage()

		if err != nil {
			log.Printf("websocket reading error: %s\n", err.Error())
			break
		}

		switch msgType {

		case websocket.PingMessage:
			wsCnc.WriteMessage(websocket.PongMessage, []byte("Pong"))

		case websocket.PongMessage:
			wsCnc.WriteMessage(websocket.PingMessage, []byte("Ping"))

		case websocket.TextMessage:
			opr := Operation{}

			err := json.Unmarshal(msgData, &opr)

			if err != nil {
				log.Printf("Message parsing error: '%s'", err.Error())
			}

			hr.onSend(ctx, user, opr.Type, opr.Message)

		default:
			log.Printf("Unknown message type: '%d'", msgType)
		}
	}
}

func (hr *MessageHandler) onSend(ctx context.Context, _ User, msgType string, msgData []byte) {
	switch msgType {

	case "message":
		var msg BroadcastMessage

		err := json.Unmarshal(msgData, &msg)

		if err != nil {
			log.Printf("Message marshaling error: '%s'", err.Error())
			return
		}

		for _, subject := range msg.Subjects {
			hr.Publisher.Publish(ctx, subject, []byte(msg.Text))
		}

	case "subscription":
		return

	case "unsubscription":
		return
	}
}

func (hr *MessageHandler) onReceive(_ context.Context, _ User, msgData []byte, ack func() error, wsCnc *websocket.Conn) {
	err := hr.send("message", Message{
		Text: string(msgData),
	}, wsCnc)

	if err == nil {
		ack()
	} else {
		log.Printf("'OnReceive' sending error: '%s'\n", err.Error())
	}
}

func (hr *MessageHandler) send(oprType string, message any, wsCnc *websocket.Conn) error {
	v, err := json.Marshal(message)

	if err != nil {
		return err
	}

	op := Operation{
		Source:  "server",
		Type:    oprType,
		Message: v,
	}

	v, err = json.Marshal(op)

	if err != nil {
		return err
	}

	err = wsCnc.WriteMessage(websocket.TextMessage, v)

	if err != nil {
		return err
	}

	return nil
}

func (hr *MessageHandler) sendForAll(oprType string, message any) {
	for _, cnc := range hr.Connections.List() {
		err := hr.send(oprType, message, cnc.WsCnc)

		if err == nil {
			log.Printf("Everyone sending to 'Name:%s, Id:%s' \n", cnc.Name, cnc.Id)
		} else {
			log.Printf("Everyone sending error: '%s'\n", err.Error())
		}
	}
}

type OnlineUserHandler struct {
	Session     SessionService
	Config      Config
	Connections Registry[string, Connection]
}

func (hr *OnlineUserHandler) List(w http.ResponseWriter, r *http.Request) {
	v, err := json.Marshal(hr.Connections.List())

	if err != nil {
		fmt.Println(err.Error())
	}

	w.Write(v)
}

type ContactHandler struct {
	Config *Config
}

func (hr *ContactHandler) Delete(w http.ResponseWriter, r *http.Request) {
}

func (hr *ContactHandler) Create(w http.ResponseWriter, r *http.Request) {
}
