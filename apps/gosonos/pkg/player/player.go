package player

import (
	"log/slog"
	"mp/gosonos/pkg/track"
	"net"
)

type Volume int

const (
	DefaultVolume = 0
)

type Player interface {
	Address() net.Addr
	AddTracks([]track.Track) error
	ClearQueue() error
	GetLogger() *slog.Logger
	IsPlaying() (bool, error)
	Join(Player) error
	Pause() error
	Play() error
	Queue() ([]track.Track, error)
	SetVolume(volume Volume) error
	UID() string
	Unjoin() error
}
