package gosonos

import (
	_ "embed"
	"fmt"
	"io"
	"log/slog"
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

//go:embed requests/queue.xml
var queueXml string

// FIXME: iterator
func (p *Player) Queue() error {
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
	fmt.Println(string(body))

	return nil
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
