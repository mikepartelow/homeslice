package main

import (
	"mp/lmz/pkg/lmz"
	"net/http"
	"strings"

	"log/slog"
)

type Server struct {
	logger   *slog.Logger
	machines map[string]*lmz.LMZ
}

func (s *Server) HandleRoot(w http.ResponseWriter, r *http.Request) {
	s.logger.Debug(r.URL.Path, "method", r.Method)

	id := r.PathValue("id")
	s.logger.Debug(r.URL.Path, "id", id)

	m, ok := s.machines[id]
	if !ok {
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	op := strings.ToLower(r.FormValue("op"))
	s.logger.Debug(r.URL.Path, "id", id, "op", op)

	switch op {
	case "on":
		if err := m.TurnOn(); err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
	case "off":
		if err := m.TurnOff(); err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
	default:
		w.WriteHeader(http.StatusBadRequest)
		return
	}
}
