from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from urllib.parse import urlparse
import random

# Spotify API credentials
client_id = ''
client_secret = ''
redirect_uri = 'http://localhost:8888/callback'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope='playlist-modify-public playlist-modify-private playlist-read-private'))

app = Flask(__name__)

# Home page
@app.route('/')
def index():
    return render_template('index.html', status="")

# Route for copying playlist
@app.route('/copy_playlist', methods=['POST'])
def copy_playlist():
    playlist_link = request.form['playlist_link']
    if playlist_link:
        query = urlparse(playlist_link)
        if query.hostname == 'open.spotify.com' and query.path.startswith('/playlist/'):
            # Extract playlist ID from the URL
            playlist_id = query.path.split('/')[2]
            # Fetch playlist information to get the name
            playlist_info = sp.playlist(playlist_id)
            playlist_name = playlist_info['name']
            # Fetch tracks from the playlist
            playlist_items = sp.playlist_items(playlist_id)
            # Extract track URIs from playlist items
            track_uris = [item['track']['uri'] for item in playlist_items['items']]
            # Create a new playlist with the same name as the original playlist
            new_playlist = sp.user_playlist_create(sp.me()['id'], playlist_name, public=False)
            # Add tracks to the new playlist
            sp.playlist_add_items(new_playlist['id'], track_uris)
            return render_template('index.html', status="Playlist copied successfully!", playlists=get_user_playlists())
        else:
            return render_template('index.html', status="Invalid playlist link!")
    else:
        return render_template('index.html', status="Please enter a playlist link!")

@app.route('/shuffle_playlist', methods=['POST'])
def shuffle_playlist_route():
    playlist_link = request.form['playlist_link']
    if playlist_link:
        query = urlparse(playlist_link)
        if query.hostname == 'open.spotify.com' and query.path.startswith('/playlist/'):
            # Extract playlist ID from the URL
            playlist_id = query.path.split('/')[2]
            # Fetch tracks from the playlist
            playlist_items = sp.playlist_items(playlist_id)
            # Extract track URIs from playlist items
            track_uris = [item['track']['uri'] for item in playlist_items['items']]
            # Shuffle the track URIs in place
            random.shuffle(track_uris)
            # Reorder tracks in the playlist with shuffled URIs
            sp.playlist_replace_items(playlist_id, track_uris)
            return "Playlist shuffled successfully!"
        else:
            return "Invalid playlist link!"
    else:
        return "Please enter a playlist link!"

def get_user_playlists():
    playlists = sp.current_user_playlists(limit=50)
    return [playlist['name'] for playlist in playlists['items']]

if __name__ == '__main__':
    app.run(debug=True)
