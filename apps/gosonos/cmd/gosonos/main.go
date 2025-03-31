package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand/v2"
	"mp/gosonos/pkg/config"
	"mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/playlist"
	"mp/gosonos/pkg/server"
	"mp/gosonos/pkg/track"
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

			logger, err := cfg.Load(cmd.String("config"))
			if err != nil {
				return cli.Exit(err.Error(), 1)
			}

			for _, c := range cfg.Curations {
				logger.Debug("config", "got curation", c.GetID())
			}

			server := server.Server{
				Config: &cfg,
				Logger: logger,
				Port:   int(cmd.Int("port")),
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
			var cfg config.Config

			// -1 num-tracks means all tracks from backup
			_, err := cfg.Load(cmd.String("config"))
			if err != nil {
				return cli.Exit(err.Error(), 1)
			}

			playlistID := cmd.String("playlist-id")

			cid, err := curation.ParseID(playlistID)
			if err != nil {
				return cli.Exit(err.Error(), 1)
			}

			pl, ok := cfg.Curations[cid].(*playlist.Playlist)
			if !ok {
				return cli.Exit(fmt.Sprintf("curation %q is not a Playlist", pl.GetID()), 1)
			}

			type BackupTidalTrack struct {
				ID int `json:"id"`
			}

			file, err := os.Open(cmd.String("tidal-backup"))
			if err != nil {
				return cli.Exit(err.Error(), 1)
			}
			defer file.Close()

			var backup []BackupTidalTrack
			err = json.NewDecoder(file).Decode(&backup)
			if err != nil {
				cli.Exit(err.Error(), 1)
			}

			rand.Shuffle(len(backup), func(i, j int) {
				backup[i], backup[j] = backup[j], backup[i]
			})

			numTracks := int(cmd.Int("num-tracks"))
			if numTracks < 1 {
				numTracks = len(backup)
			} else {
				numTracks = min(numTracks, len(backup))
			}

			// tracks := backup[0:numTracks]
			var tracks []track.Track

			for _, tid := range pl.Tracks[0:numTracks] {
				tracks = append(tracks, &playlist.TidalTrack{ID: track.TrackID(tid.TrackID())})
			}

			(cfg.Curations[cid]).(*playlist.Playlist).Tracks = tracks

			ofile, err := os.Create(cmd.String("output"))
			if err != nil {
				cli.Exit(err.Error(), 1)
			}
			defer ofile.Close()

			err = cfg.Write(ofile)
			if err != nil {
				cli.Exit(err.Error(), 1)
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
			&cli.StringFlag{
				Name:     "playlist-id",
				Usage:    "update playlist `PLAYLIST_ID`",
				Sources:  cli.EnvVars("PLAYLIST_ID"),
				Required: true,
			},
			&cli.StringFlag{
				Name:     "output",
				Usage:    "output to `FILE`",
				Required: true,
			},
			&cli.StringFlag{
				Name:     "tidal-backup",
				Usage:    "load track ids from Tidal Backup `FILE`",
				Sources:  cli.EnvVars("TIDAL_BACKUP_PATH"),
				Required: true,
			},
			&cli.IntFlag{
				Name:  "num-tracks",
				Usage: "number of Tidal Backup tracks to copy to gosonos config, or <1 for all",
				Value: 42,
			},
		},
	}
}
