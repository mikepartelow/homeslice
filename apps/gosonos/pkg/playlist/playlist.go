package playlist

import (
	"cmp"
	"fmt"
	"mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/player"
	"mp/gosonos/pkg/track"
	"slices"
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

type Playlist struct {
	ID     curation.ID
	Name   string
	Tracks []track.Track
	Volume player.Volume
}

var _ curation.Curation = &Playlist{}

func (p *Playlist) Enqueue(player player.Player) error {
	if err := player.AddTracks(p.Tracks); err != nil {
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
	tracks, err := player.Queue()
	if err != nil {
		return false, fmt.Errorf("error adding tracks from playlist %q to player %q: %w", p.Name, player.Address().String(), err)
	}

	if len(tracks) != len(p.Tracks) {
		return false, nil
	}

	slices.SortFunc(tracks, func(a, b track.Track) int {
		return cmp.Compare(a.TrackID(), b.TrackID())
	})
	slices.SortFunc(p.Tracks, func(a, b track.Track) int {
		return cmp.Compare(a.TrackID(), b.TrackID())
	})

	for i, t := range tracks {
		if p.Tracks[i].TrackID() != t.TrackID() {
			return false, nil
		}
	}

	return true, nil
}
