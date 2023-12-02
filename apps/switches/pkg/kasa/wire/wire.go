package wire

import (
	"encoding/binary"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"time"
)

type Connection struct {
	conn net.Conn
}

// NewConnection establishes a connection to a TP-Link Smart Home Protocol device.
func NewConnection(address string) (*Connection, error) {
	d := net.Dialer{
		Timeout: time.Second * 60,
	}
	conn, err := d.Dial("tcp", address)
	if err != nil {
		return nil, err
	}
	return &Connection{
		conn: conn,
	}, nil
}

// Write encodes data as a message to the device.
func (c *Connection) Write(data interface{}) error {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return err
	}

	encryptedData := Encrypt(jsonData)
	framedData := Frame(encryptedData)

	_, err = c.conn.Write(framedData)
	return err
}

// Read receives a message parsed as a data structure.
func (c *Connection) Read(data interface{}) error {
	payload, err := ReadFrame(c.conn)
	if err != nil {
		return err
	}
	jsonData := Decrypt(payload)
	fmt.Println(string(jsonData))
	return json.Unmarshal(jsonData, data)
}

// Close closes the connect once done. It's vital to close connections when done as TP-Link Smart Home devices are small embedded devices that don't accept many concurrent connections.
func (c *Connection) Close() error {
	return c.conn.Close()
}

const (
	iv byte = 0xAB
)

// Encrypt encrypts plaintext with TP-Link's form of an Autokey Cipher.
// The function is simply {ciphertext = key XOR plaintext} with the initial key being  0xAB.
func Encrypt(plaintext []byte) []byte {
	ciphertext := make([]byte, len(plaintext))

	key := iv
	for i, currentByte := range plaintext {
		encByte := key ^ currentByte
		key = encByte
		ciphertext[i] = encByte
	}

	return ciphertext
}

// Decrypt decrypts ciphertext encrypted with TP-Link's form of an Autokey Cipher.
// See Encrypt for details.
func Decrypt(ciphertext []byte) []byte {
	plaintext := make([]byte, len(ciphertext))

	key := iv
	for i, currentByte := range ciphertext {
		decByte := key ^ currentByte
		key = currentByte
		plaintext[i] = decByte
	}

	return plaintext
}

const (
	frameHeaderSize = 4
	maxFrameSize    = 1 << 30 // 1 GB
)

var (
	// ErrFrameTooLarge means an incoming frame exceeds limits
	ErrFrameTooLarge = errors.New("recv frame exceeds max frame size of 1GB")
)

// Frame prepends data with the size of data and returns the new data byte slice.
func Frame(data []byte) []byte {
	frameSize := len(data)
	frameBuffer := make([]byte, frameHeaderSize, frameSize+frameHeaderSize)
	binary.BigEndian.PutUint32(frameBuffer, uint32(frameSize))
	return append(frameBuffer, data...)
}

// ReadFrame reads a full frame from r and returns the payload.
func ReadFrame(r io.Reader) ([]byte, error) {
	header := make([]byte, 4)
	if _, err := io.ReadFull(r, header); err != nil {
		return nil, err
	}

	frameSize := binary.BigEndian.Uint32(header)
	if frameSize > maxFrameSize {
		return nil, ErrFrameTooLarge
	}
	frameBuffer := make([]byte, frameSize)

	_, err := io.ReadFull(r, frameBuffer)
	return frameBuffer, err
}
