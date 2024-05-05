package anonimus

import (
	"encoding/json"
	"net/http"
	"net/url"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

type SessionService struct {
	CookieName string
}

func (service *SessionService) GetUser(r *http.Request) (*User, error) {
	cookie, err := r.Cookie(service.CookieName)

	if err != nil {
		return nil, err
	}

	value, err := url.PathUnescape(cookie.Value)

	if err != nil {
		return nil, err
	}

	user := &User{}

	err = json.Unmarshal([]byte(value), user)

	if err != nil {
		return nil, err
	}

	return user, nil
}

func NewSessionService(cookieName string) SessionService {
	return SessionService{
		CookieName: cookieName,
	}
}

type OnlineUserService struct {
	onlineUsers sync.Map
}

type OnlineUser struct {
	User   *User
	Socket *websocket.Conn
}

func (srv *OnlineUserService) Get(id string) (*websocket.Conn, bool) {
	v, ok := srv.onlineUsers.Load(id)

	if !ok {
		return nil, ok
	}

	return v.(*websocket.Conn), true
}

func (srv *OnlineUserService) Add(id string, o OnlineUser) {
	srv.onlineUsers.Store(id, o)
}

func (srv *OnlineUserService) Delete(id string) {
	srv.onlineUsers.Delete(id)
}

func (srv *OnlineUserService) Items() []OnlineUser {
	onlineUsers := make([]OnlineUser, 10)

	srv.onlineUsers.Range(func(k any, v any) bool {
		onlineUsers = append(onlineUsers, v.(OnlineUser))
		return true
	})

	return onlineUsers
}

func (srv *OnlineUserService) Len() int {
	return len(srv.Items())
}

func NewOnlineUserService() OnlineUserService {
	return OnlineUserService{
		onlineUsers: sync.Map{},
	}
}

type TickerService struct {
	timeout int
	stop    chan bool
	tasks   []func()
}

func (srv *TickerService) Start() {
	for _, task := range srv.tasks {
		go func(task func(), ticker *time.Ticker) {
			for {
				select {
				case <-ticker.C:
					task()
				case v := <-srv.stop:
					if v {
						ticker.Stop()
						return
					}
				}
			}
		}(task, time.NewTicker(time.Duration(srv.timeout) * time.Second))
	}
}

func (srv *TickerService) Stop() {
	srv.stop <- true
}

func NewTickerService(timeout int, tasks ...func()) TickerService {
	return TickerService{
		stop:    make(chan bool),
		timeout: timeout,
		tasks:   tasks,
	}
}
