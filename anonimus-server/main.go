package main

import (
	"anonimus-server/anonimus"

	"context"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/nats-io/nats.go"
	"github.com/nats-io/nats.go/jetstream"
)

func main() {
	// 0. Settings
	assetsPath, ok := os.LookupEnv("ANONIMUS_ASSETS_PATH")

	if !ok {
		panic("Unknown assets directory path")
	}

	settings, settingsPath, err := anonimus.ReadSettings("settings.json", assetsPath)

	if err != nil {
		log.Printf("Read settings file with error: %s\n", err.Error())
		return
	}

	log.Printf("Read settings from : %s\n", settingsPath)

	// 1. HTTP Handlers
	messageSrv := anonimus.NewMessageService(context.Background())
	sessionSrv := anonimus.NewSessionService("user")

	messageHandler := anonimus.MessageHandler{
		Settings:   settings,
		MessageSrv: messageSrv,
		SessionSrv: &sessionSrv,
	}
	onlineUserHandler := anonimus.OnlineUserHandler{
		Settings:   settings,
		MessageSrv: messageSrv,
		SessionSrv: &sessionSrv,
	}

	router := http.NewServeMux()

	router.HandleFunc("/api/serve", messageHandler.Serve)
	router.HandleFunc("/api/online-user", onlineUserHandler.List)

	server := http.Server{
		Handler: router,
		Addr:    settings.Addr,
	}

	// 2. NATS messanging
	nc, err := nats.Connect(nats.DefaultURL)

	if err != nil {
		log.Printf("NATS error: %s\n", err.Error())
	}

	js, err := jetstream.New(nc)

	if err != nil {
		log.Printf("NATS JS error: %s\n", err.Error())
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// stream, _ := js.CreateOrUpdateStream(ctx, jetstream.StreamConfig{
	//     Name:     "orders",
	//     Subjects: []string{"1.1", "1.2"},
	// })

	s, _ := js.Stream(ctx, "orders")

	info, _ := s.Info(ctx)

	log.Print("Subjects: ", info.Config.Subjects)

	js.UpdateStream(ctx, jetstream.StreamConfig{
		Name:     "orders",
		Subjects: []string{"1", "2"},
	})

	go func() {
		for i := 0; i < 100; i++ {
			js.Publish(ctx, "orders.message", []byte("Message"))
			time.Sleep(5 * time.Second)
		}
	}()

	// cns, _ := stream.CreateOrUpdateConsumer(ctx, jetstream.ConsumerConfig{
	//     Durable:   "cns",
	//     AckPolicy: jetstream.AckExplicitPolicy,
	// 	FilterSubject: "orders.message",
	// })

	// messages, _ := cns.Messages()

	// for i := 0; i < 100; i++ {
	// 	msg, err := messages.Next()

	// 	if err != nil {
	// 		log.Printf("Next message error: %s\n", err.Error())
	// 	}

	// 	msg.Ack()

	// 	log.Printf("Received a JetStream message via iterator: %s: %s\n", msg.Subject(), string(msg.Data()))
	// }

	// 3. Start server
	log.Printf("Start server on: %s\n", server.Addr)

	err = server.ListenAndServe()

	if err == nil {
		log.Printf("Stop server")
	} else {
		log.Printf("Stop server with error: '%s'", err)
	}
}
