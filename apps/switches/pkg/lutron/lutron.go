package lutron

import (
	"bufio"
	"errors"
	"fmt"
	"log/slog"
	"net"
	"os"
	"strconv"
	"strings"
	"time"
)

const (
	// DefaultPort is the default Telnet port for Lutron integrations.
	DefaultPort = 23

	defaultTimeout  = 5 * time.Second
	loginReadLimit  = 8
	loginReadMax    = 2048
	responseReadMax = 12
)

var errUnexpectedResponse = errors.New("unexpected lutron response")

// Lutron implements switches.Switch via the Lutron telnet protocol.
// Authentication uses LUTRON_TELNET_USERNAME and LUTRON_TELNET_PASSWORD.
type Lutron struct {
	id            string
	integrationID int
	address       string
	port          int
	logger        *slog.Logger
	username      string
	password      string
	timeout       time.Duration
}

// New creates a Lutron telnet client for a specific integration ID.
func New(id string, address net.IP, port int, integrationID int, logger *slog.Logger) *Lutron {
	if port == 0 {
		port = DefaultPort
	}

	return &Lutron{
		id:            id,
		integrationID: integrationID,
		address:       address.String(),
		port:          port,
		logger:        logger,
		username:      os.Getenv("LUTRON_TELNET_USERNAME"),
		password:      os.Getenv("LUTRON_TELNET_PASSWORD"),
		timeout:       defaultTimeout,
	}
}

// ID returns the switch identifier configured in switches.json.
func (l *Lutron) ID() string { return l.id }

func (l *Lutron) On() error {
	l.logger.Debug("lutron on", "id", l.id, "integration_id", l.integrationID)
	return l.setLevel(100)
}

func (l *Lutron) Off() error {
	l.logger.Debug("lutron off", "id", l.id, "integration_id", l.integrationID)
	return l.setLevel(0)
}

func (l *Lutron) Toggle() error {
	l.logger.Debug("lutron toggle", "id", l.id, "integration_id", l.integrationID)
	on, err := l.getState()
	if err != nil {
		return err
	}
	if on {
		return l.Off()
	}
	return l.On()
}

func (l *Lutron) getState() (bool, error) {
	cmd := fmt.Sprintf("?OUTPUT,%d,1", l.integrationID)
	l.logger.Debug("lutron getState", "id", l.id, "cmd", cmd)
	level, err := l.runQuery(cmd)
	if err != nil {
		return false, err
	}
	return level > 0, nil
}

func (l *Lutron) setLevel(level int) error {
	cmd := fmt.Sprintf("#OUTPUT,%d,1,%d", l.integrationID, level)
	l.logger.Debug("lutron setLevel", "id", l.id, "cmd", cmd, "level", level)
	return l.send(cmd)
}

func (l *Lutron) runQuery(cmd string) (float64, error) {
	target := net.JoinHostPort(l.address, strconv.Itoa(l.port))
	l.logger.Debug("lutron connect", "id", l.id, "target", target)
	conn, err := net.DialTimeout("tcp", target, l.timeout)
	if err != nil {
		l.logger.Error("lutron connect failed", "id", l.id, "error", err)
		return 0, err
	}
	defer func() { _ = conn.Close() }()

	l.logger.Debug("lutron connection success", "id", l.id, "target", target)

	reader := bufio.NewReader(conn)
	if err := l.maybeLogin(reader, conn); err != nil {
		l.logger.Error("lutron login failed", "id", l.id, "error", err)
		return 0, err
	}

	l.logger.Debug("lutron login success", "id", l.id, "target", target)

	l.logger.Debug("lutron cmd", "id", l.id, "target", target, "cmd", cmd)
	if err := l.writeLine(conn, cmd); err != nil {
		l.logger.Error("lutron write failed", "id", l.id, "error", err)
		return 0, err
	}

	_ = conn.SetReadDeadline(time.Now().Add(l.timeout))
	level, err := l.readLevel(reader)
	if err != nil {
		l.logger.Error("lutron read failed", "id", l.id, "error", err)
		return 0, err
	}
	l.logger.Debug("lutron response", "id", l.id, "level", level)
	return level, nil
}

func (l *Lutron) send(cmd string) error {
	target := net.JoinHostPort(l.address, strconv.Itoa(l.port))
	l.logger.Debug("lutron connect", "id", l.id, "target", target)
	conn, err := net.DialTimeout("tcp", target, l.timeout)
	if err != nil {
		l.logger.Error("lutron connect failed", "id", l.id, "error", err)
		return err
	}
	defer func() { _ = conn.Close() }()

	l.logger.Debug("lutron connection success", "id", l.id, "target", target)

	reader := bufio.NewReader(conn)
	if err := l.maybeLogin(reader, conn); err != nil {
		l.logger.Error("lutron login failed", "id", l.id, "error", err)
		return err
	}

	l.logger.Debug("lutron login success", "id", l.id, "target", target)

	l.logger.Debug("lutron cmd", "id", l.id, "target", target, "cmd", cmd)
	if err := l.writeLine(conn, cmd); err != nil {
		l.logger.Error("lutron write failed", "id", l.id, "error", err)
		return err
	}

	return nil
}

func (l *Lutron) maybeLogin(reader *bufio.Reader, conn net.Conn) error {
	if l.username == "" || l.password == "" {
		return fmt.Errorf("username/password required")
	}

	deadline := time.Now().Add(l.timeout)
	_ = conn.SetReadDeadline(deadline)

	for i := 0; i < loginReadLimit; i++ {
		token, err := l.readUntilAny(reader, []string{"login:", "username:", "password:", "gnet>"})
		if err != nil {
			l.logger.Debug("lutron login read", "id", l.id, "error", err, "attempt", i+1)
			return err
		}
		switch {
		case token == "login:" || token == "username:":
			l.logger.Debug("lutron login prompt", "id", l.id, "prompt", "username")
			if err := l.writeLine(conn, l.username); err != nil {
				return err
			}
		case token == "password:":
			l.logger.Debug("lutron login prompt", "id", l.id, "prompt", "password")
			if err := l.writeLine(conn, l.password); err != nil {
				return err
			}
			return nil
		case token == "gnet>":
			l.logger.Debug("lutron login prompt", "id", l.id, "prompt", "gnet>")
			return nil
		}
	}

	return fmt.Errorf("login prompt not found")
}

func (l *Lutron) readLevel(reader *bufio.Reader) (float64, error) {
	for i := 0; i < responseReadMax; i++ {
		line, err := reader.ReadString('\n')
		if err != nil {
			return 0, err
		}
		line = strings.TrimSpace(line)
		l.logger.Debug("lutron response line", "id", l.id, "line", line)
		if line == "" || strings.HasSuffix(line, ">") {
			continue
		}

		level, ok := parseOutputLevel(line, l.integrationID)
		if !ok {
			continue
		}
		return level, nil
	}

	return 0, errUnexpectedResponse
}

func (l *Lutron) writeLine(conn net.Conn, value string) error {
	_, err := fmt.Fprintf(conn, "%s\r\n", value)
	return err
}

func (l *Lutron) readUntilAny(reader *bufio.Reader, tokens []string) (string, error) {
	var buf strings.Builder
	for buf.Len() < loginReadMax {
		b, err := reader.ReadByte()
		if err != nil {
			return "", err
		}
		buf.WriteByte(b)
		lower := strings.ToLower(buf.String())
		for _, token := range tokens {
			if strings.Contains(lower, token) {
				l.logger.Debug("lutron login buffer", "id", l.id, "token", token, "buf", strings.TrimSpace(buf.String()))
				return token, nil
			}
		}
	}
	return "", fmt.Errorf("login buffer exceeded %d bytes", loginReadMax)
}

// parseOutputLevel parses a ~OUTPUT response and returns the output level.
func parseOutputLevel(line string, integrationID int) (float64, bool) {
	parts := strings.Split(line, ",")
	if len(parts) < 4 {
		return 0, false
	}
	if strings.TrimSpace(parts[0]) != "~OUTPUT" {
		return 0, false
	}
	id, err := strconv.Atoi(strings.TrimSpace(parts[1]))
	if err != nil || id != integrationID {
		return 0, false
	}
	level, err := strconv.ParseFloat(strings.TrimSpace(parts[3]), 64)
	if err != nil {
		return 0, false
	}
	return level, true
}
