package curation

import (
	"fmt"
	"log/slog"
	"mp/gosonos/pkg/player"
	"sync"

	"golang.org/x/sync/errgroup"
)

type Curation interface {
	Enqueue(player.Player) error
	IsPlayingOn(player.Player) (bool, error)

	GetID() ID
	GetName() string
	GetVolume() player.Volume
}

func Do(op Op, curation Curation, coordiator player.Player, players []player.Player, logger *slog.Logger) (bool, error) {
	switch op {
	case PauseOp:
		return true, Pause(coordiator)
	case PlayOp:
		isPlaying, err := curation.IsPlayingOn(coordiator)
		logger.Debug("PlayOp", "isPlaying", isPlaying)
		if err == nil && isPlaying {
			return true, nil
		}
		return true, Play(curation, coordiator, players, nil, logger)
	case StatusOp:
		return curation.IsPlayingOn(coordiator)
	}

	return false, fmt.Errorf("undoable op %d", op)
}

func Pause(coordinator player.Player) error {
	if err := coordinator.Pause(); err != nil {
		return fmt.Errorf("couldn't pause coordinator %q: %w", coordinator.Address().String(), err)
	}
	return nil
}

func Play(c Curation, coordinator player.Player, players []player.Player, wg *sync.WaitGroup, logger *slog.Logger) error {
	var eg errgroup.Group

	eg.Go(func() error {
		logger.Debug("Unjoin")
		if err := coordinator.Unjoin(); err != nil {
			return fmt.Errorf("couldn't unjoin on coordinator %q: %w", coordinator.Address().String(), err)
		}
		return nil
	})

	eg.Go(func() error {
		logger.Debug("ClearQueue")
		if err := coordinator.ClearQueue(); err != nil {
			return fmt.Errorf("couldn't clear queue on coordinator %q: %w", coordinator.Address().String(), err)
		}
		return nil
	})

	eg.Go(func() error {
		logger.Debug("SetVolume")
		if err := coordinator.SetVolume(c.GetVolume()); err != nil {
			return fmt.Errorf("couldn't set volume on coordinator %q: %w", coordinator.Address().String(), err)
		}
		return nil
	})

	if err := eg.Wait(); err != nil {
		return err
	}

	logger.Debug("Enqueue")
	if err := c.Enqueue(coordinator); err != nil {
		return fmt.Errorf("couldn't enqueue curation on coordinator %q: %w", coordinator.Address().String(), err)
	}
	logger.Debug("Play")
	if err := coordinator.Play(); err != nil {
		return fmt.Errorf("couldn't play on coordinator %q: %w", coordinator.Address().String(), err)
	}
	logger.Debug("Joins")
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