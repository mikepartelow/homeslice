package player

import (
	"mp/gosonos/pkg/track"
	"net"
)

type Player interface {
	Address() net.Addr
	AddTracks([]track.Track) error
	ClearQueue() error
	Play() error
	SetVolume(volume int) error
	Queue() ([]track.Track, error)
	UID() string
}
