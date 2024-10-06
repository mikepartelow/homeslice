package gosonos

import (
	"bytes"
	_ "embed"
	"fmt"
	"io"
	"log/slog"
	"mp/gosonos/pkg/soap"
	"net"
	"net/http"
	"os"
	"strings"
	"text/template"

	"github.com/phsym/console-slog"
)

const (
	PlayerPort = 1400
)

type Player struct {
	Address net.Addr
	Logger  *slog.Logger

	queueXmlTemplate *template.Template
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

//go:embed requests/queue.xml.tmpl
var queueXmlTemplate string

// FIXME: iterator: have this return (error, func() Iter) so that we can stop panicking on error
// FIXME: queue.xml expects pagination, so paginate. test with large queue.
func (p *Player) Queue() ([]Track, error) {
	p.init()

	endpoint := "MediaServer/ContentDirectory/Control"
	action := "urn:schemas-upnp-org:service:ContentDirectory:1#Browse"

	logger := p.Logger.With("method", "Queue")
	logger.Info("", "endpoint", endpoint)

	var tracks []Track
	const pageSize = 100
	for page := 0; ; page += pageSize {
		var queueXML bytes.Buffer
		err := p.queueXmlTemplate.Execute(&queueXML, struct {
			Page     int
			PageSize int
		}{
			Page:     page,
			PageSize: pageSize,
		})
		if err != nil {
			return nil, fmt.Errorf("error executing queue XML template: %w", err)
		}

		var dl soap.DidlLite
		err = p.post(endpoint, action, queueXML.String(), func(r io.Reader) error {
			return dl.Decode(r)
		})
		if err != nil {
			return nil, fmt.Errorf("error decoding Sonos response: %w", err)
		}

		if len(dl.Items) == 0 {
			break
		}

		for _, item := range dl.Items {
			// x-sonos-http:track%2f2619614.flac?sid=174&flags=8232&sn=34
			// FIXME: some if statement to determine this is actually a tidal track
			uri := item.Res.Value
			id := strings.Split(strings.Split(uri, "%2f")[1], ".")[0]
			track := Track{
				TidalTrack: &TidalTrack{
					Id: id,
				},
				URI: uri,
			}
			tracks = append(tracks, track)
		}
	}

	return tracks, nil
}

func (p *Player) post(endpoint, action, body string, callback func(io.Reader) error) error {
	endpoint = fmt.Sprintf("http://%s/%s", p.Address.String(), endpoint)
	logger := p.Logger.With("method", "post")
	logger.Debug("", "endpoint", endpoint)

	req, err := http.NewRequest("POST", endpoint, strings.NewReader(body))
	if err != nil {
		return fmt.Errorf("error creating HTTP Request: %w", err)
	}

	req.Header.Add("Content-Type", `text/xml; charset="utf-8"`)
	req.Header.Add("SOAPACTION", action)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("error doing HTTP Request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("HTTP error %d: %s", resp.StatusCode, resp.Status)
	}

	return callback(resp.Body)
}

func (p *Player) init() {
	if p.Logger == nil {
		p.Logger = slog.New(
			console.NewHandler(os.Stderr, &console.HandlerOptions{Level: slog.LevelInfo}),
		)
	}
	if p.queueXmlTemplate == nil {
		t, err := template.New("queueXML").Parse(queueXmlTemplate)
		if err != nil {
			panic(fmt.Errorf("error parsing queue XML template: %w", err))
		}
		p.queueXmlTemplate = t
	}
}

func check(err error) {
	fmt.Println("FIXME")
	if err != nil {
		panic(err)
	}
}
