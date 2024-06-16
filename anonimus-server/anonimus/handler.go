package anonimus

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"slices"
	"strconv"
	"sync"

	"github.com/gorilla/websocket"
	"github.com/nats-io/nats.go"
	"github.com/nats-io/nats.go/jetstream"
)

var Upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

type OnlineUser struct {
	Id       string `json:"id"`
	Name     string `json:"name"`
	DeviceId string `json:"deviceId"`

	wsMtx    *sync.Mutex      `json:"-"`
	wsCnc    *websocket.Conn  `json:"-"`
	consumer *consumerService `json:"-"`
}

type MessageHandler struct {
	Config          Config
	Session         SessionService
	ConsumerFactory ConsumerFactoryService
	Publisher       PublisherService
	OnlineUsers     Registry[string, OnlineUser]
}

func (hr *MessageHandler) Serve(w http.ResponseWriter, r *http.Request) {
	user, err := hr.Session.GetUser(r)

	if err != nil {
		log.Printf("Session parse error: %s\n", err.Error())
		return
	}

	if _, ok := hr.OnlineUsers.Get(user.DeviceId); ok {
		log.Printf("User device already connected: %s\n", user.DeviceId)
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

	consumer, err := hr.ConsumerFactory.Get(ctx, user.Id, user.DeviceId)

	if err != nil {
		log.Printf("Register consumer error: %s. Close connection\n", err.Error())
		return
	}

	consumer.OnReceive = func(msg jetstream.Msg) {
		hr.onReceive(ctx, user, msg, wsCnc)
	}

	err = consumer.Start(ctx)

	if err != nil {
		log.Printf("Start consumer error: %s\n", err.Error())
		return
	}

	defer consumer.Stop()

	hr.OnlineUsers.Set(user.DeviceId, OnlineUser{
		Id:       user.Id,
		DeviceId: user.DeviceId,
		Name:     user.Name,

		// TODO: Refactring?
		wsMtx:    &sync.Mutex{},
		wsCnc:    wsCnc,
		consumer: &consumer,
	})

	defer hr.OnlineUsers.Delete(user.DeviceId)

	hr.distribute("event", Event{
		Name: "connect",
	})

	defer hr.distribute("event", Event{
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
			var op Operation

			err := json.Unmarshal(msgData, &op)

			if err != nil {
				log.Printf("Message parsing error: '%s'", err.Error())
			}

			hr.onSend(ctx, user, op.Type, op.Message)

		default:
			log.Printf("Unknown message type: '%d'", msgType)
		}
	}
}

func (hr *MessageHandler) onSend(ctx context.Context, user User, msgType string, msgData []byte) {
	switch msgType {

	case "message":
		var msg BroadcastMessage

		err := json.Unmarshal(msgData, &msg)

		if err != nil {
			log.Printf("Message marshaling error: '%s'", err.Error())
			return
		}

		if len(msg.ChatSubjects) == 0 {
			// TODO: Implement fetch subjects in DB
			return
		}

		// Send if subjets present in message
		for _, subject := range msg.ChatSubjects {
			hr.Publisher.PublishMsg(ctx, &nats.Msg{
				Header: nats.Header{
					"Id":               []string{msg.Id},
					"Chat-Id":          []string{msg.Chat},
					"Sender-Id":        []string{user.Id},
					"Sender-Device-Id": []string{user.DeviceId},
					// Non string fields
					"Sequence": []string{strconv.Itoa(msg.Sequence)},
				},
				Subject: subject,
				Data:    []byte(msg.Text),
			})
		}

	case "subscription":
		return

	case "unsubscription":
		return
	}
}

func (hr *MessageHandler) onReceive(_ context.Context, user User, msg jetstream.Msg, wsCnc *websocket.Conn) {
	ack := func() {
		err := msg.Ack()

		if err != nil {
			log.Printf("'Ack' sending error: '%s'\n", err.Error())
		}
	}

	log.Printf("Receive message: '%s:%s'\n", user.Id, user.Name)

	headers := msg.Headers()

	if headers == nil {
		ack()
		log.Printf("Ignore message with empty headers\n")
		return
	}

	sequence, err := strconv.Atoi(headers.Get("Sequence"))

	if err != nil {
		ack()
		log.Printf("Ignore message with incorrect sequence: '%s'\n", err.Error())
		return
	}

	err = hr.send("message", Message{
		Id:       headers.Get("Id"),
		Chat:     headers.Get("Chat-Id"),
		Sequence: sequence,
		Text:     string(msg.Data()),
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

func (hr *MessageHandler) distribute(oprType string, message any) {
	for _, user := range hr.OnlineUsers.List() {
		// TODO: Replace lock with chanel?
		user.wsMtx.Lock()
		err := hr.send(oprType, message, user.wsCnc)
		user.wsMtx.Unlock()

		if err != nil {
			log.Printf("Notify sending error: '%s'\n", err.Error())
		}
	}
}

type OnlineUserHandler struct {
	Session     SessionService
	Config      Config
	OnlineUsers Registry[string, OnlineUser]
}

func (hr *OnlineUserHandler) List(w http.ResponseWriter, r *http.Request) {
	user, err := hr.Session.GetUser(r)

	if err != nil {
		log.Printf("Session parse error: %s\n", err.Error())
		return
	}

	sls := slices.DeleteFunc(hr.OnlineUsers.List(), func(onlUser OnlineUser) bool {
		return onlUser.Id == user.Id
	})

	v, err := json.Marshal(sls)

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
