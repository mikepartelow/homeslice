package auth

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strings"

	"mp/lmz/pkg/config"
)

const (
	lmzCMS = "https://cms.lamarzocco.io"
)

// GetToken implements an Oauth 2.0 Client Credentials Flow
// https://auth0.com/docs/get-started/authentication-and-authorization-flow/client-credentials-flow
func GetToken(c *config.Config) (string, error) {
	endpoint, err := url.JoinPath(lmzCMS, "/oauth/v2/token")
	if err != nil {
		return "", fmt.Errorf("error joining URL: %w", err)
	}

	formData := url.Values{}
	formData.Set("grant_type", "password")
	formData.Set("username", c.Auth.Username)
	formData.Set("password", c.Auth.Password)

	body := strings.NewReader(formData.Encode())

	req, err := http.NewRequest("POST", endpoint, body)
	if err != nil {
		return "", fmt.Errorf("error posting to CMS endpoint: %w", err)
	}

	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("clientID", c.Auth.ClientId)
	req.Header.Set("clientSecret", c.Auth.ClientSecret)

	req.Header.Set("Authorization", "Basic "+makeBearerToken(c.Auth.ClientId, c.Auth.ClientSecret))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("error during Authorization: %w", err)
	}
	defer resp.Body.Close()

	var response struct {
		AccessToken string `json:"access_token"`
	}

	err = json.NewDecoder(resp.Body).Decode(&response)
	if err != nil {
		return "", fmt.Errorf("error decoding auth JSON: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		panic(fmt.Sprintf("oops: %d", resp.StatusCode))
	}

	return response.AccessToken, nil
}

func makeBearerToken(clientID, clientSecret string) string {
	text := clientID + ":" + clientSecret
	return base64.URLEncoding.EncodeToString([]byte(text))
}
