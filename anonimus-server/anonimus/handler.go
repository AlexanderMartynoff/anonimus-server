package anonimus

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"

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

	// TODO: Replace `wscMtx` with chanel?
	csSrv  *consumerService `json:"-"`
	wsCn   *websocket.Conn  `json:"-"`
	wscMtx *sync.Mutex      `json:"-"`
}

type MessageHandler struct {
	Cfg             Config
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

	wsCn, err := Upgrader.Upgrade(w, r, http.Header{
		"X-Anonimus-Server-Version": {hr.Cfg.Version},
	})

	if err != nil {
		log.Printf("Websocket upgrade error: %s\n", err.Error())
	}

	ctx := context.Background()

	csSrv, err := hr.ConsumerFactory.Get(ctx, user.Id, user.DeviceId)

	if err != nil {
		log.Printf("Register consumer error: %s. Close connection\n", err.Error())
		return
	}

	wscMtx := sync.Mutex{}

	csSrv.Consume = func(msg jetstream.Msg) {
		hr.onConsume(ctx, msg, wsCn, &wscMtx)
	}

	err = csSrv.Start(ctx)

	if err != nil {
		log.Printf("Start consumer error: %s\n", err.Error())
		return
	}

	hr.OnlineUsers.Set(user.DeviceId, OnlineUser{
		Id:       user.Id,
		DeviceId: user.DeviceId,
		Name:     user.Name,

		// TODO: Refactring?
		csSrv:  &csSrv,
		wscMtx: &wscMtx,
		wsCn:   wsCn,
	})

	hr.sendToOnlineUsers("event", Event{
		Name: "connect",
	})

	defer func() {
		log.Printf("Close handler '%s:%s'", user.DeviceId, user.Name)

		csSrv.Stop()
		wsCn.Close()

		hr.OnlineUsers.Delete(user.DeviceId)

		hr.sendToOnlineUsers("event", Event{
			Name: "disconnect",
		})
	}()

	wsCn.WriteMessage(websocket.PingMessage, []byte{})

	for {
		msgType, msgData, err := wsCn.ReadMessage()

		if err != nil {
			log.Printf("websocket reading error: %s\n", err.Error())
			break
		}

		switch msgType {

		case websocket.CloseMessage:
			return

		case websocket.TextMessage:
			var cmd Command

			err := json.Unmarshal(msgData, &cmd)

			if err != nil {
				log.Printf("Message parsing error: '%s'", err.Error())
			}

			hr.onPublish(ctx, cmd.Type, cmd.Data)

		default:
			log.Printf("Unknown message type: '%d'", msgType)
		}
	}
}

func (hr *MessageHandler) onPublish(ctx context.Context, msgType string, pbData []byte) {
	switch msgType {

	case "message":
		// TODO: Validate message!
		var pbMsg PublishingMessage

		err := json.Unmarshal(pbData, &pbMsg)

		if err != nil {
			log.Printf("Message unmarshaling error: '%s'", err.Error())
			return
		}

		msg := Message{
			Id: pbMsg.Id,

			SenderId:       pbMsg.SenderId,
			SenderDeviceId: pbMsg.SenderDeviceId,
			SenderName:     pbMsg.SenderName,

			Chat:     pbMsg.Chat,
			Sequence: pbMsg.Sequence,
			Text:     pbMsg.Text,
		}

		data, err := json.Marshal(msg)

		if err != nil {
			log.Printf("Message marshaling error: '%s'", err.Error())
			return
		}

		if len(pbMsg.ChatSubjects) == 0 {
			// TODO: Implement fetch subjects in DB
			return
		}

		// Send if subjets present in message
		for _, subject := range pbMsg.ChatSubjects {
			hr.Publisher.PublishMsg(ctx, &nats.Msg{
				Subject: subject,
				Data:    data,
			})
		}

	case "subscription":
		return

	case "unsubscription":
		return
	}
}

func (hr *MessageHandler) onConsume(_ context.Context, jsMsg jetstream.Msg, wsCn *websocket.Conn, wscMtx *sync.Mutex) {
	ack := func() {
		err := jsMsg.Ack()

		if err != nil {
			log.Printf("'Ack' sending error: '%s'\n", err.Error())
		}
	}

	msg := Message{}

	err := json.Unmarshal(jsMsg.Data(), &msg)

	if err != nil {
		log.Printf("Consumer message unmarshaling error: '%s'", err.Error())
		return
	}

	err = hr.send("message", msg, wsCn, wscMtx)

	if err == nil {
		ack()
	} else {
		log.Printf("'OnReceive' sending error: '%s'\n", err.Error())
	}
}

func (hr *MessageHandler) send(cmdType string, message any, wsCn *websocket.Conn, wscMtx *sync.Mutex) error {
	v, err := json.Marshal(message)

	if err != nil {
		return err
	}

	cmd := Command{
		Type: cmdType,
		Time: time.Now().Unix(),
		Data: v,
	}

	v, err = json.Marshal(cmd)

	if err != nil {
		return err
	}

	wscMtx.Lock()
	err = wsCn.WriteMessage(websocket.TextMessage, v)
	wscMtx.Unlock()

	if err != nil {
		return err
	}

	return nil
}

func (hr *MessageHandler) sendToOnlineUsers(oprType string, message any) {
	for _, olUser := range hr.OnlineUsers.List() {
		err := hr.send(oprType, message, olUser.wsCn, olUser.wscMtx)

		if err != nil {
			log.Printf("Broadcat sending error: '%s'\n", err.Error())
		}
	}
}

type OnlineUserHandler struct {
	Session     SessionService
	Cfg         Config
	OnlineUsers Registry[string, OnlineUser]
}

func (hr *OnlineUserHandler) List(w http.ResponseWriter, r *http.Request) {
	v, err := json.Marshal(hr.OnlineUsers.List())

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

type PurgeHandler struct {
	Config *Config
}

func (hr *PurgeHandler) Delete(w http.ResponseWriter, r *http.Request) {
}
