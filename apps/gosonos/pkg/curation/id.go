package curation

import (
	"fmt"
	"regexp"
	"strings"
)

type ID struct{ id string } // this way, we can't say ID("invalid id"), we must ParseID("valid-id")

func ParseID(s string) (ID, error) {
	s = strings.ToLower(s)

	if !regexp.MustCompile(`^[\w-]+$`).MatchString(s) {
		return ID{}, fmt.Errorf("invalid curation id %q", s)
	}

	return ID{id: s}, nil
}

func (id ID) String() string {
	return id.id
}
