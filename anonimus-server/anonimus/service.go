package anonimus

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"net/url"
	"sync"
	"time"

	"github.com/gorilla/websocket"
	"github.com/nats-io/nats.go"
	"github.com/nats-io/nats.go/jetstream"
)

// SessionService
type SessionService struct {
	CookieName string
}

func (srv *SessionService) GetUser(r *http.Request) (User, error) {
	cookie, err := r.Cookie(srv.CookieName)

	if err != nil {
		return User{}, err
	}

	value, err := url.PathUnescape(cookie.Value)

	if err != nil {
		return User{}, err
	}

	user := User{}

	err = json.Unmarshal([]byte(value), &user)

	if err != nil {
		return User{}, err
	}

	return user, nil
}

func NewSessionService(cookieName string) SessionService {
	return SessionService{
		CookieName: cookieName,
	}
}

type Onliner struct {
	User *User
	Wc   *websocket.Conn
}

// MessageService
type MessageService interface {
	SendMessage(msg Message)
	RegisterOnliner(user User, wc *websocket.Conn) error
	UnregisterOnliner(user User)
	ListUsers() []User
	Start()
	Stop()
}

type messageService struct {
	nc *nats.Conn
	js jetstream.JetStream

	parentCtx context.Context
	ctx       context.Context
	cancel    context.CancelFunc

	onls   map[string]Onliner
	onlsMu sync.Mutex
}

func (srv *messageService) SendMessage(msg Message) {
	srv.js.Publish(srv.ctx, "orders.message", []byte(msg.Text))
}

func (srv *messageService) RegisterOnliner(user User, wc *websocket.Conn) error {
	srv.onlsMu.Lock()
	defer srv.onlsMu.Unlock()

	_, _ = srv.js.CreateOrUpdateStream(srv.ctx, jetstream.StreamConfig{
		Name:     "orders",
		Subjects: []string{"1", "2"},
	})

	srv.onls[user.Device] = Onliner{
		User: &user,
		Wc:   wc,
	}

	return nil
}

func (srv *messageService) UnregisterOnliner(user User) {
	srv.onlsMu.Lock()
	defer srv.onlsMu.Unlock()
}

func (srv *messageService) ListUsers() []User {
	srv.onlsMu.Lock()
	defer srv.onlsMu.Unlock()

	ln := len(srv.onls)
	ls := make([]User, ln)

	for _, v := range srv.onls {
		ln--
		ls[ln] = *v.User
	}

	return ls
}

func (srv *messageService) Start() {
	nc, err := nats.Connect(nats.DefaultURL)

	if err != nil {
		log.Printf("NATS error: %s\n", err.Error())
	}

	srv.nc = nc

	js, err := jetstream.New(nc)

	if err != nil {
		log.Printf("NATS JS error: %s\n", err.Error())
	}

	srv.js = js

	ctx, cancel := context.WithTimeout(srv.parentCtx, 30*time.Second)

	srv.ctx = ctx
	srv.cancel = cancel
}

func (srv *messageService) Stop() {
	srv.cancel()
}

func NewMessageService(ctx context.Context) MessageService {
	return &messageService{
		parentCtx: ctx,
	}
}
