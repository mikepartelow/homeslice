package curation

import (
	"fmt"
	"mp/gosonos/pkg/player"
	"strings"
	"sync"
)

type ID string

func ParseID(s string) (ID, error) {
	return ID(strings.ToLower(s)), nil
}

type Op int

const (
	InvalidOp = iota
	PlayOp
)

func ParseOp(s string) (Op, error) {
	s = strings.ToLower(s)
	switch s {
	case "play":
		return PlayOp, nil
	}
	return InvalidOp, fmt.Errorf("invalid op %q", s)
}

type Curation interface {
	Do(Op, player.Player, []player.Player) error

	Enqueue(player.Player) error
	IsPlayingOn(player.Player) (bool, error)
	PlayOn(player.Player, []player.Player, player.Volume, *sync.WaitGroup) error

	GetID() ID
	GetName() string
	GetVolume() player.Volume
}

func Do(op Op, curation Curation, coordiator player.Player, players []player.Player) error {
	switch op {
	case PlayOp:
		return curation.PlayOn(coordiator, players, curation.GetVolume(), nil)
	}

	return fmt.Errorf("undoable op %d", op)
}

func Play(c Curation, coordinator player.Player, players []player.Player, wg *sync.WaitGroup) error {
	if err := coordinator.Ungroup(); err != nil {
		return fmt.Errorf("couldn't ungroup on coordinator %q: %w", coordinator.Address().String(), err)
	}
	if err := coordinator.ClearQueue(); err != nil {
		return fmt.Errorf("couldn't clear queue on coordinator %q: %w", coordinator.Address().String(), err)
	}
	if err := coordinator.SetVolume(c.GetVolume()); err != nil {
		return fmt.Errorf("couldn't set volume on coordinator %q: %w", coordinator.Address().String(), err)
	}
	if err := c.Enqueue(coordinator); err != nil {
		return fmt.Errorf("couldn't enqueue curation on coordinator %q: %w", coordinator.Address().String(), err)
	}
	if err := coordinator.Play(); err != nil {
		return fmt.Errorf("couldn't play on coordinator %q: %w", coordinator.Address().String(), err)
	}

	for _, p := range players {
		if wg != nil {
			wg.Add(1)
		}
		go func() {
			if wg != nil {
				defer wg.Done()
			}
			if err := p.SetVolume(c.GetVolume()); err != nil {
				p.GetLogger().Error("error setting volume", "player", p.Address().String(), "error", err)
			}
			if err := p.Join(coordinator); err != nil {
				p.GetLogger().Error("error joining", "player", p.Address().String(), "coordinator", coordinator.Address().String(), "error", err)
			}
		}()
	}
	return nil
}
