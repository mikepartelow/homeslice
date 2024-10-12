package ttlt_test

import (
	"mp/gosonos/pkg/ttlt"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestTTLT(t *testing.T) {
	d := time.Duration(100 * time.Millisecond)
	b := ttlt.New[bool](d)

	_, ok := b.GetValue()
	assert.False(t, ok)

	vv := b.SetValue(true)
	assert.Equal(t, true, vv)
	v, ok := b.GetValue()
	assert.True(t, ok)
	assert.True(t, v)

	time.Sleep(200 * time.Millisecond)
	_, ok = b.GetValue()
	assert.False(t, ok)

	vv = b.SetValue(false)
	assert.Equal(t, false, vv)
	v, ok = b.GetValue()
	assert.True(t, ok)
	assert.False(t, v)
}
