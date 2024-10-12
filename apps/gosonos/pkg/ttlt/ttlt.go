package ttlt

import "time"

type TTLT[T any] struct {
	expiry time.Time
	ttl    time.Duration
	value  T
}

func New[T any](ttl time.Duration) *TTLT[T] {
	return &TTLT[T]{
		ttl: ttl,
	}
}

func (t *TTLT[T]) GetValue() (T, bool) {
	return t.value, time.Now().Before(t.expiry)
}

func (t *TTLT[T]) SetValue(value T) T {
	t.value = value
	t.expiry = time.Now().Add(t.ttl)
	return value
}
