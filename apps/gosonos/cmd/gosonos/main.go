package main

import (
	"fmt"
	"mp/gosonos/pkg/config"
	"mp/gosonos/pkg/curation"
	"os"
	"sync"
)

func main() {
	file, err := os.Open("config.yaml")
	check(err)

	var cfg config.Config
	err = cfg.Parse(file)
	check(err)

	coordinator := cfg.Coordinator
	players := cfg.Players

	playlist := cfg.Curations[0]

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
