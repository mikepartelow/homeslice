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

func Play(c Curation, coordinator player.Player, players []player.Player, volume int) error {
	if err := coordinator.ClearQueue(); err != nil {
		return fmt.Errorf("couldn't clear queue on player %q: %w", coordinator.Address().String(), err)
	}
	if err := coordinator.SetVolume(volume); err != nil {
		return fmt.Errorf("couldn't set volume on player %q: %w", coordinator.Address().String(), err)
	}
	if err := c.Enqueue(coordinator); err != nil {
		return fmt.Errorf("couldn't enqueue curation on player %q: %w", coordinator.Address().String(), err)
	}
	if err := coordinator.Play(); err != nil {
		return fmt.Errorf("couldn't play on player %q: %w", coordinator.Address().String(), err)
	}

	for _, p := range players {
		if err := p.SetVolume(volume); err != nil {
			p.Logger().Error("error setting volume on %q: %w", p.Address().String(), err)
		}
		if err := p.Join(coordinator); err != nil {
			p.Logger().Error("error joining %q to coordinator %q: %w", p.Address().String(), coordinator.Address().String(), err)
		}
	}
	return nil
}
