package kasa

import (
	"mp/switches/pkg/kasa/wire"
	"net"
)

const HostPort = "9999"

type Kasa struct {
	destination string

	conn *wire.Connection
}

func New(address net.IP) *Kasa {
	return &Kasa{
		destination: net.JoinHostPort(address.String(), HostPort),
	}
}

func (k *Kasa) SysInfo() (SysInfoResponse, error) {
	request := GenericRequest{
		System: &SystemRequests{
			GetSysinfo: &GetSysinfoRequest{},
		},
	}
	var response GenericResponse
	if err := k.sendCommand(request, &response); err != nil {
		return SysInfoResponse{}, err
	}
	return *response.System.SysInfo, nil
}

func (k *Kasa) sendCommand(data interface{}, response interface{}) error {
	conn, err := wire.NewConnection(k.destination)
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
