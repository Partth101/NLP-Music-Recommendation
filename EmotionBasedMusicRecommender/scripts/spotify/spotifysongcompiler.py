import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from credentials import APIKeys
import pandas as pd

client_id = APIKeys.get_client_id()
client_secret = APIKeys.get_client_secret()

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

redirect_uri = 'http://localhost:8891/callback'
playlist_id = '54FWKfSRIHnwkq0trEyT5h'  # Your playlist ID

# Set up authorization
scope = "playlist-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))

# Fetch tracks from the playlist
results = sp.playlist_tracks(playlist_id)
tracks = results['items']

# If the playlist is large, paginate through the results
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

# Initialize a list to hold your data
data = []

# Iterate over tracks and collect data
for idx, item in enumerate(tracks):
    track = item.get('track')
    if track is None:
        print(f"Track {idx+1} is unavailable or missing data.")
        continue  # Skip this iteration if track is None

    # Extract the required information
    track_name = track['name']
    artist_names = ', '.join(artist['name'] for artist in track['artists'])
    artist_id = track['album']['artists'][0]['id'] if track['album']['artists'] else None
    track_id = track['id']

    # Append to the data list
    data.append({'Song Name': track_name, 'Artists': artist_names, 'Artist_ID': artist_id, 'Track_ID': track_id})

# Create DataFrame
df = pd.DataFrame(data)

# The file is stored in the data directory
df.to_csv('data/songs.csv', index=False)
