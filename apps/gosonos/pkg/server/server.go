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
	DefaultListenPort = 8080
	DefaultSuccess    = "1"
	DefaultFailure    = "0"
)

type Server struct {
	*config.Config

	Logger *slog.Logger

	Port int

	Failure string
	Success string
}

func (s *Server) init() {
	if s.Logger == nil {
		s.Logger = slog.New(
			console.NewHandler(os.Stderr, &console.HandlerOptions{Level: slog.LevelError}),
		)
	}

	if s.Port == 0 {
		s.Port = DefaultListenPort
	}

	if s.Failure == "" {
		s.Failure = DefaultFailure
	}
	if s.Success == "" {
		s.Success = DefaultSuccess
	}

}

func (s *Server) Serve() error {
	s.init()

	http.HandleFunc("POST /curations/{id}/{op}", s.HandleCurations)
	http.HandleFunc("GET /curations/{id}/status", s.HandleCurations)

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

	if r.Method == http.MethodGet {
		// if we got here via http GET, the op is fixed at status
		r.SetPathValue("op", "status")
	}

	c, op, err := s.parseCurationsRequest(r)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		logger.Debug("parse error", "error", err)
		return
	}

	logger = logger.With("id", c.GetID(), "op", op)
	logger.Debug("curation")

	success, err := curation.Do(op, c, s.Coordinator, s.Players, logger)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		logger.Error("error doing op", "error", err)
		return
	}

	if success {
		_, _ = w.Write([]byte(s.Success))
	} else {
		_, _ = w.Write([]byte(s.Failure))
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
