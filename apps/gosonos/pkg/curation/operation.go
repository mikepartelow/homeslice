package curation

import (
	"fmt"
	"strings"
)

type Op int

const (
	InvalidOp = iota
	PauseOp
	PlayOp
	StatusOp
)

func ParseOp(s string) (Op, error) {
	s = strings.ToLower(s)
	switch s {
	case "pause":
		return PauseOp, nil
	case "play":
		return PlayOp, nil
	case "status":
		return StatusOp, nil
	}
	return InvalidOp, fmt.Errorf("invalid op %q", s)
}
