package main

import (
	"fmt"
	"mp/gosonos/pkg/gosonos"
	"net"
)

func main() {
	a, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("192.168.1.204:%d", gosonos.PlayerPort)) // FIXME: awkward
	check(err)

	p := gosonos.Player{
		Address: a,
	}
	fmt.Println(p)

	err = p.Queue()
	check(err)
}

func check(err error) {
	fmt.Println("FIXME")
	if err != nil {
		panic(err)
	}
}
