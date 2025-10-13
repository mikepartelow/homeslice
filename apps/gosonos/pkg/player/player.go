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
	AddShareLink(string) error
	AddTracks([]track.Track) error
	Channel() (string, error)
	ClearQueue() error
	GetLogger() *slog.Logger
	IsPlaying() (bool, error)
	Join(Player) error
	Pause() error
	Play() error
	PlayURI(track.URI, string) error
	Queue() ([]track.Track, error)
	Seek(uint) error
	SetVolume(volume Volume) error
	UID() string
	Unjoin() error
}
