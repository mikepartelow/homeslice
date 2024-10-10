package main

import (
	"fmt"
	"mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/player"
	"mp/gosonos/pkg/playlist"
	"mp/gosonos/pkg/sonos"
	"mp/gosonos/pkg/track"
	"net"
	"sync"
)

func main() {
	// DR
	caddress, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("192.168.1.204:%d", sonos.PlayerPort)) // FIXME: awkward
	check(err)

	coordinator := &sonos.Player{
		Addr: caddress,
	}

	ips := []string{
		"192.168.1.169", // K
		"192.168.1.185", // B
		"192.168.1.188", // L
	}

	var players []player.Player
	for _, ip := range ips {
		a, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("%s:%d", ip, sonos.PlayerPort)) // FIXME: awkward
		check(err)

		players = append(players, &sonos.Player{Addr: a})
	}

	trackIds := []string{
		"73569259",
		"16334233",
		"21702638",
		"97874177",
	}

	var tracks []track.Track
	for _, tid := range trackIds {
		tracks = append(tracks, &playlist.TidalTrack{ID: track.TrackID(tid)})
	}

	playlist := &playlist.Playlist{Name: "Example 1", Tracks: tracks}

	var wg sync.WaitGroup
	err = curation.Play(playlist, coordinator, players, 0, &wg)
	check(err)

	wg.Wait()
}

func check(err error) {
	fmt.Println("FIXME")
	if err != nil {
		panic(err)
	}
}
