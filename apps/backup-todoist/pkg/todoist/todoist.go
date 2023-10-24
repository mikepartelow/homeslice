package todoist

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"

	"github.com/google/uuid"
)

const (
	ApiRoot = "https://api.todoist.com/rest/v2/"
)

// Rate Limiting
//
// For each user, you can make a maximum of 450 requests within a 15 minute period.
type Client struct {
	Token string
}

type Dump struct {
	Projects    []Project `json:"projects"`
	ActiveTasks []Task    `json:"active_tasks"`
}

type Project struct {
	Id   string `json:"id"`
	Name string `json:"name"`
}

type Task struct {
	Content   string `json:"content"`
	ProjectId string `json:"project_id"`
	ParentId  string `json:"parent_id"`
}

func (c *Client) Dump() (*Dump, error) {

	return &Dump{}, nil

	// projects, err := c.Projects()
	// if err != nil {
	// 	return nil, fmt.Errorf("error fetching projects: %w", err)
	// }

	// tasks, err := c.ActiveTasks()
	// if err != nil {
	// 	return nil, fmt.Errorf("error fetching tasks: %w", err)
	// }

	// return &Dump{
	// 	Projects:    projects,
	// 	ActiveTasks: tasks,
	// }, nil
}

func (c *Client) Projects() ([]Project, error) {
	var projects []Project

	err := c.do("projects", &projects)
	if err != nil {
		return nil, fmt.Errorf("client error: %w", err)
	}

	return projects, nil
}

func (c *Client) ActiveTasks() ([]Task, error) {
	var tasks []Task

	err := c.do("tasks", &tasks)
	if err != nil {
		return nil, fmt.Errorf("couldn't decode json: %w", err)
	}

	return tasks, nil
}

func (c *Client) do(resource string, things interface{}) error {
	endpoint, err := url.JoinPath(ApiRoot, resource)
	if err != nil {
		return fmt.Errorf("couldn't join url: %w", err)
	}

	req, err := http.NewRequest(http.MethodGet, endpoint, nil)
	if err != nil {
		return fmt.Errorf("couldn't create new Request for %q: %w", endpoint, err)
	}

	u, err := uuid.NewUUID()
	if err != nil {
		return fmt.Errorf("couldn't generate new UUID for %q: %w", endpoint, err)
	}

	req.Header.Add("X-Request-Id", u.String())
	req.Header.Add("Authorization", "Bearer "+c.Token)

	client := http.Client{}

	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("http error: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("http status error: %d", resp.StatusCode)
	}

	return json.NewDecoder(resp.Body).Decode(things)
}
