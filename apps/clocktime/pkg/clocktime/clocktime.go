package clocktime

import (
	"fmt"
	"net/http"
	"time"
)

type Server struct {
	Time     func() time.Time
	Location *time.Location
}

func (s Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	var now time.Time

	if s.Time != nil {
		now = s.Time()
	} else {
		now = time.Now().In(s.Location)
	}

	fmt.Fprintf(w, "%02d%02d", now.Hour(), now.Minute())
}
