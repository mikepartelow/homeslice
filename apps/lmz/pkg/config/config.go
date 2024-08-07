package config

import (
	"bytes"
	_ "embed"

	"github.com/goccy/go-yaml"
)

//go:embed config.yaml
var configYaml []byte

// Config holds auth credentials and machine serial number
type Config struct {
	Auth struct {
		Username     string `yaml:"username"`
		Password     string `yaml:"password"`
		ClientId     string `yaml:"client_id"`
		ClientSecret string `yaml:"client_secret"`
	} `yaml:"auth"`
	Serial string `yaml:"serial"`
}

// MustRead returns a Config initialized from embedded config, or panics.
func MustRead() *Config {
	var config Config

	err := yaml.NewDecoder(bytes.NewReader(configYaml)).Decode(&config)
	if err != nil {
		panic(err)
	}

	return &config
}
