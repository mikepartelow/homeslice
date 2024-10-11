package server

import (
	"fmt"
	"log/slog"
	"mp/gosonos/pkg/config"
	"mp/gosonos/pkg/curation"
	"net/http"
	"os"
	"strconv"

	"github.com/phsym/console-slog"
)

const (
	DefaultPort = 8080
)

type Server struct {
	*config.Config

	Logger *slog.Logger
	Port   int
}

func (s *Server) init() {
	if s.Logger == nil {
		s.Logger = slog.New(
			console.NewHandler(os.Stderr, &console.HandlerOptions{Level: slog.LevelError}),
		)
	}

	if s.Port == 0 {
		s.Port = DefaultPort
	}
}

func (s *Server) Serve() error {
	s.init()

	http.HandleFunc("POST /curations/{id}/{op}", s.HandleCurations)

	s.Logger.Warn("Listening", "port", s.Port)
	if err := http.ListenAndServe(":"+strconv.Itoa(s.Port), nil); err != nil {
		s.Logger.Error("http.ListenAndServe", "error", err)
		return fmt.Errorf("http.ListenAndServe failed: %w", err)
	}

	return nil
}

func (s *Server) HandleCurations(w http.ResponseWriter, r *http.Request) {
	logger := s.Logger.With("path", r.URL.Path, "method", r.Method)
	logger.Debug("")

	c, op, err := s.parseCurationsRequest(r)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		logger.Debug("parse error", "error", err)
		return
	}

	logger = logger.With("id", c.GetID(), "op", op)
	s.Logger.Debug("curation")

	err = c.Do(op, s.Coordinator, s.Players)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		logger.Error("error doing op", "error", err)
		return
	}
}

func (s *Server) parseCurationsRequest(r *http.Request) (curation.Curation, curation.Op, error) {
	id, err := curation.ParseID(r.PathValue("id"))
	if err != nil {
		return nil, curation.InvalidOp, fmt.Errorf("couldn't parse id %q: %w", r.PathValue("id"), err)
	}

	c, ok := s.Curations[id]
	if !ok {
		return nil, curation.InvalidOp, fmt.Errorf("invalid id %q: %w", id, err)
	}

	op, err := curation.ParseOp(r.PathValue("op"))
	if err != nil {
		return nil, curation.InvalidOp, fmt.Errorf("couldn't parse op %q: %w", r.PathValue("op"), err)
	}

	return c, op, nil
}
