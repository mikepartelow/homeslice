package main

import (
	"context"
	"fmt"
	"log"
	"mp/gosonos/pkg/config"
	"mp/gosonos/pkg/server"
	"os"

	"github.com/urfave/cli/v3"
)

func main() {
	cmd := &cli.Command{
		Name:  "gosonos",
		Usage: "sonos ops server and cli",
		Commands: []*cli.Command{
			serve(),
			updateConfig(),
		},
	}

	if err := cmd.Run(context.Background(), os.Args); err != nil {
		log.Fatal(err)
	}
}

func serve() *cli.Command {
	return &cli.Command{
		Name:    "serve",
		Aliases: []string{"s"},
		Usage:   "run the gosonos web API",
		Action: func(ctx context.Context, cmd *cli.Command) error {
			var cfg config.Config

			logger, err := cfg.Load(cmd.String("config"), int(cmd.Int("port")))
			if err != nil {
				return cli.Exit(err.Error(), 1)
			}

			for _, c := range cfg.Curations {
				logger.Debug("config", "got curation", c.GetID())
			}

			server := server.Server{
				Config: &cfg,
				Logger: logger,
			}

			if err := server.Serve(); err != nil {
				return cli.Exit(err.Error(), 1)
			}

			return nil
		},
		Flags: []cli.Flag{
			&cli.StringFlag{
				Name:     "config",
				Usage:    "load configuration from `FILE`",
				Sources:  cli.EnvVars("CONFIG_PATH"),
				Required: true,
			},
			&cli.IntFlag{
				Name:    "port",
				Usage:   "listen on `PORT`",
				Value:   8000,
				Sources: cli.EnvVars("LISTEN_PORT"),
			},
		},
	}
}

func updateConfig() *cli.Command {
	return &cli.Command{
		Name:    "update-config",
		Aliases: []string{"uc"},
		Usage:   "update config from a tidal backup",
		Action: func(ctx context.Context, cmd *cli.Command) error {
			fmt.Println("foo")
			return nil
		},
	}
}
