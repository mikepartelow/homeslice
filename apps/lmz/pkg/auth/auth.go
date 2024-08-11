package auth

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"

	"mp/lmz/pkg/config"
)

// TODO: use refresh tokens, don't password auth every time

const (
	lmzCMS = "https://cms.lamarzocco.io"
)

// GetToken returns a expireable OAuth 2.0 access token and the time when a client should request a new token
// GetToken implements an Oauth 2.0 Client Credentials Flow
// https://auth0.com/docs/get-started/authentication-and-authorization-flow/client-credentials-flow
func GetToken(c *config.Config) (string, time.Time, error) {
	endpoint, err := url.JoinPath(lmzCMS, "/oauth/v2/token")
	if err != nil {
		return "", time.Time{}, fmt.Errorf("error joining URL: %w", err)
	}

	formData := url.Values{}
	formData.Set("grant_type", "password")
	formData.Set("username", c.Auth.Username)
	formData.Set("password", c.Auth.Password)

	body := strings.NewReader(formData.Encode())

	req, err := http.NewRequest("POST", endpoint, body)
	if err != nil {
		return "", time.Time{}, fmt.Errorf("error posting to CMS endpoint: %w", err)
	}

	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("clientID", c.Auth.ClientId)
	req.Header.Set("clientSecret", c.Auth.ClientSecret)

	req.Header.Set("Authorization", "Basic "+makeBearerToken(c.Auth.ClientId, c.Auth.ClientSecret))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", time.Time{}, fmt.Errorf("error during Authorization: %w", err)
	}
	defer resp.Body.Close()

	var response struct {
		AccessToken string `json:"access_token"`
		ExpiresIn   int    `json:"expires_in"`
	}

	err = json.NewDecoder(resp.Body).Decode(&response)
	if err != nil {
		return "", time.Time{}, fmt.Errorf("error decoding auth JSON: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		panic(fmt.Sprintf("oops: %d", resp.StatusCode))
	}

	response.ExpiresIn -= 8
	askAgainAt := time.Now().Add(time.Duration(time.Second * time.Duration(response.ExpiresIn)))

	return response.AccessToken, askAgainAt, nil
}

func makeBearerToken(clientID, clientSecret string) string {
	text := clientID + ":" + clientSecret
	return base64.URLEncoding.EncodeToString([]byte(text))
}
