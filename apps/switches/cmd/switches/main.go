package main

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"mp/switches/pkg/kasa"
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
	Port    int    `json:"port"`
}

func main() {
	logger := mustMakeLogger()
	if len(os.Args) != 2 {
		logger.Error("missing path to switches.json")
		_, _ = fmt.Fprintf(os.Stderr, "Usage: %s /path/to/switches.json", os.Args[0])
		os.Exit(1)
	}
	configPath := os.Args[1]

	var devices []switches.Switch
	for _, cfg := range mustParseConfigs(configPath, logger) {
		logger.Debug("got switch cfg", "cfg", cfg)

		switch cfg.Kind {
		case "wemo/v1":
			devices = append(devices, &wemo.Wemo{
				Id:      cfg.Id,
				Name:    cfg.Name,
				Address: net.ParseIP(cfg.Address),
				Port:    cfg.Port,
				Logger:  logger,
			})
		case "kasa/v1":
			devices = append(devices, kasa.New(
				cfg.Id,
				net.ParseIP(cfg.Address),
				logger,
			))
		default:
			panic(fmt.Sprintf("unknown kind: %s", cfg.Kind))
		}
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

	h := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{AddSource: true, Level: level})
	return slog.New(h)
}

func mustParseConfigs(configPath string, logger *slog.Logger) (cfgs []switchConfig) {
	logger.Info("reading config", "configPath", configPath)
	file, err := os.Open(configPath)
	if err != nil {
		panic(err)
	}
	defer func() { _ = file.Close() }()

	if err := json.NewDecoder(file).Decode(&cfgs); err != nil {
		panic(err)
	}

	return
}
