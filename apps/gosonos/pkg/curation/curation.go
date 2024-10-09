package curation

import (
	"fmt"
	"mp/gosonos/pkg/player"
)

type Curation interface {
	Enqueue(player.Player) error
	IsPlayingOn(player.Player) (bool, error)
	Name() string
}

func Play(c Curation, p player.Player, volume int) error {
	if err := p.ClearQueue(); err != nil {
		return fmt.Errorf("couldn't clear queue on player %q: %w", p.Address().String(), err)
	}
	if err := p.SetVolume(volume); err != nil {
		return fmt.Errorf("couldn't set volume on player %q: %w", p.Address().String(), err)
	}
	if err := c.Enqueue(p); err != nil {
		return fmt.Errorf("couldn't enqueue curation on player %q: %w", p.Address().String(), err)
	}
	if err := p.Play(); err != nil {
		return fmt.Errorf("couldn't play on player %q: %w", p.Address().String(), err)
	}
	return nil
}
