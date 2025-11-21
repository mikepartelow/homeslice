package buttons

import (
	"fmt"
	"io"
	"net/http"
	"strings"

	"log/slog"

	lru "github.com/hashicorp/golang-lru/v2"
)

type Status int

const (
	Off Status = iota
	On
)

func (s Status) String() string {
	if s == On {
		return "ON"
	}
	return "OFF"
}

type Server struct {
	clocktimeUrl string
	logger       *slog.Logger
	buttons      *lru.Cache[string, Status]
}

func NewServer(logger *slog.Logger, clocktimeUrl string) *Server {
	buttons, err := lru.New[string, Status](128)
	if err != nil {
		logger.Error(err.Error())
		panic(err)
	}

	return &Server{
		clocktimeUrl: clocktimeUrl,
		logger:       logger,
		buttons:      buttons,
	}
}

func (s Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	s.logger.Debug(r.URL.Path, "method", r.Method)

	parts := strings.Split(r.URL.Path, "/")

	if r.Method == http.MethodPost {
		s.post(w, r, parts)
	} else {
		s.get(w, r, parts)
	}
}

func (s Server) post(w http.ResponseWriter, r *http.Request, parts []string) {
	const WantParts = 7
	if len(parts) != WantParts {
		s.logger.Error("unexpected parts", "want", WantParts, "got", len(parts))
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	id, op := parts[4], parts[5]
	s.logger.Info("buttons", "id", id, "op", op)

	switch op {
	case "on":
		s.buttons.Add(id, On)
	case "off":
		s.buttons.Add(id, Off)
	default:
		s.logger.Error("uknown op", "op", op)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	_, _ = fmt.Fprintf(w, "OK")
}

func (s Server) get(w http.ResponseWriter, r *http.Request, parts []string) {
	const WantParts = 6
	if len(parts) != WantParts {
		s.logger.Error("unexpected parts", "want", WantParts, "got", len(parts))
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	id := parts[4]
	s.logger.Info("buttons", "id", id)

	status, ok := s.buttons.Get(id)
	if !ok {
		s.logger.Error("unknown button", "id", id)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	body := status.String()
	if parts[3] == "buttontimes" {
		clocktime, err := s.getClocktime()
		if err != nil {
			s.logger.Error("error fetching clocktime", "error", err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}

		body += ":" + clocktime
	}

	_, _ = fmt.Fprintln(w, body)
}

func (s Server) getClocktime() (string, error) {
	resp, err := http.Get(s.clocktimeUrl)
	if err != nil {
		return "", fmt.Errorf("couldn't get clocktime from %s: %w", s.clocktimeUrl, err)
	}
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("clocktime not OK. status: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("couldn't read response body: %w", err)
	}

	return strings.TrimSpace(string(body)), nil
}
