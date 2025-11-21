package main

import (
	"errors"
	"fmt"
	"log/slog"
	"mp/switches/pkg/kasa"
	"net"
	"os"
	"os/user"
	"strings"

	"gopkg.in/yaml.v3"
)

const (
	configPath = "~/.kasaclirc"
)

type config struct {
	Dinguses []struct {
		Name    string `yaml:"name"`
		Address string `yaml:"address"`
	} `yaml:"dinguses"`
}

func main() {
	if len(os.Args) != 3 {
		fmt.Println("Usage: kasacli <name> <on|off>")
		os.Exit(1)
	}

	name, state := os.Args[1], os.Args[2]

	usr, _ := user.Current()
	homeDir := usr.HomeDir
	configPath := strings.ReplaceAll(configPath, "~", homeDir)

	file, err := os.Open(configPath)
	check(err, fmt.Sprintf("Error: couldn't open config file at %q", configPath))
	defer func() { _ = file.Close() }()

	var cfg config
	err = yaml.NewDecoder(file).Decode(&cfg)
	check(err, fmt.Sprintf("Error: couldn't decode YAML config file at %q", configPath))

	var address string
	for _, dingus := range cfg.Dinguses {
		if dingus.Name == name {
			address = dingus.Address
			break
		}
	}
	if address == "" {
		check(errors.New(name), "Error: Unknown Kasa name")
	}

	h := slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: slog.LevelError})
	logger := slog.New(h)

	k := kasa.New("1", net.ParseIP(address), logger)

	switch strings.ToLower(state) {
	case "on":
		check(k.On(), "")
	case "off":
		check(k.Off(), "")
	default:
		check(errors.New(state), "Error: Unknown command")
	}
}

func check(err error, msg string) {
	if err != nil {
		fmt.Println(msg + " : " + err.Error())
		os.Exit(1)
	}
}
