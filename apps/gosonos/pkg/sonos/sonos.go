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

	addUriToQueueXmlTemplate     *template.Template
	joinXmlTemplate              *template.Template
	playURIXmlTemplate           *template.Template
	queueXmlTemplate             *template.Template
	seekXmlTemplate              *template.Template
	setAVTransportURIXmlTemplate *template.Template
	setVolumeXmlTemplate         *template.Template

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

func (p *Player) AddShareLink(shareLink string) error {
	p.init()

	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#AddURIToQueue"

	logger := p.Logger.With("method", "AddShareLink", "player", p.Address().String(), "share link", shareLink)
	logger.Info("", "endpoint", endpoint)

	// Given: https://music.apple.com/us/playlist/lost-due-to-incompetence/pl.u-38oWX9ECvqDrDL
	// Want: pl.u-38oWX9ECvqDrDL
	parts := strings.Split(shareLink, "/")
	shareLinkID := parts[len(parts)-1]

	var addUriToQueueXml bytes.Buffer
	err := p.addUriToQueueXmlTemplate.Execute(&addUriToQueueXml, struct {
		ShareLinkID string
	}{
		ShareLinkID: shareLinkID,
	})
	if err != nil {
		return fmt.Errorf("error executing addUriToQueue XML template: %w", err)
	}

	return p.post(endpoint, action, addUriToQueueXml.String(), func(r io.Reader) error {
		return nil
	})
}

//	if zone.get_current_media_info()["channel"] != self.title:
//
// IsPlaying operation has no variables, and so is not a template
//
//go:embed requests/get_current_media_info.xml
var getCurrentMediaInfoXml string

func (p *Player) Channel() (string, error) {
	p.init()

	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#GetMediaInfo"

	logger := p.Logger.With("method", "Channel", "player", p.Address().String())
	logger.Info("", "endpoint", endpoint)

	// dc:title&gt;SomaFM Groove Salad (Powered by Kubernetes)&lt;/dc:title

	var channel string
	err := p.post(endpoint, action, getCurrentMediaInfoXml, func(r io.Reader) error {
		body, err := io.ReadAll(r)
		if err != nil {
			return err
		}

		matches := regexp.MustCompile("dc:title&gt;(.*?)&lt;/dc:title").FindSubmatch(body)
		if len(matches) != 2 {
			return fmt.Errorf("unable to determine channel for %s", p.Address().String())
		}

		channel = string(matches[1])

		return nil
	})

	return channel, err
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

// IsPlaying operation has no variables, and so is not a template
//
//go:embed requests/get_current_transport_info.xml
var getCurrentTransportInfoXml string

func (p *Player) IsPlaying() (bool, error) {
	p.init()

	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#GetTransportInfo"

	logger := p.Logger.With("method", "IsPlaying", "player", p.Address().String())
	logger.Info("", "endpoint", endpoint)

	var isPlaying bool

	err := p.post(endpoint, action, getCurrentTransportInfoXml, func(r io.Reader) error {
		body, err := io.ReadAll(r)
		if err != nil {
			return err
		}
		isPlaying = strings.Contains(string(body), "PLAYING")
		return nil
	})

	return isPlaying, err
}

// Pause operation has no variables, and so is not a template
//
//go:embed requests/pause.xml
var pauseXml string

func (p *Player) Pause() error {
	p.init()

	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#Pause"

	logger := p.Logger.With("method", "Pause", "player", p.Address().String())
	logger.Info("", "endpoint", endpoint)

	return p.post(endpoint, action, pauseXml, nil)
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

func (p *Player) PlayURI(uri track.URI, title string) error {
	p.init()

	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"

	logger := p.Logger.With("method", "PlayURI", "player", p.Address().String(), "uri", uri)
	logger.Info("", "endpoint", endpoint)

	var playURIXml bytes.Buffer
	err := p.playURIXmlTemplate.Execute(&playURIXml, struct {
		Title string
		URI   string
	}{
		Title: title,
		URI:   strings.Replace(string(uri), "https://", "x-rincon-mp3radio://", 1),
	})
	if err != nil {
		return fmt.Errorf("error executing playURI XML template: %w", err)
	}

	return p.post(endpoint, action, playURIXml.String(), func(r io.Reader) error {
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
			tracks = append(tracks, makeTrack(&item))
		}
	}

	return tracks, nil
}

// Shuffle operation has no variables, and so is not a template
//
//go:embed requests/shuffle.xml
var shuffleXml string

func (p *Player) Shuffle() error {
	p.init()

	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#SetPlayMode"

	logger := p.Logger.With("method", "Play", "player", p.Address().String())
	logger.Info("", "endpoint", endpoint)

	return p.post(endpoint, action, shuffleXml, nil)
}

func makeTrack(item *soap.Item) track.Track {
	// Apple Music:
	//   - x-sonos-http:librarytrack%3ai.3VBNbzOUpK5q5x.mp4?sid=204&flags=8232&sn=421
	//   - x-sonos-http:song%3a310111228.mp4?sid=204&flags=8232&sn=421
	//
	// sid is service id and could be used to identify the track kind.

	uri := item.Res.Value

	var t track.Track

	if strings.HasPrefix(uri, "x-sonos-http:librarytrack%3a") || strings.HasPrefix(uri, "x-sonos-http:song%3a") {
		// Apple Music
		id := track.MakeID(item.Album, item.Creator, item.Title)
		t = &playlist.AppleMusicTrack{ID: track.TrackID((id))}
	} else {
		panic(fmt.Sprintf("unhandled music service: %q", uri))
	}

	return t
}

func (p *Player) Seek(position uint) error {
	p.init()

	if err := p.setAVTransportURI(); err != nil {
		return err
	}

	position = position + 1

	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#Seek"

	logger := p.Logger.With("method", "Seek", "player", p.Address().String(), "position", position)
	logger.Info("", "endpoint", endpoint)

	var seekXml bytes.Buffer
	err := p.seekXmlTemplate.Execute(&seekXml, struct {
		Target uint
	}{
		Target: position,
	})
	if err != nil {
		return fmt.Errorf("error executing seek XML template: %w", err)
	}

	return p.post(endpoint, action, seekXml.String(), func(r io.Reader) error {
		return nil
	})
}

func (p *Player) setAVTransportURI() error {
	p.init()
	endpoint := "MediaRenderer/AVTransport/Control"
	action := "urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"

	logger := p.Logger.With("method", "SetAVTransportURI", "player", p.Address().String())
	logger.Info("", "endpoint", endpoint)

	var setAVTransportURIXML bytes.Buffer
	err := p.setAVTransportURIXmlTemplate.Execute(&setAVTransportURIXML, struct {
		Rincon string
	}{
		Rincon: p.UID(),
	})
	if err != nil {
		return fmt.Errorf("error executing setAVTransportURI XML template: %w", err)
	}

	return p.post(endpoint, action, setAVTransportURIXML.String(), func(r io.Reader) error {
		return nil
	})
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
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("HTTP error %d: %s", resp.StatusCode, resp.Status)
	}

	if callback != nil {
		return callback(resp.Body)
	}
	return nil
}

//go:embed requests/add_uri_to_queue.xml.tmpl
var addUriToQueueXmlTemplate string

//go:embed requests/join.xml.tmpl
var joinXmlTemplate string

//go:embed requests/play_uri.xml.tmpl
var playURIXmlTemplate string

//go:embed requests/queue.xml.tmpl
var queueXmlTemplate string

//go:embed requests/seek.xml.tmpl
var seekXmlTemplate string

//go:embed requests/set_av_transport_uri.xml.tmpl
var setAVTransportURIXmlTemplate string

//go:embed requests/set_volume.xml.tmpl
var setVolumeXmlTemplate string

func (p *Player) init() {
	if p.Logger == nil {
		p.Logger = slog.New(
			console.NewHandler(os.Stderr, &console.HandlerOptions{Level: slog.LevelError}),
		)
	}
	if p.addUriToQueueXmlTemplate == nil {
		p.addUriToQueueXmlTemplate = mustParseTemplate("addUriToQueueXml", addUriToQueueXmlTemplate)
	}
	if p.joinXmlTemplate == nil {
		p.joinXmlTemplate = mustParseTemplate("joinXml", joinXmlTemplate)
	}
	if p.playURIXmlTemplate == nil {
		p.playURIXmlTemplate = mustParseTemplate("playURI", playURIXmlTemplate)
	}
	if p.queueXmlTemplate == nil {
		p.queueXmlTemplate = mustParseTemplate("queueXml", queueXmlTemplate)
	}
	if p.seekXmlTemplate == nil {
		p.seekXmlTemplate = mustParseTemplate("seekXml", seekXmlTemplate)
	}
	if p.setAVTransportURIXmlTemplate == nil {
		p.setAVTransportURIXmlTemplate = mustParseTemplate("setAVTransportURIXML", setAVTransportURIXmlTemplate)
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
		defer func() { _ = resp.Body.Close() }()
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
