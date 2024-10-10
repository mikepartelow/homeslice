package curation

import (
	"fmt"
	"mp/gosonos/pkg/player"
	"sync"
)

type Curation interface {
	Enqueue(player.Player) error
	IsPlayingOn(player.Player) (bool, error)
	GetName() string
}

func Play(c Curation, coordinator player.Player, players []player.Player, volume int, wg *sync.WaitGroup) error {
	if err := coordinator.Ungroup(); err != nil {
		return fmt.Errorf("couldn't ungroup on coordinator %q: %w", coordinator.Address().String(), err)
	}
	if err := coordinator.ClearQueue(); err != nil {
		return fmt.Errorf("couldn't clear queue on coordinator %q: %w", coordinator.Address().String(), err)
	}
	if err := coordinator.SetVolume(volume); err != nil {
		return fmt.Errorf("couldn't set volume on coordinator %q: %w", coordinator.Address().String(), err)
	}
	if err := c.Enqueue(coordinator); err != nil {
		return fmt.Errorf("couldn't enqueue curation on coordinator %q: %w", coordinator.Address().String(), err)
	}
	if err := coordinator.Play(); err != nil {
		return fmt.Errorf("couldn't play on coordinator %q: %w", coordinator.Address().String(), err)
	}

	for _, p := range players {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if err := p.SetVolume(volume); err != nil {
				p.Logger().Error("error setting volume", "player", p.Address().String(), "error", err)
			}
			if err := p.Join(coordinator); err != nil {
				p.Logger().Error("error joining", "player", p.Address().String(), "coordinator", coordinator.Address().String(), "error", err)
			}
		}()
	}
	return nil
}
