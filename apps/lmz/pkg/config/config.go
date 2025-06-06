package config

import (
	"bytes"
	_ "embed"
	"os"
	"os/user"
	"path"

	"github.com/goccy/go-yaml"
)

// Config holds auth credentials and machine serial number
type Config struct {
	Auth struct {
		Username string `yaml:"username"`
		Password string `yaml:"password"`
	} `yaml:"auth"`
	Serial string `yaml:"serial"`
}

// MustRead returns a Config initialized from embedded config, or panics.
func MustRead() *Config {
	u, err := user.Current()
	if err != nil {
		panic(err)
	}

	configYaml, err := os.ReadFile(path.Join(u.HomeDir, ".config/lmz/config.yaml"))
	if err != nil {
		panic(err)
	}

	var config Config
	err = yaml.NewDecoder(bytes.NewReader(configYaml)).Decode(&config)
	if err != nil {
		panic(err)
	}

	return &config
}
