package main

import (
	"log/slog"
	"mp/buttons/pkg/buttons"
	"net/http"
	"os"
	"strconv"
)

const Port = 8000

func main() {
	logger := slog.New(slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: slog.LevelDebug}))
	server := buttons.NewServer(logger, mustGetClocktimeUrl(logger))
	logger.Info("Listening", "port", Port)
	err := http.ListenAndServe(":"+strconv.Itoa(Port), server)
	logger.Error(err.Error())
}

func mustGetClocktimeUrl(logger *slog.Logger) string {
	url := os.Getenv("CLOCKTIME_URL")
	if url == "" {
		logger.Error("couldn't get CLOCKTIME_URL", "url", url)
		panic("couldn't get CLOCKTIME_URL")
	}

	return url
}
