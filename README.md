# Guess the Artist – AI-Powered Music Taste Detector

Guess the Artist is a simple AI agent that uses the Spotify and OpenAI APIs to analyze a user's playlist and guess their favorite artist. It also recommends a similar artist not in the playlist. The agent learns over time based on user feedback, mimicking a basic reinforcement learning mechanism.

**How It Works**

User provides a Spotify playlist link.
Spotify API is used to extract artist data from the playlist.
The agent uses frequency of artist appearances and historical feedback to make a guess.
It then provides a recommendation for a similar artist using OpenAI’s GPT model.
The user gives feedback ("yes"/"no") on if the artist is the favorite and the agent adjusts its scores accordingly.
Agent continues to guess until user affirms guess is the favorite or it has guessed all available artists in playlist.
Feedback is saved in a local artist_feedback.json file for future learning.

**Technologies Used:**

Python
Spotify Web API via Spotipy
OpenAI API for GPT-based recommendations
JSON for persistent feedback tracking
dotenv for secure API key management

**Setup Instructions**

Clone the Repository

git clone https://github.com/YOUR_USERNAME/guess-the-artist

cd guess-the-artist

Install Dependencies

pip install spotipy openai python-dotenv

Create .env file

SPOTIPY_CLIENT_ID=your_spotify_client_id

SPOTIPY_CLIENT_SECRET=your_spotify_client_secret

SPOTIPY_REDIRECT_URI=http://localhost:8888/callback

OPENAI_API_KEY=your_openai_api_key

**Run the App**

Command-Line Application 
python main.py
Enter your Spotify playlist URL:
    Input playlist url
Example Output

🤖 Based on your playlist, your favorite artist might be: Taylor Swift.
I recommend you check out the artist: Phoebe Bridgers!

Was my guess correct? (yes/no)
> yes

🤖 Yay! Glad I got it right!

**Project Structure**

main.py                           # Main script

artist_feedback.json              # Stores learning feedback

.env                              # Your API keys (not tracked)

README.md                         # Project documentation

**Learning Mechanism**

If the agent guesses artist correctly: artist_score += 1

If the guess is incorrect: artist_score -= 1

These scores influence future guesses using weighted sorting along with the frequency of the artist in the playlist.

total_score = artist_score + frequency

**Notes**

Your playlist must be public or shared with proper permissions for the API to access.
The app doesn't use a database – it stores feedback locally in JSON.

**License**

This project is for educational and non-commercial use.

