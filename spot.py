import pprint
import sys
import json

import spotipy
import spotipy.util as util

with open("spotify.json", "rb") as f:
    spotify_dict = json.loads(f.read())

    client_id       = spotify_dict['auth']['client-id']
    client_secret   = spotify_dict['auth']['client-secret']
    redirect_uri    = spotify_dict['auth']['redirect-uri']

    username        = spotify_dict['auth']['username']

    # token           = spotify_dict['auth']['token']


scope = 'user-top-read user-follow-read'
token = util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    after = None
    while True:
        reply = sp.current_user_followed_artists(after=after)
        if len(reply['artists']['items']) == 0:
            break

        for artist in reply['artists']['items']:
            print(artist['name'])
            after = artist['id']

    # ranges = ['short_term', 'medium_term', 'long_term']
    # for range in ranges:
    #     print "range:", range
    #     results = sp.current_user_top_artists(time_range=range, limit=50)
    #     for i, item in enumerate(results['items']):
    #         print i, item['name']
    #     print
else:
    print("No token")