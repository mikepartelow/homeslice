package playlist

import (
	"encoding/json"
	"fmt"
	"io"
	"mp/gosonos/pkg/track"
	"net/http"
	"regexp"
	"time"
)

// NOTE: a lot of this was LLM generated.

func fetch(u string) ([]byte, error) {
	req, err := http.NewRequest("GET", u, nil)
	if err != nil {
		return nil, fmt.Errorf("error creating HTTP Request: %w", err)
	}

	c := &http.Client{Timeout: 8 * time.Second}
	resp, err := c.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error doing HTTP Request: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP error %d: %s", resp.StatusCode, resp.Status)
	}

	return io.ReadAll(resp.Body)
}

type docRoot struct {
	Data struct {
		Sections []section `json:"sections"`
	} `json:"data"`
}

type section struct {
	ItemKind string   `json:"itemKind"` // we want "trackLockup"
	Items    []tEntry `json:"items"`
}

type tEntry struct {
	Title         string `json:"title"` // Title
	SubtitleLinks []struct {
		Title string `json:"title"` // Artist
	} `json:"subtitleLinks"`
	TertiaryLinks []struct {
		Title string `json:"title"` // Album
	} `json:"tertiaryLinks"`
}

var serDataRe = regexp.MustCompile(`(?is)<script[^>]+id=["']serialized-server-data["'][^>]*>(.*?)</script>`)

func parsePlaylistHTML(html []byte) ([]track.Track, error) {
	m := serDataRe.FindSubmatch(html)
	if m == nil {
		return nil, fmt.Errorf("serialized-server-data script not found")
	}
	raw := m[1]

	var pages []docRoot
	if err := json.Unmarshal(raw, &pages); err != nil {
		return nil, fmt.Errorf("unmarshal serialized-server-data: %w", err)
	}

	var tracks []track.Track
	for _, p := range pages {
		for _, s := range p.Data.Sections {
			if s.ItemKind != "trackLockup" {
				continue
			}
			for _, it := range s.Items {
				title := it.Title
				artist := ""
				album := ""
				if len(it.SubtitleLinks) > 0 {
					artist = it.SubtitleLinks[0].Title
				}
				if len(it.TertiaryLinks) > 0 {
					album = it.TertiaryLinks[0].Title
				}
				if title != "" || artist != "" || album != "" {
					id := track.MakeID(album, artist, title)
					tracks = append(tracks, &AppleMusicTrack{ID: track.TrackID((id))})
				}
			}
		}
	}
	return tracks, nil
}

func fetchShareLinkTracks(shareLink string) ([]track.Track, error) {
	html, err := fetch(shareLink)
	if err != nil {
		return nil, fmt.Errorf("error fetching tracks from sharelink %q: %w", shareLink, err)
	}

	return parsePlaylistHTML(html)
}
