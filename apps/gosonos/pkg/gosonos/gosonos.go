package gosonos

import (
	_ "embed"
	"fmt"
	"io"
	"log/slog"
	"mp/gosonos/pkg/soap"
	"net"
	"net/http"
	"strings"
)

const (
	PlayerPort = 1400
)

type Player struct {
	Address net.Addr
	Logger  *slog.Logger
}

type TidalTrack struct {
	Id string
}

type Track struct {
	URI string
	*TidalTrack
}

func (t *Track) Id() string {
	if t.TidalTrack == nil {
		panic("NIH")
	}
	return t.TidalTrack.Id
}

//go:embed requests/queue.xml
var queueXml string

// FIXME: iterator: have this return (error, func() Iter) so that we can stop panicking on error
// FIXME: queue.xml expects pagination, so paginate. test with large queue.
func (p *Player) Queue() ([]Track, error) {
	p.init()

	endpoint := fmt.Sprintf("http://%s/MediaServer/ContentDirectory/Control", p.Address.String())
	logger := p.Logger.With("method", "Queue")
	logger.Info("", "endpoint", endpoint)

	req, err := http.NewRequest("POST", endpoint, strings.NewReader(queueXml))
	check(err)

	req.Header.Add("Content-Type", `text/xml; charset="utf-8"`)
	req.Header.Add("SOAPACTION", "urn:schemas-upnp-org:service:ContentDirectory:1#Browse")

	client := &http.Client{}
	resp, err := client.Do(req)
	check(err)

	fmt.Println(resp.Status)
	body, err := io.ReadAll(resp.Body)
	check(err)

	dl := soap.DidlLite{}
	err = dl.Unmarshal(body)
	check(err)

	tracks := make([]Track, len(dl.Items))
	for i, item := range dl.Items {
		// x-sonos-http:track%2f2619614.flac?sid=174&flags=8232&sn=34
		// FIXME: some if statement to determine this is actually a tidal track
		uri := item.Res.Value
		id := strings.Split(strings.Split(uri, "%2f")[1], ".")[0]
		tracks[i] = Track{
			TidalTrack: &TidalTrack{
				Id: id,
			},
			URI: uri,
		}
	}

	return tracks, nil
}

func (p *Player) init() {
	if p.Logger == nil {
		p.Logger = slog.Default() // FIXME: use the fancy console/structured logging thing
	}
}

func check(err error) {
	fmt.Println("FIXME")
	if err != nil {
		panic(err)
	}
}
