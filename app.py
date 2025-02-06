from flask import Flask, jsonify, request, redirect, session
import requests
import os
from urllib.parse import urlencode

app = Flask(__name__, static_folder="static", static_url_path="")

app.secret_key = os.urandom(24)  # Genererer en tilfeldig session-nøkkel

# 🔑 Spotify API Credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# 🔹 Spotify API URLs
TOKEN_URL = "https://accounts.spotify.com/api/token"
CURRENTLY_PLAYING_URL = "https://api.spotify.com/v1/me/player/currently-playing"

# 🔹 Scopes (gir tilgang til å hente sanginfo)
SCOPE = "user-read-playback-state user-read-currently-playing"

# 🔹 Sangtekster for utvalgte sanger
SONG_TEXTS = {
    "Piano": "Big hit from 2006 with Norways beloved Karpe (Formerly Karpe Diem)",
    "Goofy 2018": "🎆 Party anthem of the decade! The song from my very own russebuss. We got more then 3 million plays",
    "Sjeiken 2015": "💃 The biggest russe-song of all time! Funfact: In 2011 a russebuss got Skrillex to make them a song. -Disco Rangers 2011",
    "Linje1": "🎶 A russesong for those who did not have their own bus and had to take the subway",
    "Gunerius": "🎤 A wonderful cover version of one of Karpe's biggest hits",
    "Optimist": "🎸 Jan Teigen (RIP) did attend the Norwegian Euroviosion 14 times. He is known for his skeleton-suit",
    "Spis din syvende sans" : "⚡ Yet another hit from Karpe. Funfact: Magdi from Karpe lives in Nittedal, Birk and Camillas homwtown",
    "Her kommer vinteren": "Jokke was a famous rockstar in the 90s and died like one too. A lot of drugs. The song is about him watching tv durinmg the whole winter",
    "Jenter": " Di Derre's vocalist is also Norways most famous Author, Jo Nesbø",
    "Hjerteknuser": "Truly one of Norways best bands. Kaizers Orchestra. Funfact: several people from around the world has learned Norwegian just so they can understand their lyrics. Such a shame that not even Norwegians can understand what they say",
    "Pstereo": "Emilie Nicolas is great! She used to be me and Camillas neighbour. She NEVER had her dog on a leash",
    "Du fortenar ein som meg": "Big hit from 2015. Every woman over 40 had a crush on this guy. Not heard much from him since",
    "Fy faen": "Translates to 'oh fuck'. Big hit from a couple years ago. Catchy, but not great",
    "PAF.no": "Yet another great song from Norways pride and joy, Karpe.",
    "Barcelona": "This song was played live at Norway Cup (A childrens football event) in 2005. The lead singer screamed to the kids from stage 'Drugs are better than football'",
    "Fredag": "Norway has soooo many songs about Friday. Is this normal?",
    "Traktor": "In Norway we have a 2 social classes People from Østfold and everyone else. These guys are from Østfold and they like tractors",
    "E-Ore": "A rap duo that was big in the 2000s. One of the guys is now a Professor in law",
    "Kursiv": "Translates to 'italics'. Funfact: A friend of my dads took this picture. Funfact2: When I was a kid, I had such a hard time determining if the kid on the cover was a boy or a girl. I guess that doesnt matter anymore, but what do you guys think?",
    "Mysteriet deg": "One of Norways biggest artist of all time. Funfact: He is a priest and drive a helicopter. Kinda GOAT-energy",
    "Glir forbi": "This was a seroius hit in 2009. The song is about how the singer sees all of his friends in seroius jobs, having families and driving nice cars while he is stuck. I guess non of you doctors can relate",
    "Øynene lukket" : "I dont have much to say about this song. Funfact: The singer is my step moms ex boyfriend. ",
    "Lensome Traveller" : "In my opinion, this song is about 30 seconds too long. Its cool though",
    "Surfbrett" : "This song is about making a surfboard with plywood",
    "Cmon talk" : "This guy was a real one hit wonder. He made a couple songs, went to The Ellen Show, and now he is gone. Funfact: He is born and raised in Nittedal, mine and Camillas hometown",
    "Cut To Black" : "This song is Norwegian, even though their name sounds very french. They got the name from the Belgian genius Georges Lemaître. The man behind the big bang theory",
    "Do It Again" : "Røyksopp is such a cool and unique band. I am kinda proud that they are Norwegian",
    "Eple" : "Their biggest hit and one of the greatest songs of all time in my opinion. Funfact: Eple translates to Apple. I guess that is kinda obvious",
    "Kvelertak" : "In my opnion the greatest Norwegian band of all time. This is their biggest hit. Kinda weird the have a song that is called the same as the band.",
    "Die For You" : "Made by the Norwegian guy Cashmere Cat. He is a veeery weird guy, but very talented as a producer and DJ",
    "Dance, Baby!" :"I dont know much about this guy, but yihaaaa this song is great",
    "Feeling Lonely" : "Have Camilla told you guys about our dog yet? He is kinda the best dog.",
    "i wanna be your girlfriend" : "Girl in red is one of our biggest artists right now. ",
    "Mad" : "This is my good riend David's Band's newest song, so I feel like I had to promote it. I am hoping that the band will accept me as their manager some day.",
    "Wild Bird" : "The guy behind this band, Øystein Greni, was a professional skater until he broke his knee. Then he started this band.",
    "Enhjørning" : "Translates to 'Unicorn'. What this lyrics is about is very hard to understand, but it is definitely not about a unicorn",
    "Am I Wrong" : "This was such a big it that the guys bought the house next to Kim Kardashians house. The last I heard is that they are now voice actors for movies. I wonder how long they can keep that house",
    "The Fox" : "I felt like I had to bring in this stupid song. ",
    "Irreplaceable" : "I know, I know. Beyonce is not Norwegian, but the song is written and produced by the Norwegian duo Stargate",
    "Don't Stop The Music" : "Relaaax, Rihanna is not Norwegian, but the song was written and produced by the Norwegian duo Stargate",
    
    }

### **🏠 Hjemmeside (viser index.html)**
@app.route("/")
def home():
    return app.send_static_file("index.html")


### 1️⃣ **Login route (Spotify OAuth)**
@app.route("/login")
def login():
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    })
    return redirect(auth_url)


### 2️⃣ **Callback route (henter Access Token)**
@app.route("/callback")
def callback():
    code = request.args.get("code")
    
    if not code:
        return "No code provided", 400

    # 🔹 Be om Access Token fra Spotify
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(TOKEN_URL, data=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        session["access_token"] = data["access_token"]  # 🔑 Lagre token i session
        print("✅ ACCESS TOKEN:", session["access_token"])  # Logg token for debugging
        return redirect("/current-song")
    else:
        return "Failed to authenticate", 400


### 3️⃣ **Hente nåværende sang + tekst**
@app.route("/current-song")
def current_song():
    access_token = session.get("access_token")  # 🔑 Hent token fra session

    if not access_token:
        return redirect("/login")  # 🔄 Automatisk send til login

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(CURRENTLY_PLAYING_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        song_name = data["item"]["name"]
        artist_name = data["item"]["artists"][0]["name"]
        album_image = data["item"]["album"]["images"][0]["url"]

        # 🔹 Sjekk om sangen finnes i listen over tekster
        song_text = SONG_TEXTS.get(song_name, "")

        return jsonify({
            "song": song_name,
            "artist": artist_name,
            "image": album_image,
            "text": song_text  # 🔥 Legg til tekst i responsen
        })
    else:
        return jsonify({"error": "No song playing"}), 200


### **4️⃣ Start Flask-serveren**
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
