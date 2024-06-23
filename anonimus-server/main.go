package main

import (
	"anonimus-server/anonimus"

	"log"
	"net/http"
	"os"

	"github.com/nats-io/nats.go"
	"github.com/nats-io/nats.go/jetstream"
)

func main() {
	// 0. Settings
	assetsPath, ok := os.LookupEnv("ANONIMUS_ASSETS_PATH")

	if !ok {
		log.Panicf("Unknown assets directory path")
	}

	cfg, cfgPath, err := anonimus.ReadConfig("config.json", assetsPath)

	if err != nil {
		log.Panicf("Read config: %s\n", err.Error())
	}

	log.Printf("Read config: %s\n", cfgPath)

	// 0. NATS
	natsCnc, _ := nats.Connect(nats.DefaultURL, func(opts *nats.Options) error {
		opts.RetryOnFailedConnect = true

		opts.DisconnectedErrCB = func(_ *nats.Conn, err error) {
			log.Printf("NATS disconnected\n")
		}

		opts.ConnectedCB = func(_ *nats.Conn) {
			log.Printf("NATS connected\n")
		}

		opts.ReconnectedCB = func(_ *nats.Conn) {
			log.Printf("NATS reconnect\n")
		}
		return nil
	})

	natsJs, err := jetstream.New(natsCnc)

	if err != nil {
		log.Panicf("NATS jetstream creation: %s\n", err.Error())
	}

	// 1. HTTP Handlers
	// nats.NewEncodedConn
	consumerSrv := anonimus.NewConsumerFactoryService(natsJs)
	sessionSrv := anonimus.NewSessionService("user")
	ouRegistry := anonimus.NewRegistry[string, anonimus.OnlineUser]()

	messageHandler := anonimus.MessageHandler{
		Cfg:             cfg,
		ConsumerFactory: consumerSrv,
		Session:         sessionSrv,
		OnlineUsers:     ouRegistry,
		Publisher:       natsJs,
	}

	onlineUserHandler := anonimus.OnlineUserHandler{
		Cfg:         cfg,
		Session:     sessionSrv,
		OnlineUsers: ouRegistry,
	}

	router := http.NewServeMux()

	router.HandleFunc("/api/serve", messageHandler.Serve)
	router.HandleFunc("/api/online-user", onlineUserHandler.List)

	server := http.Server{
		Handler: router,
		Addr:    cfg.Addr,
	}

	// 3. Start server
	log.Printf("Start server on: %s\n", server.Addr)

	err = server.ListenAndServe()

	if err == nil {
		log.Printf("Stop server")
	} else {
		log.Printf("Stop server with error: '%s'", err)
	}
}
