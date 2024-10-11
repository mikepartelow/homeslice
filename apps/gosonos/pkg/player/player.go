package player

import (
	"log/slog"
	"mp/gosonos/pkg/track"
	"net"
)

type Volume int

type Player interface {
	Address() net.Addr
	AddTracks([]track.Track) error
	ClearQueue() error
	Join(Player) error
	Logger() *slog.Logger
	Play() error
	Queue() ([]track.Track, error)
	SetVolume(volume Volume) error
	UID() string
	Ungroup() error
}
