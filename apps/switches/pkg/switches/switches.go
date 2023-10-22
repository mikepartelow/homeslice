package switches

type Switch interface {
	ID() string
	On() error
	Off() error
	Toggle() error
}
