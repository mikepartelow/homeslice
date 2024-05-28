package kasa

import (
	"log/slog"
	"mp/switches/pkg/kasa/wire"
	"net"
)

const (
	HostPort = "9999"
)

type Kasa struct {
	id          string
	destination string

	conn   *wire.Connection
	logger *slog.Logger
}

func New(id string, address net.IP, logger *slog.Logger) *Kasa {
	return &Kasa{
		id:          id,
		destination: net.JoinHostPort(address.String(), HostPort),
		logger:      logger,
	}
}

func (k *Kasa) ID() string {
	return k.id
}

func (k *Kasa) On() error {
	k.logger.Info("On")
	return k.setState(On)
}

func (k *Kasa) Off() error {
	k.logger.Info("Off")
	return k.setState(Off)
}

func (k *Kasa) Toggle() error {
	k.logger.Info("Toggle")
	s, err := k.getState()
	if err != nil {
		k.logger.Error("getState", "error", err)
		return err
	}
	k.logger.Info("current", "state", s)
	if s == On {
		return k.Off()
	}
	return k.On()
}

func (k *Kasa) getState() (OnOff, error) {
	request := GenericRequest{
		System: &SystemRequests{
			GetSysinfo: &GetSysinfoRequest{},
		},
	}
	var response GenericResponse
	if err := k.sendCommand(request, &response); err != nil {
		return Off, err
	}
	return response.System.SysInfo.LightState.OnOff, nil
}

func (k *Kasa) setState(state OnOff) error {
	request := GenericRequest{
		LightingService: &LightingService{
			TransitionLightState: &TransitionLightState{
				OnOff: state,
			},
		},
		System: &SystemRequests{
			SetRelayState: &SetRelayStateRequest{
				State: state,
			},
		},
	}
	var response GenericResponse
	if err := k.sendCommand(request, &response); err != nil {
		return err
	}
	return nil
}

func (k *Kasa) sendCommand(data interface{}, response interface{}) error {
	conn, err := wire.NewConnection(k.destination, k.logger)
	if err != nil {
		return err
	}

	if err = conn.Write(data); err != nil {
		return err
	}

	if err = conn.Read(response); err != nil {
		return err
	}

	return conn.Close()
}

// Close closes the connect once done. It's vital to close connections when done as TP-Link Smart Home devices are small embedded devices that don't accept many concurrent connections.
func (k *Kasa) Close() error {
	if k.conn == nil {
		return nil
	}
	return k.conn.Close()
}
