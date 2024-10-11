package config

import (
	"fmt"
	"io"
	"log/slog"
	"mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/player"
	"mp/gosonos/pkg/playlist"
	"mp/gosonos/pkg/sonos"
	"mp/gosonos/pkg/track"
	"net"
	"regexp"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Coordinator player.Player
	Players     []player.Player

	Curations map[curation.ID]curation.Curation
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

func (c *Config) Parse(r io.Reader, logger *slog.Logger) error {
	var cfg config
	err := yaml.NewDecoder(r).Decode(&cfg)
	if err != nil {
		return fmt.Errorf("error parsing config YAML: %w", err)
	}

	// FIXME: validations
	// FIXME: too long, subroutines

	a, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("%s:%d", cfg.Coordinator, sonos.PlayerPort))
	if err != nil {
		return fmt.Errorf("couldn't resolve coordinator IP address %q: %w", cfg.Coordinator, err)
	}
	(*c).Coordinator = &sonos.Player{Addr: a, Logger: logger}

	for _, pl := range cfg.Players {
		a, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("%s:%d", pl, sonos.PlayerPort))
		if err != nil {
			return fmt.Errorf("couldn't resolve player IP address %q: %w", pl, err)
		}
		(*c).Players = append((*c).Players, &sonos.Player{Addr: a})
	}

	(*c).Curations = make(map[curation.ID]curation.Curation)

	for _, pl := range cfg.Playlists {
		if !regexp.MustCompile(`^[\w-]+$`).Match([]byte(pl.ID)) {
			return fmt.Errorf("playlist %q has invalid id %q", pl.Name, pl.ID)
		}
		cid := curation.ID(pl.ID)

		var tracks []track.Track
		for _, t := range pl.TrackIDs {
			tracks = append(tracks, &playlist.TidalTrack{ID: track.TrackID(t)})
		}
		if len(tracks) == 0 {
			return fmt.Errorf("playlist %q/%q has 0 tracks", pl.Name, pl.ID)
		}

		if pl.Volume == nil {
			n := player.DefaultVolume
			pl.Volume = &n
		}

		(*c).Curations[cid] = &playlist.Playlist{
			ID:     cid,
			Name:   pl.Name,
			Tracks: tracks,
			Volume: player.Volume(*pl.Volume),
		}
	}

	return nil
}
