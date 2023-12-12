package kasa_test

import (
	"mp/switches/pkg/kasa"
	"mp/switches/pkg/switches"
)

var _ switches.Switch = &kasa.Kasa{}
