package config

import (
	"fmt"
	"io"
	c "mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/player"
	p "mp/gosonos/pkg/playlist"
	"mp/gosonos/pkg/sonos"
	"mp/gosonos/pkg/track"
	"net"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Coordinator player.Player
	Players     []player.Player
	Curations   []c.Curation
}

type config struct {
	Kind        string     `yaml:"kind"`
	Coordinator string     `yaml:"coordinator"`
	Players     []string   `yaml:"players"`
	Playlists   []playlist `yaml:"playlists"`
	Stations    []station  `yaml:"stations"`
}

type playlist struct {
	ID       string   `yaml:"id"`
	Kind     string   `yaml:"kind"`
	Name     string   `yaml:"name"`
	TrackIDs []string `yaml:"track_ids"`
}

type station struct {
	ID   string `yaml:"id"`
	Kind string `yaml:"kind"`
	Name string `yaml:"name"`
	URI  string `yaml:"uri"`
}

func (c *Config) Parse(r io.Reader) error {
	var cfg config
	err := yaml.NewDecoder(r).Decode(&cfg)
	if err != nil {
		return fmt.Errorf("error parsing config YAML: %w", err)
	}

	// FIXME: validations

	a, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("%s:%d", cfg.Coordinator, sonos.PlayerPort))
	if err != nil {
		return fmt.Errorf("couldn't resolve coordinator IP address %q: %w", cfg.Coordinator, err)
	}
	(*c).Coordinator = &sonos.Player{Addr: a}

	for _, pl := range cfg.Players {
		a, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("%s:%d", pl, sonos.PlayerPort))
		if err != nil {
			return fmt.Errorf("couldn't resolve player IP address %q: %w", pl, err)
		}
		(*c).Players = append((*c).Players, &sonos.Player{Addr: a})
	}

	for _, pl := range cfg.Playlists {
		var tracks []track.Track

		for _, t := range pl.TrackIDs {
			tracks = append(tracks, &p.TidalTrack{ID: track.TrackID(t)})
		}

		(*c).Curations = append(c.Curations, &p.Playlist{
			Name:   pl.Name,
			Tracks: tracks,
		})
	}

	return nil
}
