package main

import (
	"mp/gosonos/pkg/config"
	"mp/gosonos/pkg/server"
)

func main() {
	var cfg config.Config

	logger, err := cfg.Load()
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
