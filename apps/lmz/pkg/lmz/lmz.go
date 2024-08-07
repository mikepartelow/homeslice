package lmz

import (
	"bytes"
	"encoding/json"
	"fmt"
	"mp/lmz/pkg/config"
	"net/http"
	"net/url"
	"time"
)

const (
	lmzGW     = "https://gw-lmz.lamarzocco.io"
	statusOff = "StandBy"
	statusOn  = "BrewingMode"
)

// LMZ communicates with a La Marzocco Linea, and possibly other La Marzocco machines.
type LMZ struct {
	c     *config.Config
	token string
}

// New returns a new LMZ client
func New(c *config.Config, token string) *LMZ {
	return &LMZ{
		c:     c,
		token: token,
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
	return l.setStatus(statusOn)
}

// TurnOff sets the machine to StandBy, AKA "off"
func (l *LMZ) TurnOff() error {
	return l.setStatus(statusOff)
}

func (l *LMZ) setStatus(status string) error {
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
