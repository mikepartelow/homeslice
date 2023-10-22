package switches

import (
	"fmt"
	"net/http"
	"strings"

	"log/slog"
)

type Server struct {
	logger   *slog.Logger
	switches map[string]Switch
}

func NewServer(logger *slog.Logger, switches []Switch) *Server {
	switchMap := make(map[string]Switch)

	for _, s := range switches {
		switchMap[s.ID()] = s
	}

	return &Server{
		logger:   logger,
		switches: switchMap,
	}
}

func (s Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	s.logger.Debug(r.URL.Path, "method", r.Method)

	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}
	parts := strings.Split(r.URL.Path, "/")

	const WantParts = 7
	if len(parts) != WantParts {
		s.logger.Error("unexpected parts", "want", WantParts, "got", len(parts))
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	id, op := parts[4], parts[5]

	sw, ok := s.switches[id]
	if !ok {
		s.logger.Error("unknown id", "id", id)
		w.WriteHeader(http.StatusNotFound)
		return
	}

	var err error
	switch op {
	case "toggle":
		err = sw.Toggle()
	case "on":
		err = sw.On()
	case "off":
		err = sw.Off()
	default:
		s.logger.Error("uknown op", "op", op)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	s.logger.Debug("op result", "err", err, "op", op, "id", id)

	fmt.Fprintf(w, "OK")
}
