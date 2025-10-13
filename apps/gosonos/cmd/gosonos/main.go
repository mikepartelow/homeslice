package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"mp/gosonos/pkg/config"
	"mp/gosonos/pkg/curation"
	"mp/gosonos/pkg/playlist"
	"mp/gosonos/pkg/server"
	"mp/gosonos/pkg/track"
	"os"
	"strconv"

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

			p := server.Players[0]
			qq, err := p.Queue()
			if err != nil {
				panic(err)
			}
			fmt.Println(qq)

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
			pl, cfg, err := getPlaylist(cmd.String("config"), cmd.String("playlist-id"))
			if err != nil {
				_ = cli.Exit(err.Error(), 1)
			}

			tracks, err := chooseBackupTracks(cmd.String("tidal-backup"))
			if err != nil {
				_ = cli.Exit(err.Error(), 1)
			}

			pl.Tracks = tracks

			ofile, err := os.Create(cmd.String("output"))
			if err != nil {
				_ = cli.Exit(err.Error(), 1)
			}
			defer ofile.Close()

			err = cfg.Write(ofile)
			if err != nil {
				_ = cli.Exit(err.Error(), 1)
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
		},
	}
}

func chooseBackupTracks(backupFilename string) ([]track.Track, error) {
	type BackupTidalTrack struct {
		ID int `json:"id"`
	}

	file, err := os.Open(backupFilename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var backup []BackupTidalTrack
	err = json.NewDecoder(file).Decode(&backup)
	if err != nil {
		return nil, err
	}

	var tracks []track.Track
	for _, btt := range backup {
		tracks = append(tracks, &playlist.TidalTrack{ID: track.TrackID(strconv.Itoa(btt.ID))})
	}

	return tracks, nil
}

func getPlaylist(configPath, playlistID string) (*playlist.Playlist, *config.Config, error) {
	var cfg config.Config

	_, err := cfg.Load(configPath)
	if err != nil {
		return nil, nil, err
	}

	cid, err := curation.ParseID(playlistID)
	if err != nil {
		return nil, nil, err
	}

	pl, ok := cfg.Curations[cid].(*playlist.Playlist)
	if !ok {
		return nil, nil, fmt.Errorf("curation %q is not a Playlist", pl.GetID())
	}

	return pl, &cfg, nil
}
