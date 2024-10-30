package config

import (
	"fmt"
	"io"
	"log/slog"
	"mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/player"
	"mp/gosonos/pkg/playlist"
	"mp/gosonos/pkg/sonos"
	"mp/gosonos/pkg/station"
	"mp/gosonos/pkg/track"
	"os"
	"strconv"

	"github.com/phsym/console-slog"
	"gopkg.in/yaml.v3"
)

type Config struct {
	Coordinator player.Player
	Players     []player.Player

	Curations map[curation.ID]curation.Curation

	ListenPort int
}

func getenvOrError(name string) (string, error) {
	val := os.Getenv(name)
	if val == "" {
		return "", fmt.Errorf("missing required env var %q", name)
	}
	return val, nil
}

func getenvOrDefault(name, defaultValue string) string {
	if val := os.Getenv(name); val != "" {
		return val
	}
	return defaultValue
}

func (c *Config) Load() (*slog.Logger, error) {
	// FIXME: log level from env
	logger := slog.New(console.NewHandler(os.Stderr, &console.HandlerOptions{Level: slog.LevelDebug}))

	port, err := strconv.Atoi(getenvOrDefault("LISTEN_PORT", "8000"))
	if err != nil {
		return nil, fmt.Errorf("invalid value for LISTEN_PORT: %w", err)
	}
	c.ListenPort = port

	configPath, err := getenvOrError("CONFIG_PATH")
	if err != nil {
		return nil, err
	}

	file, err := os.Open(configPath)
	if err != nil {
		return nil, fmt.Errorf("couldn't open config file at %q: %w", configPath, err)
	}
	defer file.Close()

	err = c.parse(file, logger)
	if err != nil {
		return nil, fmt.Errorf("error parsing config file %q: %w", configPath, err)
	}

	return logger, nil
}

type config struct {
	Kind        string        `yaml:"kind"`
	Coordinator string        `yaml:"coordinator"`
	Players     []string      `yaml:"players"`
	Playlists   []cfgplaylist `yaml:"playlists"`
	Stations    []cfgstation  `yaml:"stations"`
}

type cfgplaylist struct {
	ID       string   `yaml:"id"`
	Kind     string   `yaml:"kind"`
	Name     string   `yaml:"name"`
	TrackIDs []string `yaml:"track_ids"`
	Volume   *int     `yaml:"volume"`
}

type cfgstation struct {
	ID     string `yaml:"id"`
	Kind   string `yaml:"kind"`
	Name   string `yaml:"name"`
	URI    string `yaml:"uri"`
	Volume *int   `yaml:"volume"`
}

func (c *Config) parse(r io.Reader, logger *slog.Logger) error {
	var cfg config
	err := yaml.NewDecoder(r).Decode(&cfg)
	if err != nil {
		return fmt.Errorf("error parsing config YAML: %w", err)
	}

	coordinator, players, err := makePlayers(cfg, logger)
	if err != nil {
		return fmt.Errorf("couldn't parse players: %w", err)
	}
	(*c).Coordinator = coordinator
	(*c).Players = players

	(*c).Curations = make(map[curation.ID]curation.Curation)

	err = makePlaylists(cfg, c.Curations, logger)
	if err != nil {
		return fmt.Errorf("couldn't parse playlists: %w", err)
	}

	err = makeStations(cfg, c.Curations, logger)
	if err != nil {
		return fmt.Errorf("couldn't parse stations: %w", err)
	}

	return nil
}

func makePlayers(cfg config, logger *slog.Logger) (player.Player, []player.Player, error) {
	coordinator, err := sonos.New(cfg.Coordinator, logger)
	if err != nil {
		return nil, nil, fmt.Errorf("error creating Sonos Player %q: %w", cfg.Coordinator, err)
	}

	var players []player.Player
	for _, pl := range cfg.Players {
		player, err := sonos.New(pl, logger)
		if err != nil {
			return nil, nil, fmt.Errorf("error creating Sonos Player %q: %w", pl, err)
		}
		players = append(players, player)
	}

	return coordinator, players, nil
}

func makePlaylists(cfg config, m map[curation.ID]curation.Curation, logger *slog.Logger) error {
	for _, pl := range cfg.Playlists {
		if pl.Volume == nil {
			n := player.DefaultVolume
			pl.Volume = &n
		}

		var tracks []track.Track
		for _, t := range pl.TrackIDs {
			tracks = append(tracks, &playlist.TidalTrack{ID: track.TrackID(t)})
		}

		id, err := curation.ParseID(pl.ID)
		if err != nil {
			return fmt.Errorf("error parsing playlist id %q: %w", pl.ID, err)
		}

		p, err := playlist.New(id, pl.Name, tracks, player.Volume(*pl.Volume), logger)
		if err != nil {
			return fmt.Errorf("error creating Playlist: %w", err)
		}

		if _, ok := m[p.GetID()]; ok {
			return fmt.Errorf("duplicate curation id %q", p.GetID())
		}

		m[p.GetID()] = p
	}

	return nil
}

func makeStations(cfg config, m map[curation.ID]curation.Curation, logger *slog.Logger) error {
	for _, st := range cfg.Stations {
		if st.Volume == nil {
			n := player.DefaultVolume
			st.Volume = &n
		}

		id, err := curation.ParseID(st.ID)
		if err != nil {
			return fmt.Errorf("error parsing station id %q: %w", st.ID, err)
		}

		s, err := station.New(id, st.Name, track.URI(st.URI), player.Volume(*st.Volume), logger)
		if err != nil {
			return fmt.Errorf("error creating Station: %w", err)
		}

		if _, ok := m[s.GetID()]; ok {
			return fmt.Errorf("duplicate curation id %q", s.GetID())
		}

		m[s.GetID()] = s
	}

	return nil
}
