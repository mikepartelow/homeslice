package station

import (
	"fmt"
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

func (s *Station) GetID() curation.ID {
	panic("NIY")
}

func (p *Station) GetName() string {
	panic("NIY")
}

func (s *Station) GetVolume() player.Volume {
	fmt.Println("FIXME")
	return 0
}

func (s *Station) IsPlayingOn(player player.Player) (bool, error) {
	panic("NIY")
	return false, nil
}
