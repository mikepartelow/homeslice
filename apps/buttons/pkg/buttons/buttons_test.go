package buttons_test

import (
	"log/slog"
	"mp/buttons/pkg/buttons"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

const (
	ButtonsPath     = "/api/v0/buttons/"
	ButtonTimesPath = "/api/v0/buttontimes/"
)

func TestButtons(t *testing.T) {
	testCases := []struct {
		operations []buttons.Status
		want       buttons.Status
	}{
		{
			operations: []buttons.Status{buttons.On},
			want:       buttons.On,
		},
		{
			operations: []buttons.Status{buttons.On, buttons.On},
			want:       buttons.On,
		},
		{
			operations: []buttons.Status{buttons.On, buttons.Off},
			want:       buttons.Off,
		},
		{
			operations: []buttons.Status{buttons.Off, buttons.Off},
			want:       buttons.Off,
		},
		{
			operations: []buttons.Status{buttons.Off, buttons.On, buttons.Off},
			want:       buttons.Off,
		},
		{
			operations: []buttons.Status{buttons.Off, buttons.On, buttons.On},
			want:       buttons.On,
		},
	}

	const ButtonPath = ButtonsPath + "spam/"

	for _, tC := range testCases {
		t.Run(tC.want.String(), func(t *testing.T) {
			s := buttons.NewServer(slog.Default(), "https://url")

			request, response := play(t, s, ButtonPath, tC.operations)

			s.ServeHTTP(response, request)

			assert.Equal(t, http.StatusOK, response.Code)
			assert.Equal(t, tC.want.String(), strings.TrimSpace(response.Body.String()))
		})
	}
}

func TestButtonTimes(t *testing.T) {
	testCases := []struct {
		operations []buttons.Status
		time       string
		want       string
	}{
		{
			operations: []buttons.Status{buttons.On},
			time:       "1420",
			want:       "ON:1420",
		},
		{
			operations: []buttons.Status{buttons.Off},
			time:       "2323",
			want:       "OFF:2323",
		},
	}

	const ButtonTimePath = ButtonTimesPath + "spam/"

	for _, tC := range testCases {
		t.Run(tC.want, func(t *testing.T) {
			clocktimeServer := makeClocktimeServer(t, tC.time)
			defer clocktimeServer.Close()

			s := buttons.NewServer(slog.Default(), clocktimeServer.URL)

			request, response := play(t, s, ButtonTimePath, tC.operations)

			s.ServeHTTP(response, request)

			assert.Equal(t, http.StatusOK, response.Code)
			assert.Equal(t, tC.want, strings.TrimSpace(response.Body.String()))
		})
	}
}

func play(t *testing.T, s *buttons.Server, buttonPath string, operations []buttons.Status) (*http.Request, *httptest.ResponseRecorder) {
	t.Helper()

	for _, op := range operations {
		reqPath := buttonPath + strings.ToLower(op.String()) + "/"

		request, _ := http.NewRequest(http.MethodPost, reqPath, nil)
		response := httptest.NewRecorder()

		s.ServeHTTP(response, request)

		assert.Equal(t, http.StatusOK, response.Code)
		assert.Equal(t, "OK", response.Body.String())
	}

	request, _ := http.NewRequest(http.MethodGet, buttonPath, nil)
	response := httptest.NewRecorder()

	return request, response
}

func makeClocktimeServer(t *testing.T, time string) *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			t.Errorf("expected request to '/', got: %s", r.URL.Path)
		}
		if r.Method != http.MethodGet {
			t.Errorf("expected HTTP GET, got: %s", r.Method)
		}
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(time))
	}))
}
