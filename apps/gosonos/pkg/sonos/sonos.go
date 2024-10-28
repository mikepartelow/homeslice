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
	"time"

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
	setVolumeXmlTemplate        *template.Template

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

func (p *Player) GetLogger() *slog.Logger {
	return p.Logger
}

func (p *Player) AddTracks(tracks []track.Track) error {
	p.init()

	// implementation detail: the maximum number of tracks we can send in a single SOAP call.
	// more than this and Sonos returns HTTP 500. experimentally determined to be 16.
	const AddTracksMax = 8

	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#AddMultipleURIsToQueue"

	logger := p.Logger.With("method", "AddTracks", "player", p.Address().String())
	logger.Info("", "endpoint", endpoint)

	var uris, didls string
	var count int

	for i, t := range tracks {
		tid := t.TrackID()
		uris = uris + string(t.URI()) + " " // the " " is required!

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
		count++

		if (count > 0 && count == AddTracksMax) || i == len(tracks)-1 {
			didls = strings.TrimSpace(didls)

			var addTracksXML bytes.Buffer
			err := p.addTracksXmlTemplate.Execute(&addTracksXML, struct {
				Count    int
				URIs     string
				Metadata string
			}{
				Count:    count,
				URIs:     uris,
				Metadata: didls,
			})
			if err != nil {
				return fmt.Errorf("error executing addTracks XML template: %w", err)
			}

			logger.Debug("posting", "count", count, "len(uris)", strings.Count(uris, " "))

			for retry := 0; retry < 3; retry++ {
				logger.Debug("retry", "try", retry)
				err = p.post(endpoint, action, addTracksXML.String(), func(r io.Reader) error {
					return nil
				})
				if err == nil {
					break
				}
				time.Sleep(time.Millisecond * time.Duration(10*(retry+1)))
			}
			if err != nil {
				return err
			}

			didls, uris = "", ""
			count = 0
		}
	}
	logger.Debug("bye")
	return nil
}

// ClearQueue operation has no variables, and so is not a template
//
//go:embed requests/clear_queue.xml
var clearQueueXml string

func (p *Player) ClearQueue() error {
	p.init()

	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#RemoveAllTracksFromQueue"

	logger := p.Logger.With("method", "ClearQueue", "player", p.Address().String())
	logger.Info("", "endpoint", endpoint)

	return p.post(endpoint, action, clearQueueXml, nil)
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

	return p.post(endpoint, action, joinXML.String(), func(r io.Reader) error {
		return nil
	})
}

func (p *Player) Pause() error {
	p.init()
	panic("NIY")
}

// Play operation has no variables, and so is not a template
//
//go:embed requests/play.xml
var playXml string

func (p *Player) Play() error {
	p.init()

	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#Play"

	logger := p.Logger.With("method", "Play", "player", p.Address().String())
	logger.Info("", "endpoint", endpoint)

	return p.post(endpoint, action, playXml, nil)
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

func (p *Player) SetVolume(volume player.Volume) error {
	p.init()
	endpoint := "MediaRenderer/RenderingControl/Control"
	action := "urn:schemas-upnp-org:service:RenderingControl:1#SetVolume"

	logger := p.Logger.With("method", "SetVolume", "player", p.Address().String(), "volume", volume)
	logger.Info("", "endpoint", endpoint)

	var setVolumeXML bytes.Buffer
	err := p.setVolumeXmlTemplate.Execute(&setVolumeXML, struct {
		Volume int
	}{
		Volume: int(volume),
	})
	if err != nil {
		return fmt.Errorf("error executing setVolume XML template: %w", err)
	}

	return p.post(endpoint, action, setVolumeXML.String(), func(r io.Reader) error {
		return nil
	})
}

// Ungroup operation has no variables, and so is not a template
//
//go:embed requests/unjoin.xml
var unjoinXml string

func (p *Player) Unjoin() error {
	p.init()

	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#BecomeCoordinatorOfStandaloneGroup"

	logger := p.Logger.With("method", "Unjoin", "player", p.Address().String())
	logger.Info("", "endpoint", endpoint)

	return p.post(endpoint, action, unjoinXml, nil)
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

	if callback != nil {
		return callback(resp.Body)
	}
	return nil
}

//go:embed requests/add_track_didl_lite.xml.tmpl
var addTrackDidlLiteXmlTemplate string

//go:embed requests/add_tracks.xml.tmpl
var addTracksXmlTemplate string

//go:embed requests/join.xml.tmpl
var joinXmlTemplate string

//go:embed requests/queue.xml.tmpl
var queueXmlTemplate string

//go:embed requests/set_volume.xml.tmpl
var setVolumeXmlTemplate string

func (p *Player) init() {
	if p.Logger == nil {
		p.Logger = slog.New(
			console.NewHandler(os.Stderr, &console.HandlerOptions{Level: slog.LevelError}),
		)
	}
	if p.addTrackDidlLiteXmlTemplate == nil {
		p.addTrackDidlLiteXmlTemplate = mustParseTemplate("addTrackDidlLiteXml", addTrackDidlLiteXmlTemplate)
	}
	if p.addTracksXmlTemplate == nil {
		p.addTracksXmlTemplate = mustParseTemplate("addTracksXml", addTracksXmlTemplate)
	}
	if p.joinXmlTemplate == nil {
		p.joinXmlTemplate = mustParseTemplate("joinXml", joinXmlTemplate)
	}
	if p.queueXmlTemplate == nil {
		p.queueXmlTemplate = mustParseTemplate("queueXml", queueXmlTemplate)
	}
	if p.setVolumeXmlTemplate == nil {
		p.setVolumeXmlTemplate = mustParseTemplate("setVolumeXML", setVolumeXmlTemplate)
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

		matches := regexp.MustCompile("<UDN>uuid:(.*?)</UDN>").FindSubmatch(body)
		if len(matches) < 1 {
			panic(fmt.Errorf("unable to determine device id for %s", p.Address().String()))
		}

		p.uid = string(matches[1])
	}
}

func New(ip string, logger *slog.Logger) (*Player, error) {
	a, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("%s:%d", ip, PlayerPort))
	if err != nil {
		return nil, fmt.Errorf("couldn't resolve coordinator IP address %q: %w", ip, err)
	}
	return &Player{Addr: a, Logger: logger}, nil
}

func mustParseTemplate(name, text string) *template.Template {
	t, err := template.New(name).Parse(text)
	if err != nil {
		panic(fmt.Errorf("error parsing %s XML template: %w", name, err))
	}
	return t
}
