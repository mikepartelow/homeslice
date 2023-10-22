package wemo

import (
	"bytes"
	_ "embed"
	"fmt"
	"io"
	"log/slog"
	"net"
	"net/http"
	"regexp"
	"strconv"
	"text/template"
)

//go:embed soap.xml
var soapXmlTemplate string

type Wemo struct {
	Id      string
	Name    string
	Address net.IP
	Port    int
	Logger  *slog.Logger

	soapTempl *template.Template
}

type State int
type Operation string

const (
	DefaultPort = 49153
	EventPath   = "/upnp/control/basicevent1"

	None State = -1
	Off  State = 0
	On   State = 1

	Get Operation = "GetBinaryState"
	Set Operation = "SetBinaryState"
)

func (w *Wemo) ID() string { return w.Id }

func (w *Wemo) On() error {
	err := w.setState(On)
	return err
}

func (w *Wemo) Off() error {
	err := w.setState(Off)
	return err
}

func (w *Wemo) Toggle() error {
	state, err := w.getState()
	if err != nil {
		return err
	}

	if state == On {
		return w.Off()
	}

	return w.On()
}

func (w *Wemo) init() error {
	if w.soapTempl == nil {
		var err error
		w.soapTempl, err = template.New("").Parse(soapXmlTemplate)
		if err != nil {
			return fmt.Errorf("error parsing template: %w", err)
		}
	}
	if w.Port == 0 {
		w.Port = DefaultPort
	}

	return nil
}

func (w *Wemo) getState() (State, error) {
	return w.do(Get, None)
}

func (w *Wemo) setState(state State) error {
	_, err := w.do(Set, state)
	return err
}

// Credit: https://github.com/iancmcc/ouimeaux/blob/develop/client.py
func (w *Wemo) do(op Operation, state State) (State, error) {
	logger := w.Logger.With("name", w.Name, "op", op)
	logger.Debug("do")

	if err := w.init(); err != nil {
		return None, nil
	}

	resp, err := w.post(op, state, w.Address.String())
	if err != nil {
		return None, fmt.Errorf("error POSTing op %s: %w", op, err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	logger.Debug("wemo response (raw)", "status", resp.StatusCode, "body", body)

	if resp.StatusCode != 200 {
		return None, fmt.Errorf("non-200 response from Wemo device %s: %d", w.Name, resp.StatusCode)
	}

	return parseWemoResponse(body, logger)
}

func (w *Wemo) post(op Operation, state State, address string) (*http.Response, error) {
	w.Logger.Debug("post", "op", op, "state", state, "address", address)
	xml, action, err := w.makeXml(op, state)
	if err != nil {
		return nil, fmt.Errorf("error getting wemo xml: %w", err)
	}

	url := fmt.Sprintf("http://%s:%d%s", address, w.Port, EventPath)
	req, err := http.NewRequest(http.MethodPost, url, xml)
	if err != nil {
		return nil, fmt.Errorf("error creating Request: %w", err)
	}

	req.Header.Add("Content-Type", `text/xml; charset="utf-8"`)
	req.Header.Add("SOAPACTION", fmt.Sprintf(`"urn:Belkin:service:basicevent:1#%s"`, action))

	// otherwise, many calls fail with: Post "http://x.x.x.x:49153/upnp/control/basicevent1": EOF"
	req.Close = true

	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error calling client.Do: %w", err)
	}

	return resp, nil
}

func (w *Wemo) makeXml(op Operation, state State) (*bytes.Buffer, string, error) {
	vars := struct {
		Action string
		State  string
		Value  string
	}{
		Action: string(op),
		State:  "BinaryState",
	}

	if op == Set {
		vars.Value = strconv.Itoa(int(state))
	}

	var b bytes.Buffer
	if err := w.soapTempl.Execute(&b, vars); err != nil {
		return nil, "", fmt.Errorf("error executing template: %w", err)
	}

	return &b, vars.Action, nil
}

func parseWemoResponse(body []byte, logger *slog.Logger) (State, error) {
	pattern := `<BinaryState>(\d+)(?:\|\d+)*</BinaryState>`
	regex := regexp.MustCompile(pattern)
	match := regex.FindSubmatch(body)

	if len(match) < 1 {
		return None, fmt.Errorf("couldn't extract state from wemo response")
	}
	logger.Debug("wemo response (parsed)", "value", string(match[1]))

	if string(match[1]) == "0" {
		return Off, nil
	}

	return On, nil
}
