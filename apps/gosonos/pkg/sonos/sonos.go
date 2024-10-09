package sonos

import (
	"bytes"
	_ "embed"
	"fmt"
	"io"
	"log/slog"
	"mp/gosonos/pkg/player"
	"mp/gosonos/pkg/playlist"
	"mp/gosonos/pkg/soap"
	"mp/gosonos/pkg/track"
	"net"
	"net/http"
	"os"
	"regexp"
	"strings"
	"text/template"

	"github.com/phsym/console-slog"
)

const (
	PlayerPort = 1400
)

type Player struct {
	Addr   net.Addr
	Logger *slog.Logger

	addTracksXmlTemplate        *template.Template
	addTrackDidlLiteXmlTemplate *template.Template
	joinXmlTemplate             *template.Template
	queueXmlTemplate            *template.Template

	uid string
}

var _ player.Player = &Player{}

func (p *Player) Address() net.Addr {
	return p.Addr
}

func (p *Player) UID() string {
	p.init()
	return p.uid
}

func (p *Player) AddTracks(tracks []track.Track) error {
	p.init()

	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#AddMultipleURIsToQueue"

	logger := p.Logger.With("method", "AddTracks", "player", p.Address().String())
	logger.Info("", "endpoint", endpoint)

	var uris string
	var didls string

	for _, t := range tracks {
		tid := t.TrackID()
		uris = uris + string(t.URI())

		// in this template, whitespace is extremely significant. make sure there isn't any!
		var addTrackDidlLiteXML bytes.Buffer
		err := p.addTrackDidlLiteXmlTemplate.Execute(&addTrackDidlLiteXML, struct {
			TrackId string
		}{
			TrackId: string(tid),
		})
		if err != nil {
			return fmt.Errorf("error executing addTracks XML template: %w", err)
		}

		didls += addTrackDidlLiteXML.String()
	}

	didls = strings.TrimSpace(didls)

	var addTracksXML bytes.Buffer
	err := p.addTracksXmlTemplate.Execute(&addTracksXML, struct {
		Count    int
		URIs     string
		Metadata string
	}{
		Count:    len(tracks),
		URIs:     uris,
		Metadata: didls,
	})
	if err != nil {
		return fmt.Errorf("error executing addTracks XML template: %w", err)
	}

	return p.post(endpoint, action, addTracksXML.String(), func(r io.Reader) error {
		return nil
	})
}

func (p *Player) ClearQueue() error {
	panic("NIY")
}

func (p *Player) Join(other player.Player) error {
	p.init()
	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"

	// This is how soco.py does it, but it is not how the Sonos desktop app does it.
	// The Sonos desktop app's method is not obvious in Wireshark and does not appear to involve SOAP/POST.
	// Instead, there may be an encrypted persistent channel over which the grouping command is sent.

	logger := p.Logger.With("method", "Join", "player", p.Address().String(), "other", other.Address().String())
	logger.Info("", "endpoint", endpoint)

	var joinXML bytes.Buffer
	err := p.joinXmlTemplate.Execute(&joinXML, struct {
		Uid string
	}{
		Uid: other.UID(),
	})
	if err != nil {
		return fmt.Errorf("error executing join XML template: %w", err)
	}

	fmt.Println(joinXML.String())

	return p.post(endpoint, action, joinXML.String(), func(r io.Reader) error {
		return nil
	})
}

// FIXME: iterator: have this return (error, func() Iter) so that we can stop panicking on error
// FIXME: queue.xml expects pagination, so paginate. test with large queue.
func (p *Player) Queue() ([]track.Track, error) {
	p.init()

	endpoint := "MediaServer/ContentDirectory/Control"
	action := "urn:schemas-upnp-org:service:ContentDirectory:1#Browse"

	logger := p.Logger.With("method", "Queue", "player", p.Address().String())
	logger.Info("", "endpoint", endpoint)

	var tracks []track.Track
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
			track := playlist.TidalTrack{
				ID: track.TrackID(id),
			}
			tracks = append(tracks, &track)
		}
	}

	return tracks, nil
}

func (p *Player) Play() error {
	panic("what")
}

func (p *Player) SetVolume(volume int) error {
	panic("what")
}

func (p *Player) post(endpoint, action, body string, callback func(io.Reader) error) error {
	endpoint = fmt.Sprintf("http://%s/%s", p.Address().String(), endpoint)
	logger := p.Logger.With("method", "post", "player", p.Address().String())
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

//go:embed requests/add_track_didl_lite.xml.tmpl
var addTrackDidlLiteXmlTemplate string

//go:embed requests/add_tracks.xml.tmpl
var addTracksXmlTemplate string

//go:embed requests/join.xml.tmpl
var joinXmlTemplate string

//go:embed requests/queue.xml.tmpl
var queueXmlTemplate string

func (p *Player) init() {
	if p.Logger == nil {
		p.Logger = slog.New(
			console.NewHandler(os.Stderr, &console.HandlerOptions{Level: slog.LevelInfo}),
		)
	}
	if p.addTrackDidlLiteXmlTemplate == nil {
		t, err := template.New("addTrackDidlLiteXML").Parse(addTrackDidlLiteXmlTemplate)
		if err != nil {
			panic(fmt.Errorf("error parsing addTrackDidlLite XML template: %w", err))
		}
		p.addTrackDidlLiteXmlTemplate = t
	}
	if p.addTracksXmlTemplate == nil {
		t, err := template.New("addTracksXML").Parse(addTracksXmlTemplate)
		if err != nil {
			panic(fmt.Errorf("error parsing addTracks XML template: %w", err))
		}
		p.addTracksXmlTemplate = t
	}
	if p.joinXmlTemplate == nil {
		t, err := template.New("joinXML").Parse(joinXmlTemplate)
		if err != nil {
			panic(fmt.Errorf("error parsing join XML template: %w", err))
		}
		p.joinXmlTemplate = t
	}
	if p.queueXmlTemplate == nil {
		t, err := template.New("queueXML").Parse(queueXmlTemplate)
		if err != nil {
			panic(fmt.Errorf("error parsing queue XML template: %w", err))
		}
		p.queueXmlTemplate = t
	}

	if p.uid == "" {
		endpoint := fmt.Sprintf("http://%s/xml/device_description.xml", p.Address().String())
		resp, err := http.Get(endpoint)
		if err != nil {
			panic(fmt.Errorf("error fetching device info for %s: %w", p.Address().String(), err))
		}
		defer resp.Body.Close()
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			panic(fmt.Errorf("error fetching device info for %s: %w", p.Address().String(), err))
		}

		r, err := regexp.Compile("<UDN>uuid:(.*?)</UDN>")
		if err != nil {
			panic(fmt.Errorf("error fetching device info for %s: %w", p.Address().String(), err))
		}
		matches := r.FindSubmatch(body)
		if len(matches) > 1 {
			p.uid = string(matches[1])
		}
	}
}

func check(err error) {
	fmt.Println("FIXME")
	if err != nil {
		panic(err)
	}
}
