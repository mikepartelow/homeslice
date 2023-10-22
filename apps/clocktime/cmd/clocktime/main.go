package main

import (
	"log/slog"
	"mp/clocktime/pkg/clocktime"
	"net/http"
	"os"
	"strconv"
	"time"
)

const Port = 8000

func main() {
	logger := slog.Default()
	server := clocktime.Server{
		Location: getLocation(logger),
	}
	logger.Info("Listening", "port", Port)
	err := http.ListenAndServe(":"+strconv.Itoa(Port), server)
	logger.Error(err.Error())
}

func getLocation(logger *slog.Logger) (location *time.Location) {
	location = time.UTC

	if v := os.Getenv("LOCATION"); v != "" {
		var err error
		location, err = time.LoadLocation(v)
		if err != nil {
			logger.Error(err.Error())
			panic(err)
		}
	}

	logger.Info("getLocation", "location", location)
	return
}
