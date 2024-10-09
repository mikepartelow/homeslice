package station

import (
	"mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/player"
)

type Station struct {
}

func (p *Station) Play(player player.Player) error {
	return nil
}

var _ curation.Curation = &Station{}

func (s *Station) Enqueue(player player.Player) error {
	panic("NIY")
	return nil
}

func (s *Station) IsPlayingOn(player player.Player) (bool, error) {
	panic("NIY")
	return false, nil
}

func (p *Station) Name() string {
	panic("NIY")
}
