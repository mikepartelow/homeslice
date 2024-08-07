package main

import (
	"fmt"
	"mp/lmz/pkg/auth"
	"mp/lmz/pkg/config"
	"mp/lmz/pkg/lmz"
	"net/http"
	"os"
	"strconv"
	"strings"

	"log/slog"
)

type Op int

const (
	_ Op = iota
	Status
	On
	Off
	Serve
)

const (
	Port = 8000
)

func main() {
	logger := mustMakeLogger()

	op := MustGetOp()

	c := config.MustRead()
	t := must(auth.GetToken(c))

	l := lmz.New(c, t)

	var output string
	switch op {
	case On:
		check(l.TurnOn())
		output = "ON"
	case Off:
		check(l.TurnOff())
		output = "OFF"
	case Status:
		status := must(l.Status())
		localTime := status.Received.Local()
		output = "Status as of " + localTime.String() + ": " + status.MachineStatus
	case Serve:
		handler := makeHandler(logger, l)
		http.HandleFunc("PUT /", handler)

		logger.Info("Listening", "port", Port)
		if err := http.ListenAndServe(":"+strconv.Itoa(Port), nil); err != nil {
			logger.Error("Error: http.ListenAndServe", "error", err)
			os.Exit(1)

		}
	}

	fmt.Println(output)
}

func makeHandler(logger *slog.Logger, l *lmz.LMZ) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		logger.Debug(r.URL.Path, "method", r.Method)

		op := strings.ToLower(r.FormValue("op"))
		logger.Debug(r.URL.Path, "op", op)

		switch op {
		case "on":
			if err := l.TurnOn(); err != nil {
				w.WriteHeader(http.StatusInternalServerError)
				return
			}
		case "off":
			if err := l.TurnOff(); err != nil {
				w.WriteHeader(http.StatusInternalServerError)
				return
			}
		default:
			w.WriteHeader(http.StatusBadRequest)
			return
		}
	}
}

func showUsageAndExit() {
	fmt.Println("Usage: ", os.Args[0], "[on|off|status|serve]")
	os.Exit(1)
}

func MustGetOp() Op {
	if len(os.Args) == 2 {
		switch os.Args[1] {
		case "on":
			return On
		case "off":
			return Off
		case "status":
			return Status
		case "serve":
			return Serve
		}
	}
	showUsageAndExit()
	return Op(-1)
}

func check(err error) {
	if err != nil {
		panic(err)
	}
}

func must[T any](thing T, err error) T {
	check(err)
	return thing
}

func mustMakeLogger() *slog.Logger {
	level := slog.LevelInfo
	if v := os.Getenv("LOG_LEVEL"); v != "" {
		switch strings.ToLower(v) {
		case "debug":
			level = slog.LevelDebug
		case "info":
			level = slog.LevelInfo
		case "warn":
			level = slog.LevelWarn
		case "error":
			level = slog.LevelError
		default:
			panic(fmt.Sprintf("unknown log level: %s", v))
		}
	}

	h := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{AddSource: true, Level: level})
	return slog.New(h)
}
