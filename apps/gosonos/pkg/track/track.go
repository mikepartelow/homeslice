package track

import "fmt"

type TrackID string
type URI string

type Track interface {
	TrackID() TrackID
	URI() URI
}

func MakeID(album, artist, title string) string {
	return fmt.Sprintf("%s|%s|%s", album, artist, title)
}
