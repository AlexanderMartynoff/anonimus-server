package main

import (
	"anonimus-server/anonimus"

	"log"
	"net/http"
	"os"
)

func main() {
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

	tickerService := anonimus.NewTickerService(1, func ()  {
		log.Printf("Hello, World!")
	})

	onlineUserService := anonimus.NewOnlineUserService()
	sessionService := anonimus.NewSessionService("user")

	messageHandler := anonimus.MessageHandler{Settings: settings, OnlineUserService: &onlineUserService, SessionService: &sessionService}
	onlineUserHandler := anonimus.OnlineUserHandler{Settings: settings, OnlineUserService: &onlineUserService, SessionService: &sessionService}

	router := http.NewServeMux()

	router.HandleFunc("/api/serve", messageHandler.Serve)
	router.HandleFunc("/api/online-user", onlineUserHandler.List)

	server := http.Server{
		Handler: router,
		Addr:    settings.Addr,
	}

	tickerService.Start()

	log.Printf("Start server on: %s\n", server.Addr)

	err = server.ListenAndServe()

	if err == nil {
		log.Printf("Stop server")
	} else {
		log.Printf("Stop server with error: '%s'", err)
	}
}
