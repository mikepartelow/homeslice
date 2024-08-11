package auth

import "testing"

func TestMakeToken(t *testing.T) {
	clientId := "8_1xwei9rtkuckso44ks4o8s0c0oc4swowo00wgw0ogsok84kosg"   // off by one
	clientSecret := "3mgjqpikbfuok8g4s44oo4gsw0ks44okk4kc4kkkko0c8soc8s" // classic programmer error

	want := "OF8xeHdlaTlydGt1Y2tzbzQ0a3M0bzhzMGMwb2M0c3dvd28wMHdndzBvZ3Nvazg0a29zZzozbWdqcXBpa2JmdW9rOGc0czQ0b280Z3N3MGtzNDRva2s0a2M0a2tra28wYzhzb2M4cw=="

	got := makeBearerToken(clientId, clientSecret)
	if want != got {
		t.Errorf("wanted %q got %q", want, got)
	}
}
