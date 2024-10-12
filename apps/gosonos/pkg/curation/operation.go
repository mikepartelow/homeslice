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
)

func ParseOp(s string) (Op, error) {
	s = strings.ToLower(s)
	switch s {
	case "pause":
		return PauseOp, nil
	case "play":
		return PlayOp, nil
	}
	return InvalidOp, fmt.Errorf("invalid op %q", s)
}
