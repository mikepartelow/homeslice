package playlist

import (
	"cmp"
	"fmt"
	"math/rand"
	"mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/player"
	"mp/gosonos/pkg/track"
	"mp/gosonos/pkg/ttlt"
	"regexp"
	"slices"
	"time"
)

type TidalTrack struct {
	ID track.TrackID
}

var _ track.Track = &TidalTrack{}

func (t *TidalTrack) TrackID() track.TrackID {
	return t.ID
}

func (t *TidalTrack) URI() track.URI {
	// x-sonos-http:track%2f16334233.flac?sid=174&amp;flags=24616&amp;sn=34
	return track.URI("x-sonos-http:track%2f" + string(t.ID) + ".flac?sid=174&amp;flags=24616&amp;sn=34")
}

const (
	DefaultMaxPlayingTracks = 42
	IsPlayingOnCacheTTL     = time.Duration(1 * time.Minute)
)

type Playlist struct {
	ID               curation.ID
	Name             string
	MaxPlayingTracks int
	Tracks           []track.Track
	Volume           player.Volume

	playingTracks []track.Track
	isPlayingOn   *ttlt.TTLT[bool]
}

var _ curation.Curation = &Playlist{}

// Enqueue enqueues a shuffled subset of maximum length Playlist.MaxPlayingTracks to player.
func (p *Playlist) Enqueue(player player.Player) error {
	rand.Shuffle(len(p.Tracks), func(i, j int) {
		p.Tracks[i], p.Tracks[j] = p.Tracks[j], p.Tracks[i]
	})

	p.playingTracks = p.Tracks[0:p.MaxPlayingTracks]

	if err := player.AddTracks(p.playingTracks); err != nil {
		return fmt.Errorf("error adding tracks from playlist %q to player %q: %w", p.Name, player.Address().String(), err)
	}
	return nil
}

func (p *Playlist) Do(op curation.Op, coordiator player.Player, players []player.Player) error {
	return curation.Do(op, p, coordiator, players)
}

func (p *Playlist) GetID() curation.ID {
	return p.ID
}

func (p *Playlist) GetName() string {
	return p.Name
}

func (p *Playlist) GetVolume() player.Volume {
	return p.Volume
}

func (p *Playlist) IsPlayingOn(player player.Player) (bool, error) {
	if is, ok := p.isPlayingOn.GetValue(); ok {
		return is, nil
	}
	queueTracks, err := player.Queue()
	if err != nil {
		// don't set p.isPlayingOn because we didn't answer the question one way or the other
		return false, fmt.Errorf("error fetching queue from player %q: %w", player.Address().String(), err)
	}

	if len(queueTracks) != len(p.playingTracks) {
		return p.isPlayingOn.SetValue(false), nil
	}

	slices.SortFunc(queueTracks, func(a, b track.Track) int {
		return cmp.Compare(a.TrackID(), b.TrackID())
	})
	slices.SortFunc(p.playingTracks, func(a, b track.Track) int {
		return cmp.Compare(a.TrackID(), b.TrackID())
	})

	for i, t := range queueTracks {
		if p.playingTracks[i].TrackID() != t.TrackID() {
			return p.isPlayingOn.SetValue(false), nil
		}
	}

	return p.isPlayingOn.SetValue(true), nil
}

func New(id curation.ID, name string, tracks []track.Track, volume player.Volume) (*Playlist, error) {
	if len(tracks) == 0 {
		return nil, fmt.Errorf("no tracks")
	}

	if !regexp.MustCompile(`^[\w-]+$`).MatchString(string(id)) {
		return nil, fmt.Errorf("invalid id %q", id)
	}

	p := Playlist{
		ID:     id,
		Name:   name,
		Tracks: tracks,
		Volume: volume,
	}
	p.init()

	return &p, nil
}

func (p *Playlist) init() {
	if p.MaxPlayingTracks == 0 {
		p.MaxPlayingTracks = DefaultMaxPlayingTracks
	}
	if p.isPlayingOn == nil {
		p.isPlayingOn = ttlt.New[bool](IsPlayingOnCacheTTL)
	}
}
