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
		log.Panic("Unknown assets directory path")
	}

	config, settingsPath, err := anonimus.ReadConfig("config.json", assetsPath)

	if err != nil {
		log.Panicf("Read config: %s\n", err.Error())
	}

	log.Printf("Read config: %s\n", settingsPath)

	// 0. NATS
	natsCnc, err := nats.Connect(nats.DefaultURL)

	if err != nil {
		log.Panicf("NATS connection: %s\n", err.Error())
	}

	natsJs, err := jetstream.New(natsCnc)

	if err != nil {
		log.Panicf("NATS jetstream creation: %s\n", err.Error())
	}

	log.Printf("NATS connection on: %s\n", nats.DefaultURL)

	// 1. HTTP Handlers
	consumerSrv := anonimus.NewConsumerFactoryService(natsJs)
	sessionSrv := anonimus.NewSessionService("user")
	ouRegistry := anonimus.NewRegistry[string, anonimus.OnlineUser]()

	messageHandler := anonimus.MessageHandler{
		Config:          config,
		ConsumerFactory: consumerSrv,
		Session:         sessionSrv,
		OnlineUsers:     ouRegistry,
		Publisher:       natsJs,
	}
	onlineUserHandler := anonimus.OnlineUserHandler{
		Config:      config,
		Session:     sessionSrv,
		OnlineUsers: ouRegistry,
	}

	router := http.NewServeMux()

	router.HandleFunc("/api/serve", messageHandler.Serve)
	router.HandleFunc("/api/online-user", onlineUserHandler.List)

	server := http.Server{
		Handler: router,
		Addr:    config.Addr,
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
