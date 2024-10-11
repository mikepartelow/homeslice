package station

import (
	"mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/player"
	"sync"
)

type Station struct {
}

func (p *Station) Play(player player.Player) error {
	return nil
}

var _ curation.Curation = &Station{}

func (s *Station) Do(op curation.Op) error {
	return curation.Do(s, op)
}

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

func (s *Station) IsPlayingOn(player player.Player) (bool, error) {
	panic("NIY")
	return false, nil
}

func (s *Station) PlayOn(coordinator player.Player, players []player.Player, volume player.Volume, wg *sync.WaitGroup) error {
	return curation.Play(s, coordinator, players, volume, wg)
}
