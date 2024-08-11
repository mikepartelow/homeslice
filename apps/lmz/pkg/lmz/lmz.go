package lmz

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log/slog"
	"mp/lmz/pkg/auth"
	"mp/lmz/pkg/config"
	"net/http"
	"net/url"
	"time"
)

const (
	lmzGW     = "https://gw-lmz.lamarzocco.io"
	StatusOff = "StandBy"
	StatusOn  = "BrewingMode"
)

// LMZ communicates with a La Marzocco Linea, and possibly other La Marzocco machines.
type LMZ struct {
	c          *config.Config
	logger     *slog.Logger
	token      string
	newTokenAt time.Time
}

// New returns a new LMZ client
func New(c *config.Config, l *slog.Logger) *LMZ {
	return &LMZ{
		c:      c,
		logger: l,
	}
}

// Status represents
type Status struct {
	// Received is the time of the last reported status update
	Received time.Time `json:"received"`
	// Machine Status can be "StandBy" or "BrewingMode"
	MachineStatus string `json:"MACHINE_STATUS"`
}

// Status returns the status of the machine, or an error.
func (l *LMZ) Status() (*Status, error) {
	if err := l.auth(); err != nil {
		return nil, err
	}

	endpoint, err := url.JoinPath(lmzGW, fmt.Sprintf("/v1/home/machines/%s/status", l.c.Serial))
	if err != nil {
		return nil, fmt.Errorf("error constructing URL: %w", err)
	}

	req, err := http.NewRequest("GET", endpoint, nil)
	if err != nil {
		return nil, fmt.Errorf("error creating HTTP request: %w", err)
	}

	req.Header.Set("Accept", "application/json")
	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", l.token))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error getting status: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		panic(fmt.Sprintf("oops: %d", resp.StatusCode))
	}

	var status struct {
		Data Status `json:"data"`
	}

	err = json.NewDecoder(resp.Body).Decode(&status)
	if err != nil {
		return nil, fmt.Errorf("error decoding response JSON: %w", err)
	}

	return &status.Data, nil
}

// TurnOn sets the machine to BrewingMode, AKA "on"
func (l *LMZ) TurnOn() error {
	return l.setStatus(StatusOn)
}

// TurnOff sets the machine to StandBy, AKA "off"
func (l *LMZ) TurnOff() error {
	return l.setStatus(StatusOff)
}

func (l *LMZ) setStatus(status string) error {
	if err := l.auth(); err != nil {
		return err
	}

	endpoint, err := url.JoinPath(lmzGW, fmt.Sprintf("/v1/home/machines/%s/status", l.c.Serial))
	if err != nil {
		return fmt.Errorf("error constructing URL: %w", err)
	}

	var bb = struct {
		Status string `json:"status"`
	}{
		Status: status,
	}

	body, err := json.Marshal(bb)
	if err != nil {
		return fmt.Errorf("error marshaling body JSON: %w", err)
	}

	req, err := http.NewRequest("POST", endpoint, bytes.NewBuffer(body))
	if err != nil {
		return fmt.Errorf("error creating status request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", l.token))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("error posting to status endpoint: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("API error: %s", resp.Status)
	}

	return nil
}

func (l *LMZ) auth() error {
	if l.token == "" || time.Now().After(l.newTokenAt) {
		l.logger.Warn("fetching auth token")
		token, newTokenAt, err := auth.GetToken(l.c)
		if err != nil {
			return err
		}
		l.token, l.newTokenAt = token, newTokenAt
	}
	return nil
}
