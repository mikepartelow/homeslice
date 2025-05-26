package lmz

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
)

type signinRequestBody struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func newSigninBody(username, password string) (io.Reader, error) {
	body := signinRequestBody{
		Username: username,
		Password: password,
	}
	bodyBytes, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("error marshaling signin request body: %w", err)
	}

	return bytes.NewReader(bodyBytes), nil
}

type refreshTokenBody struct {
	Username     string `json:"username"`
	RefreshToken string `json:"refreshToken"`
}

func newRefreshTokenBody(username, refreshToken string) (io.Reader, error) {
	body := refreshTokenBody{
		Username:     username,
		RefreshToken: refreshToken,
	}

	bodyBytes, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("error marshaling refresh token request body: %w", err)
	}

	return bytes.NewReader(bodyBytes), nil
}

type signinResponseBody struct {
	Token        string `json:"accessToken"`
	RefreshToken string `json:"refreshToken"`
}

type thingDashboard struct {
	SerialNumber string            `json:"serialNumber"`
	Name         string            `json:"name"`
	Widgets      []dashboardWidget `json:"widgets"`
}

type dashboardWidget struct {
	Code   string               `json:"code"`
	Output *machineStatusWidget `json:"output,omitempty"`
}

// CMMachineStatus
type machineStatusWidget struct {
	Status string `json:"status"`
}

type MachineStatus string

const (
	StatusErr         MachineStatus = ""
	StatusStandBy     MachineStatus = "StandBy"
	StatusBrewingMode MachineStatus = "BrewingMode"
	StatusPoweredOn   MachineStatus = "PoweredOn"
)

func IsOn(status MachineStatus) bool {
	return status == StatusPoweredOn
}

func IsOff(status MachineStatus) bool {
	return status == StatusStandBy
}

type changeModeBody struct {
	Mode MachineStatus `json:"mode"`
}

func newChangeModeBody(status MachineStatus) (io.Reader, error) {
	body := changeModeBody{
		Mode: status,
	}
	bodyBytes, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("error marshaling signin request body: %w", err)
	}

	return bytes.NewReader(bodyBytes), nil
}
