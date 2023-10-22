package main

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"mp/switches/pkg/switches"
	"mp/switches/pkg/wemo"
	"net"
	"net/http"
	"os"
	"strconv"
	"strings"
)

const Port = 8000

type switchConfig struct {
	Id      string `json:"id"`
	Kind    string `json:"kind"`
	Name    string `json:"name"`
	Address string `json:"address"`
}

func main() {
	logger := mustMakeLogger()
	if len(os.Args) != 2 {
		logger.Error("missing path to switches.json")
		_, _ = os.Stderr.Write([]byte(fmt.Sprintf("Usage: %s /path/to/switches.json", os.Args[0])))
		os.Exit(1)
	}
	configPath := os.Args[1]

	var devices []switches.Switch
	for _, cfg := range mustParseConfigs(configPath, logger) {
		if cfg.Kind != "wemo/v1" {
			panic(fmt.Sprintf("unknown kind: %s", cfg.Kind))
		}
		logger.Debug("got switch cfg", "cfg", cfg)
		devices = append(devices, &wemo.Wemo{
			Id:      cfg.Id,
			Name:    cfg.Name,
			Address: net.ParseIP(cfg.Address),
			Logger:  logger,
		})
	}

	server := switches.NewServer(logger, devices)

	logger.Info("Listening", "port", Port)
	err := http.ListenAndServe(":"+strconv.Itoa(Port), server)
	logger.Error(err.Error())
}

func mustMakeLogger() *slog.Logger {
	level := slog.LevelInfo
	if v := os.Getenv("LOG_LEVEL"); v != "" {
		switch strings.ToLower(v) {
		case "debug":
			level = slog.LevelDebug
		case "info":
			level = slog.LevelInfo
		case "warn":
			level = slog.LevelWarn
		case "error":
			level = slog.LevelError
		default:
			panic(fmt.Sprintf("unknown log level: %s", v))
		}
	}

	h := slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: level})
	return slog.New(h)
}

func mustParseConfigs(configPath string, logger *slog.Logger) (cfgs []switchConfig) {
	logger.Info("reading config", "configPath", configPath)
	file, err := os.Open(configPath)
	if err != nil {
		panic(err)
	}
	defer file.Close()

	if err := json.NewDecoder(file).Decode(&cfgs); err != nil {
		panic(err)
	}

	return
}
