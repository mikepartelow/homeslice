package station

import (
	"fmt"
	"log/slog"
	"mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/player"
	"mp/gosonos/pkg/track"
	"mp/gosonos/pkg/ttlt"
	"os"
	"time"

	"github.com/phsym/console-slog"
)

const (
	IsPlayingOnCacheTTL = time.Duration(16 * time.Second)
)

type Station struct {
	ID     curation.ID
	Logger *slog.Logger
	Name   string
	URI    track.URI
	Volume player.Volume

	isPlayingOn *ttlt.TTLT[bool]
}

func (s *Station) Enqueue(player player.Player) error {
	return player.PlayURI(s.URI, s.Name)
}

func (s *Station) Shuffle(player player.Player) error {
	return nil
}

var _ curation.Curation = &Station{}

func (s *Station) GetID() curation.ID {
	return s.ID
}

func (s *Station) GetName() string {
	return s.Name
}

func (s *Station) GetVolume() player.Volume {
	return s.Volume
}

func (s *Station) IsPlayingOn(player player.Player) (bool, error) {
	s.init()

	if is, ok := s.isPlayingOn.GetValue(); ok {
		s.Logger.Debug("s.isPlayingOn", "is", is)
		return is, nil
	}

	channel, err := player.Channel()
	if err != nil {
		// don't set s.isPlayingOn because we didn't answer the question one way or the other
		return false, fmt.Errorf("error fetching channel from player %q: %w", player.Address().String(), err)
	}
	s.Logger.Debug("IsPlayingOn", "channel", channel)

	if channel != s.Name {
		return s.isPlayingOn.SetValue(false), nil
	}

	isPlaying, err := player.IsPlaying()
	if err != nil {
		// don't set p.isPlayingOn because we didn't answer the question one way or the other
		return false, fmt.Errorf("error getting IsPlaying status from player %q: %w", player.Address().String(), err)
	}

	return s.isPlayingOn.SetValue(isPlaying), nil
}

func (s *Station) Play(player player.Player) error {
	return player.Play()
}

func New(id curation.ID, name string, uri track.URI, volume player.Volume, logger *slog.Logger) (*Station, error) {
	s := &Station{
		ID:     id,
		Logger: logger,
		Name:   name,
		URI:    uri,
		Volume: volume,
	}
	s.init()

	return s, nil
}

func (s *Station) init() {
	if s.Logger == nil {
		s.Logger = slog.New(
			console.NewHandler(os.Stderr, &console.HandlerOptions{Level: slog.LevelError}),
		)
	}
	if s.isPlayingOn == nil {
		s.isPlayingOn = ttlt.New[bool](IsPlayingOnCacheTTL)
	}
}
