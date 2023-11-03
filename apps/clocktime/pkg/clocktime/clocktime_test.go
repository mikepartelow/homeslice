package clocktime_test

import (
	"mp/clocktime/pkg/clocktime"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

const ApiPath = "/api/v0/clocktime/"

func TestClocktime(t *testing.T) {
	testCases := []struct {
		time time.Time
		want string
	}{
		{
			time: time.Date(2023, 10, 16, 16, 20, 0, 0, time.Local),
			want: "1620",
		},
		{
			time: time.Date(2023, 10, 16, 23, 23, 0, 0, time.Local),
			want: "2323",
		},
		{
			time: time.Date(2023, 10, 16, 9, 1, 0, 0, time.Local),
			want: "0901",
		},
		{
			time: time.Date(2023, 10, 16, 0, 1, 0, 0, time.Local),
			want: "0001",
		},
	}

	for _, tC := range testCases {
		t.Run(tC.want, func(t *testing.T) {
			request, _ := http.NewRequest(http.MethodGet, ApiPath, nil)
			response := httptest.NewRecorder()

			s := clocktime.Server{
				Time: func() time.Time {
					return tC.time
				},
			}

			s.ServeHTTP(response, request)

			got := response.Body.String()

			assert.Equal(t, tC.want, got)
		})
	}
}
