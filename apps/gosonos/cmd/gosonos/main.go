package main

import (
	"log/slog"
	"mp/gosonos/pkg/config"
	"mp/gosonos/pkg/server"
	"os"

	"github.com/phsym/console-slog"
)

func main() {
	logger := slog.New(console.NewHandler(os.Stderr, &console.HandlerOptions{Level: slog.LevelDebug}))

	file, err := os.Open("config.yaml")
	check(err)

	var cfg config.Config
	err = cfg.Parse(file, logger)
	check(err)

	for _, c := range cfg.Curations {
		logger.Debug("config", "got curation", c.GetID())
	}

	server := server.Server{
		Config: &cfg,
		Logger: logger,
	}

	panic(server.Serve())
}

func check(err error) {
	if err != nil {
		panic(err)
	}
}
