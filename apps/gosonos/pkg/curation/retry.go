package curation

import (
	"log/slog"
	"time"
)

type sleeper func(int) time.Duration

func backoffer(base time.Duration) sleeper {
	return func(i int) time.Duration {
		if i == 0 {
			return base
		}
		return time.Duration(base * time.Duration(1.8*float64(i)))
	}
}

func retry(retries int, s sleeper, logger *slog.Logger, fn func() error) error {
	var err error

	for retry := 0; retry < retries; retry++ {
		logger.Debug("retries()", "retry", retry)
		if err = fn(); err == nil {
			return nil
		}
		if retry+1 < retries {
			d := s(retry)
			logger.Debug("sleeping", "duration", d)
			time.Sleep(d)
		}
	}

	return err
}
