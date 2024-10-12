package curation

import (
	"strings"
)

type ID string

func ParseID(s string) (ID, error) {
	return ID(strings.ToLower(s)), nil
}
