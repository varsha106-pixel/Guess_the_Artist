# imports Spotify client from spotipy library (allows to interact with spotify web API (playlist,user data etc.) )
# use client to retrieve data from Spotify's server
from spotipy import Spotify
# imports SpotifyOAuth from spotipy.oauth2 library which allows the authentication to access a user's account
from spotipy.oauth2 import SpotifyOAuth
# access environment variables (openapi key, spotify client)
import os 
# loads the variables from .env file
from dotenv import load_dotenv
# imports OpenAI client from openai python sdk to interact with chatgpt
from openai import OpenAI
# python module for reading/writing json files 
import json
# loads the variables from the .env file
load_dotenv()

# gets the spotify client id (public identifier for spotify) from the .env file 
client_id = os.getenv("SPOTIPY_CLIENT_ID")

# gets the spotify client secret (password only i know) from the .env file 
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
# gets the spotify redirect url (send them back to this after user logs in, authenticates user, asks for permission for access to playlists and data
# then redirects them to url with authorization code and code can be used to get an access token)
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
# creates an openai client while passing key from .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# creates a spotify client 
# auth_manager=SpotifyOAuth -> handles authorization flow (redirect link)
sp = Spotify(auth_manager=SpotifyOAuth(
    # loads id,secret,redirect uri
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    # sets the scope which allows reading playlists, collaborations but no modification
    # "playlist-read-private" one of Spotify's official built-in OAuth scopes
    scope="playlist-read-private"
))
# Parameter: playlist_url -> user's link to their spotify playlist 
# Method: reads the playlist and songs on it taking the artist name 
def get_artists_from_playlist(playlist_url):
    # splits the url to extract just the playlist id whichis unique and can be used to identify any playlist
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    # uses built in method from spotify api that returns tracks in the form of a dictionary returns at most 100 songs
    # results =
   # {
 #      "items": [ ...track data... ],   # Up to 100 track entries
 #      "next": None,                    # No more pages
 #      "limit": 100,
 #      "offset": 0,
 #          ...
 #   }
    results = sp.playlist_tracks(playlist_id)
    # creates a new dictionary for the artist count/frequency
    artist_count = {}

    # the key "items" holds the tracks iterates through every track
    # each item has a track key that points to the track object which holds the title and artist of the song
    for item in results["items"]:
        #creates variable track for each track
        track = item["track"]
        # happens when track is deleted or region-restricted so data is not there skips this iteraton and moves to next track
        if track is None:
            continue
        #track["artists"] -> list of dictionaries and "artists" is a field in track object
        for artist in track["artists"]:
            # gets the value of name key in dictionary which is the artist name
            name = artist["name"]
            # adds 1 to the artist's count; the dictionary ensures each artist appears only once as a key
            # artist_count.get(name, 0) if artist name is not in dictionary sets the count automatically to 0
            artist_count[name] = artist_count.get(name, 0) + 1
    #returns the dictionary with the updated artist counts
    return artist_count
# Parameters: artist_count -> dictionary retrieved from get_artists_from_playlist method that holds artist names as keys and frequency as values
#             feedback_data -> dictionary holding the number of times an artist has been a favorite
# Method: guesses the favorite artist in playlist based on how often artist is in playlist and 
# how often is has been a favorite from past users 
def guess_favorite_artist(artist_count,feedback_data):
    # checks if input is empty if artist_count is an empty dictionary
    if not artist_count:

        return "No artists found."
    # creates new dictionary for scores
    scores = {}
    # items() groups it into tuples of two iterates through each artist and count by setting artist to the artist name (key) and 
    # count to the frequency (value)
    for artist, count in artist_count.items():
        # gets how often the artist has been the favorite from the dictionary in json file and if artist is not found sets it to 0
        feedback_score = feedback_data.get(artist, 0)
        # sets artist's score to the sum of how often it appears in the playlist and how often it was the favorite
        scores[artist] = count +  feedback_score
    # finds the max value in scores key=scores.get clarifies to compare keys by their value
    favorite_artist = max(scores, key=scores.get)
    #return artist with max score
    return favorite_artist
# Parameters: favorite_artist -> artist name returned by guess_favorite_artist that has the maximum score
#            playlist_url -> user's link to their spotify playlist 
# Method: generates a recommendation of a similar artist to the favorite one that is not in the playlist
def artist_recommendation(favorite_artist,playlist_url):
    # splits the url to retrieve unique playlist id
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
# uses built in method from spotify api that returns tracks in the form of a dictionary returns at most 100 songs
    results = sp.playlist_tracks(playlist_id)
    # creates a list for artists
    artists = []
    # iterates through each item adding each artist name to artists
    for item in results["items"]:
        # gets the track object
        track = item["track"]
        # if the track doesn't exist moves to next iteration
        if track is None:
            continue
        # looks at the dictionary with the artists and sets name to the artists name 
        for artist in track["artists"]:
            name = artist["name"]
            # adds artist name to artists list if not there previously
            if artist not in artists:
                 artists.append(name)
    

    # prompt to chat-gpt asking for a recommendation similar to the favorite artist      
    prompt = f"Given this artist: {favorite_artist}, recommend a new artist with a similar music style that is not in this list: {artists} and give a one sentence summary of how that artist is similar"
    # makes an api call to GPT-4 using openai python sdk
    response = client.chat.completions.create(
        model="gpt-4",
        # the user is providing the chat with a message that is prompt created above
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    # returns the message content from the first response and removes any extra whitespace
    return response.choices[0].message.content.strip()
# Method : loads the artist feedback from .json file
def load_artist_feedback():
    # checks if the file exists in directory
    if os.path.exists("artist_feedback.json"):
        # opens the file in read mode which doesn't allow modification sets open file object to variable f
        with open("artist_feedback.json", "r") as f:
            # reads and parses content of the file
            return json.load(f)
    # if file does not exist returns empty dictionary
    return {}
# Parameter: feedback_data -> dictionary with the data of how often a atrist has been a favorite in .json file
# Method : saves the artist feedback from .json file

def save_artist_feedback(feedback_data):
    # opens file in write mode which creates a file if non-existant or overwrites it if it does sets open file object to variable f
    with open("artist_feedback.json", "w") as f:
        # writes the feedback_data dictionary into the file in JSON format to save across uses
        json.dump(feedback_data, f, indent=2)

def main():
   # takes in input of playlist url from user
    playlist_url = input("Enter your Spotify playlist URL:\n> ")

    artist_count = get_artists_from_playlist(playlist_url)
    # sets variable to data loaded from json file
    feedback_data = load_artist_feedback()

    sorted_artists = sorted(
        # converts artist_count into a list of tuples with artist name and count [("Drake",4),("Sza", 1)]
        artist_count.items(),
        # lambda defines a short function x where for each tuple x the count is added to the frequency from 
        # feedback_data in the .json file to x[0] = artist name x[1] = count
        key=lambda x: x[1] + feedback_data.get(x[0], 0),
        # sorts from highest total score to lowest 
        reverse=True
    )

    guess = guess_favorite_artist(artist_count, feedback_data)
    recommendation = artist_recommendation(guess, playlist_url)
   
# loops through each artist in sorted-artist tuples but _ ignores the second part with the score since only names are necessary
    for artist, _ in sorted_artists:
        
        recommendation = artist_recommendation(artist, playlist_url)
        print(f"\n🤖 Based on your playlist, your favorite artist might be: {artist}. I recommend you check out the {recommendation}!")
        # takes feedback on whether guess was correct
        feedback = input("Was my guess correct? (yes/no)\n> ")
        # if guess is correct the score of the artist in json file goes up by one and loop is ended
        if feedback.lower() == "yes":
            feedback_data[artist] = feedback_data.get(artist, 0) + 1
            print("🤖 Yay! Glad I got it right!")
            break
        else:
            # if guess is incorrect the score in json file goes down by one to update artist is becoming less popular
            feedback_data[artist] = feedback_data.get(artist, 0) - 1
    # if all artists have been guessed and none is correct (loop finishes without a break)
    else:
        print("🤖 Hmm, sorry I couldn't guess your favorite artist accurately.")
    #writes update feedback to json file
    save_artist_feedback(feedback_data)  

   
# only runs if being run directly not imported
if __name__ == "__main__":
    main()


