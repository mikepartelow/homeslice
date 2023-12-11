package wemo_test

import (
	"io"
	"mp/switches/pkg/switches"
	"mp/switches/pkg/wemo"
	"net"
	"net/http"
	"net/http/httptest"
	"strconv"
	"strings"
	"testing"

	"log/slog"

	"github.com/stretchr/testify/assert"
)

var _ switches.Switch = &wemo.Wemo{}

func TestOn(t *testing.T) {
	setResponse := "<BinaryState>1</BinaryState>"
	server, ip, port := mockServer(t, "", setResponse)
	defer server.Close()

	w := &wemo.Wemo{
		Address: net.ParseIP(ip),
		Port:    port,
		Logger:  slog.Default(),
	}

	err := w.On()
	assert.NoError(t, err)
}

func TestOff(t *testing.T) {
	setResponse := "<BinaryState>1</BinaryState>"
	server, ip, port := mockServer(t, "", setResponse)
	defer server.Close()

	w := &wemo.Wemo{
		Address: net.ParseIP(ip),
		Port:    port,
		Logger:  slog.Default(),
	}

	err := w.Off()
	assert.NoError(t, err)
}

func TestToggleOn(t *testing.T) {
	getReponse := "<BinaryState>0</BinaryState>"
	setResponse := "<BinaryState>1</BinaryState>"
	server, ip, port := mockServer(t, getReponse, setResponse)
	defer server.Close()

	w := &wemo.Wemo{
		Address: net.ParseIP(ip),
		Port:    port,
		Logger:  slog.Default(),
	}

	err := w.Toggle()
	assert.NoError(t, err)

}

func TestToggleOff(t *testing.T) {
	getReponse := "<BinaryState>1</BinaryState>"
	setResponse := "<BinaryState>0</BinaryState>"
	server, ip, port := mockServer(t, getReponse, setResponse)
	defer server.Close()

	w := &wemo.Wemo{
		Address: net.ParseIP(ip),
		Port:    port,
		Logger:  slog.Default(),
	}

	err := w.Toggle()
	assert.NoError(t, err)
}

func mockServer(t *testing.T, getReponse, setResponse string) (*httptest.Server, string, int) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/upnp/control/basicevent1" {
			t.Errorf("expected request to '/upnp/control/basicevent1', got: %s", r.URL.Path)
		}
		if r.Method != http.MethodPost {
			t.Errorf("expected HTTP POST, got: %s", r.Method)
		}

		body, _ := io.ReadAll(r.Body)
		if strings.Contains(string(body), string(wemo.Get)) {
			_, _ = w.Write([]byte(getReponse))
		} else {
			_, _ = w.Write([]byte(setResponse))
		}
	}))

	parts := strings.Split(strings.ReplaceAll(server.URL, "http://", ""), ":")
	ip := parts[0]
	port, _ := strconv.Atoi(parts[1])

	return server, ip, port
}
