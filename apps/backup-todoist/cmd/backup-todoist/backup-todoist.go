package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"mp/backup-todoist/pkg/todoist"
	"os"
	"path"
	"time"

	"github.com/go-git/go-git/v5"
	"github.com/go-git/go-git/v5/plumbing/object"
	"github.com/go-git/go-git/v5/plumbing/transport/ssh"
)

type BackerUpper struct {
	Todoist        *todoist.Client
	GitCloneUrl    string
	PrivateKeyPath string
	AuthorName     string
	AuthorEmail    string
	Filename       string
	CommitMessage  string
	Logger         *slog.Logger
}

func main() {
	logger := slog.Default()

	bu := BackerUpper{
		Todoist: &todoist.Client{
			Token: mustGetenv("TODOIST_TOKEN"),
		},
		GitCloneUrl:    mustGetenv("GITHUB_BACKUP_GIT_CLONE_URL"),
		PrivateKeyPath: mustGetenv("GITHUB_BACKUP_PRIVATE_KEY_PATH"),
		AuthorName:     mustGetenv("GITHUB_BACKUP_AUTHOR_NAME"),
		AuthorEmail:    mustGetenv("GITHUB_BACKUP_AUTHOR_EMAIL"),
		CommitMessage:  getenvOrDefault("GITHUB_BACKUP_COMMIT_MESSAGE", "backup"),
		Filename:       getenvOrDefault("TODOIST_BACKUP_FILENAME", "backup.json"),
		Logger:         logger,
	}

	err := bu.Backup()
	if err != nil {
		logger.Error("backup failed", "error", err)
		panic(err)
	}

	logger.Info("backup succeeded")
}

func (b *BackerUpper) Backup() error {
	publicKeys, err := ssh.NewPublicKeysFromFile("git", b.PrivateKeyPath, "")
	if err != nil {
		b.Logger.Error("error reading SSH key", "error", err)
		panic(err)
	}

	d, err := b.Todoist.Dump()
	if err != nil {
		return fmt.Errorf("error dumping Todoist: %w", err)
	}

	err = b.pushBackup(publicKeys, func(w io.Writer) error {
		return json.NewEncoder(w).Encode(&d)
	})
	if err != nil {
		return fmt.Errorf("error pushing backup: %w", err)
	}

	return nil
}

func (b *BackerUpper) pushBackup(publicKeys *ssh.PublicKeys, writer func(io.Writer) error) error {
	clonePath, err := os.MkdirTemp("", "")
	if err != nil {
		return fmt.Errorf("couldn't create temp dir: %w", err)
	}

	repo, err := git.PlainClone(clonePath, false, &git.CloneOptions{
		URL:  b.GitCloneUrl,
		Auth: publicKeys,
	})
	if err != nil {
		return fmt.Errorf("couldn't clone %q: %w", b.GitCloneUrl, err)
	}

	worktree, err := repo.Worktree()
	if err != nil {
		return fmt.Errorf("couldn't get Worktree: %w", err)
	}

	repoFilename := path.Join(clonePath, b.Filename)
	file, err := os.Create(repoFilename)
	if err != nil {
		return fmt.Errorf("couldn't open file %q: %w", repoFilename, err)
	}
	defer func() { _ = file.Close() }()

	err = writer(file)
	if err != nil {
		return fmt.Errorf("couldn't write file %q: %w", repoFilename, err)
	}
	defer func() { _ = file.Close() }()

	_, err = worktree.Add(b.Filename)
	if err != nil {
		return fmt.Errorf("couldn't add %q: %w", b.Filename, err)
	}

	_, err = worktree.Commit(b.CommitMessage, &git.CommitOptions{
		Author: &object.Signature{
			Name:  b.AuthorName,
			Email: b.AuthorEmail,
			When:  time.Now(),
		},
	})
	if err != nil {
		return fmt.Errorf("couldn't commit %q: %w", b.Filename, err)
	}

	err = repo.Push(&git.PushOptions{
		Auth: publicKeys,
	})
	if err != nil {
		return fmt.Errorf("couldn't push repo: %w", err)
	}

	return nil
}

func mustGetenv(name string) string {
	if v := os.Getenv(name); v != "" {
		return v
	}

	panic(fmt.Sprintf("couldn't get required env var %q", name))
}

func getenvOrDefault(name, defaultVal string) string {
	if v := os.Getenv(name); v != "" {
		return v
	}

	return defaultVal
}
