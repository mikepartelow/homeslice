package playlist

import (
	"cmp"
	"fmt"
	"log/slog"
	"math/rand"
	"mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/player"
	"mp/gosonos/pkg/track"
	"mp/gosonos/pkg/ttlt"
	"os"
	"slices"
	"time"

	"github.com/phsym/console-slog"
)

type AppleMusicTrack struct {
	ID track.TrackID
}

type TidalTrack struct {
	ID track.TrackID
}

var _ track.Track = &AppleMusicTrack{}
var _ track.Track = &TidalTrack{}

func (t *AppleMusicTrack) TrackID() track.TrackID {
	return t.ID
}

func (t *AppleMusicTrack) URI() track.URI {
	// x-sonos-http:librarytrack%3ai.3VBNbzOUpK5q5x.mp4?sid=204&flags=8232&sn=421
	return track.URI("x-sonos-http:librarytrack%3a" + string(t.ID) + ".flac?sid=174&amp;flags=24616&amp;sn=34")
}

func (t *TidalTrack) TrackID() track.TrackID {
	return t.ID
}

func (t *TidalTrack) URI() track.URI {
	// x-sonos-http:track%2f16334233.flac?sid=174&amp;flags=24616&amp;sn=34
	return track.URI("x-sonos-http:track%2f" + string(t.ID) + ".flac?sid=174&amp;flags=24616&amp;sn=34")
}

const (
	DefaultMaxPlayingTracks = 42
	IsPlayingOnCacheTTL     = time.Duration(16 * time.Second)
)

type Playlist struct {
	ID               curation.ID
	Logger           *slog.Logger
	MaxPlayingTracks int
	Kind             curation.Kind
	Name             string
	Tracks           []track.Track
	ShareLink        string
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

	p.playingTracks = p.Tracks[0:min(p.MaxPlayingTracks, len(p.Tracks))]

	if err := player.AddTracks(p.playingTracks); err != nil {
		return fmt.Errorf("error adding tracks from playlist %q to player %q: %w", p.Name, player.Address().String(), err)
	}
	return nil
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
	p.init()

	if len(p.playingTracks) == 0 {
		p.Logger.Debug("no tracks playing (internal)")
		return false, nil
	}

	if is, ok := p.isPlayingOn.GetValue(); ok {
		p.Logger.Debug("p.isPlayingOn", "is", is)
		return is, nil
	}

	queueTracks, err := player.Queue()
	if err != nil {
		// don't set p.isPlayingOn because we didn't answer the question one way or the other
		return false, fmt.Errorf("error fetching queue from player %q: %w", player.Address().String(), err)
	}
	p.Logger.Debug("IsPlayingOn", "len(queueTracks)", len(queueTracks), "len(p.playingTracks)", len(p.playingTracks))

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

	isPlaying, err := player.IsPlaying()
	if err != nil {
		// don't set p.isPlayingOn because we didn't answer the question one way or the other
		return false, fmt.Errorf("error getting IsPlaying status from player %q: %w", player.Address().String(), err)
	}

	return p.isPlayingOn.SetValue(isPlaying), nil
}

func (p *Playlist) Play(player player.Player) error {
	if err := player.Seek(0); err != nil {
		return fmt.Errorf("error seeking to 0 from player %q: %w", player.Address().String(), err)
	}

	if err := player.Play(); err != nil {
		return fmt.Errorf("error playing from player %q: %w", player.Address().String(), err)
	}

	return nil
}

func New(id curation.ID, name string, kind curation.Kind, tracks []track.Track, shareLink string, volume player.Volume, logger *slog.Logger) (*Playlist, error) {
	if len(tracks) == 0 && shareLink == "" {
		return nil, fmt.Errorf("no tracks, no share link")
	}

	p := Playlist{
		ID:        id,
		Kind:      kind,
		Logger:    logger,
		Name:      name,
		Tracks:    tracks,
		ShareLink: shareLink,
		Volume:    volume,
	}
	p.init()

	return &p, nil
}

func (p *Playlist) init() {
	if p.Logger == nil {
		p.Logger = slog.New(
			console.NewHandler(os.Stderr, &console.HandlerOptions{Level: slog.LevelError}),
		)
	}
	if p.MaxPlayingTracks == 0 {
		p.MaxPlayingTracks = DefaultMaxPlayingTracks
	}
	if p.isPlayingOn == nil {
		p.isPlayingOn = ttlt.New[bool](IsPlayingOnCacheTTL)
	}
}
