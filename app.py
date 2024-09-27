import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from flask import Flask, request, url_for, session, redirect
import time

# Load the environment variables from .env
load_dotenv()

app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = os.getenv("SECRET_KEY")
TOKEN_INFO = 'token_info'


@app.route("/")
def login():
    # Redirect the user to Spotify for authorization
    spotify_oauth = create_spotify_oauth()
    auth_url = spotify_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/redirect")
def redirect_page():
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code, as_dict=True)

    # Debugging print
    print("Token Info:", token_info)  

    if isinstance(token_info, str):  # Check if token_info is a string
        return f"Error retrieving token: {token_info}"

    # Store token information in session
    session[TOKEN_INFO] = {
        'access_token': token_info['access_token'],
        'refresh_token': token_info['refresh_token'],
        'expires_at': int(time.time()) + token_info['expires_in']
    }
    return redirect(url_for('make_playlist_from_liked_songs', _external=True))


@app.route("/make_playlist")
def make_playlist_from_liked_songs():
    print("Attempting to create playlist...")
    token_info = get_token()

    print("toekn info",token_info)
    if isinstance(token_info, str):  # Check if the redirect to login was invoked
        return redirect(url_for("login"))

    sp = spotipy.Spotify(auth=token_info['access_token'], requests_timeout=10)

    try:
        user_profile = sp.current_user()
        print("user profile",user_profile)
    except spotipy.exceptions.SpotifyException as e:
        print("Error fetching user profile:", e)
        return "Error fetching user profile. Please check your permissions."

    # Proceed to create the playlist
    track_uris = []
    offset = 0
    limit = 50
    while True:
        results = sp.current_user_saved_tracks(limit=limit, offset=offset)
        if not results['items']:
            break
        for item in results['items']:
            track = item['track']
            track_uris.append(track['uri'])
        offset += limit

    user_id = user_profile['id']
    playlist_name = " Personal Playlist"
    new_playlist = sp.user_playlist_create(user_id, playlist_name, public=False)

    if track_uris:
        batch_size = 100
        for i in range(0, len(track_uris), batch_size):
            sp.playlist_add_items(new_playlist['id'], track_uris[i:i+batch_size])

    return "New playlist created"


# Function to create SpotifyOAuth object
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=url_for('redirect_page', _external=True),
        scope='playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-library-modify user-library-read user-read-email user-read-private',
        show_dialog=True 
    )


# Function to retrieve or refresh token
def get_token():
    token_info = session.get(TOKEN_INFO, None)

    if not token_info:
        return redirect(url_for("login"))

    current_time = int(time.time())
    is_expired = token_info['expires_at'] - current_time < 60

    if is_expired:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = {
            'access_token': token_info['access_token'],
            'refresh_token': token_info['refresh_token'],
            'expires_at': int(time.time()) + token_info['expires_in']
        }

    return session.get(TOKEN_INFO)


if __name__ == "__main__":
    app.run(debug=True)
