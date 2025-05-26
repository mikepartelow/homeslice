package lmz

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"mp/lmz/pkg/config"
	"net/http"
	"net/url"
	"time"
)

const (
	lmzApiUrl        = "http://lion.lamarzocco.io/api/customer-app/"
	WidgetCodeStatus = "CMMachineStatus"
	TokenLifespan    = time.Duration(time.Minute * 10)
)

// LMZ communicates with a La Marzocco Linea, and possibly other La Marzocco machines.
type LMZ struct {
	c            *config.Config
	newTokenAt   time.Time
	token        string
	refreshToken string
}

// New returns a new LMZ client
func New(c *config.Config) *LMZ {
	return &LMZ{
		c: c,
	}
}

// Status returns the status of the machine, or an error.
func (l *LMZ) Status() (MachineStatus, error) {
	if err := l.auth(); err != nil {
		return StatusErr, err
	}

	endpoint, err := url.JoinPath(lmzApiUrl, fmt.Sprintf("things/%s/dashboard", l.c.Serial))
	if err != nil {
		return StatusErr, fmt.Errorf("error constructing URL: %w", err)
	}

	req, err := http.NewRequest("GET", endpoint, nil)
	if err != nil {
		return StatusErr, fmt.Errorf("error creating request for %q: %w", endpoint, err)
	}

	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", l.token))

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return StatusErr, fmt.Errorf("error getting status: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return StatusErr, logError(endpoint, resp)
	}

	var dashboard thingDashboard

	err = json.NewDecoder(resp.Body).Decode(&dashboard)
	if err != nil {
		return StatusErr, fmt.Errorf("error decoding response JSON: %w", err)
	}

	status := StatusErr
	for _, w := range dashboard.Widgets {
		if w.Code == WidgetCodeStatus {
			status = MachineStatus(w.Output.Status)
			break
		}
	}
	if status == StatusErr {
		return StatusErr, errors.New("couldn't extract status from response JSON")
	}

	return status, nil
}

// TurnOn sets the machine to BrewingMode, AKA "on"
func (l *LMZ) TurnOn() error {
	return l.setStatus(StatusBrewingMode)
}

// TurnOff sets the machine to StandBy, AKA "off"
func (l *LMZ) TurnOff() error {
	return l.setStatus(StatusStandBy)
}

func (l *LMZ) setStatus(status MachineStatus) error {
	if err := l.auth(); err != nil {
		return err
	}

	endpoint, err := url.JoinPath(lmzApiUrl, fmt.Sprintf("things/%s/command/CoffeeMachineChangeMode", l.c.Serial))
	if err != nil {
		return fmt.Errorf("error constructing URL: %w", err)
	}

	body, err := newChangeModeBody(status)
	if err != nil {
		return fmt.Errorf("couldn't construct changeModeBody: %w", err)
	}

	req, err := http.NewRequest("POST", endpoint, body)
	if err != nil {
		return fmt.Errorf("error creating status request: %w", err)
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", l.token))
	req.Header.Set("Content-type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("error posting to %q: %w", endpoint, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return logError(endpoint, resp)
	}

	return nil
}

func (l *LMZ) auth() error {
	needRefresh := l.refreshToken != "" && time.Now().After(l.newTokenAt)

	if l.token == "" || needRefresh {
		slog.Warn("fetching auth token", "needRefresh", needRefresh)
		return l.signin(needRefresh)
	}

	return nil
}

func (l *LMZ) signin(refresh bool) error {
	endpoint, body, err := l.prepareSignin(refresh)
	if err != nil {
		return fmt.Errorf("error preparing signin: %w", err)
	}

	resp, err := http.Post(endpoint, "application/json", body)
	if err != nil {
		return fmt.Errorf("error making auth request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return logError(endpoint, resp)
	}

	var signinResponse signinResponseBody

	err = json.NewDecoder(resp.Body).Decode(&signinResponse)
	if err != nil {
		return fmt.Errorf("error decoding auth response JSON: %w", err)
	}
	l.token, l.refreshToken, l.newTokenAt = signinResponse.Token, signinResponse.RefreshToken, time.Now().Add(TokenLifespan)

	slog.Info("fetched auth token", "expires_at", l.newTokenAt)

	return nil
}

func (l *LMZ) prepareSignin(refresh bool) (string, io.Reader, error) {
	var endpoint string
	var err error
	var body io.Reader

	if refresh {
		endpoint, err = url.JoinPath(lmzApiUrl, "auth/refreshtoken")
		if err != nil {
			return "", nil, fmt.Errorf("error constructing URL: %w", err)
		}
		body, err = newRefreshTokenBody(l.c.Auth.Username, l.refreshToken)
		if err != nil {
			return "", nil, fmt.Errorf("error constructing refresh token body: %w", err)
		}
	} else {
		endpoint, err = url.JoinPath(lmzApiUrl, "auth/signin")
		if err != nil {
			return "", nil, fmt.Errorf("error constructing URL: %w", err)
		}
		body, err = newSigninBody(l.c.Auth.Username, l.c.Auth.Password)
		if err != nil {
			return "", nil, fmt.Errorf("error constructing signin body: %w", err)
		}
	}

	return endpoint, body, nil
}

func logError(endpoint string, resp *http.Response) error {
	body, _ := io.ReadAll(resp.Body)
	slog.Error("error response from status endpoint",
		"status", resp.Status,
		"headers", resp.Header,
		"body", string(body),
	)
	return fmt.Errorf("error response from %q: %s", endpoint, resp.Status)
}
