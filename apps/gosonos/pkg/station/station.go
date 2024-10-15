package station

import (
	"log/slog"
	"mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/player"
)

type Station struct {
	ID     curation.ID
	Logger *slog.Logger
	Name   string
	Volume player.Volume
}

func (p *Station) Play(player player.Player) error {
	return nil
}

var _ curation.Curation = &Station{}

func (s *Station) Enqueue(player player.Player) error {
	panic("NIY")
	return nil
}

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
	panic("NIY")
	return false, nil
}

func New(id curation.ID, name string, volume player.Volume, logger *slog.Logger) (*Station, error) {
	s := &Station{
		ID:     id,
		Logger: logger,
		Name:   name,
		Volume: volume,
	}

	return s, nil
}
