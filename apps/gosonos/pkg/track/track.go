package track

type TrackID string
type URI string

type Track interface {
	TrackID() TrackID
	URI() URI
}
