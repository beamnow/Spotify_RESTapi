from concurrent.futures import thread
from operator import methodcaller
from flask import Flask, request, json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from keyfile import client_id, client_secret

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
app = Flask(__name__)

def on_json_loading_failed_return_dict(e):
    return {}

def get_search(sp, search):
    #return type : dict
    result = sp.search(search,type='track')
    search_dict = {
        "artist_id" : [],
        "artist_name" : [], 
        "tracks_id" : [], 
        "tracks_name":[], 
        "tracks_image":[]
    };

    for i in range(len(result['tracks']["items"])):
        search_dict["artist_id"].append(result["tracks"]["items"][i]["artists"][0]["id"])
        search_dict["artist_name"].append(result['tracks']['items'][i]['artists'][0]['name']) 
        search_dict["tracks_id"].append(result['tracks']['items'][i]['id'])
        search_dict["tracks_name"].append(result['tracks']['items'][i]['name'])
        search_dict["tracks_image"].append(result['tracks']['items'][i]['album']['images'][0]['url'])

    return search_dict

def get_song_recommen (sp, artist_id, artist_name, track_id):
    # return type : dict

    result = sp.search(artist_name, type='track')
    track = result['tracks']['items'][0]
    for i in range(len(result['tracks']['items'])):
        artist_search = result["tracks"]["items"][i]["artists"][0]["id"]
        if artist_search == artist_id :
            artist = sp.artist(track["artists"][0]["external_urls"]["spotify"])
            genre = artist["genres"]
            if genre==None :
                genre = ''
        break
    genre = ''.join(map(str, genre))

    # recommendations
    rec = sp.recommendations(seed_artists=[artist_id], seed_genres=[genre], seed_tracks=[track_id], limit=3)
    rec_dict = {
        "artist_name" : [],
        "artist_id":[],  
        "tracks_name":[], 
        "tracks_id":[],
        "tracks_image":[], 
        "tracks_prev":[]
    };
    
    for track in rec['tracks']:
        rec_dict["artist_name"].append(track['artists'][0]['name'])
        rec_dict["artist_id"].append(track['artists'][0]['id'])
        rec_dict["tracks_name"].append(track['name'])
        rec_dict["tracks_id"].append(track['id'])
        rec_dict["tracks_image"].append(track['album']['images'][0]['url'])
        rec_dict["tracks_prev"].append(track['preview_url'])
        if(rec_dict["tracks_prev"] == None):
            rec_dict["tracks_prev"] = ""

    return rec_dict
        
@app.route('/') # basic
def main_get():
    return 'Hello World!'

# 음악 검색 GET, POST
@app.route('/search', methods=['GET', 'POST'])
def search():
    search_for = request.json
    search_for = search_for['search'] # BODY에 들어갈 내용 { "search" : "검색어 " }
    request.on_json_loading_failed = on_json_loading_failed_return_dict # 예외처리
    search_result = get_search(sp=sp, search=search_for) # 검색함수

    #검색결과(가수이름, 노래제목, 앨범아트)
    jsonString = json.dumps(search_result, default=str, indent=5, sort_keys = True)
    return jsonString

# 음악 추천
@app.route('/recommend', methods=['GET','POST'])
def recommend():
    Bookmark = request.json # BODY { "artist_id" : "아티스트id", "artist_name" : "아티스트이름", "track_id" : "트랙id" }
    request.on_json_loading_failed = on_json_loading_failed_return_dict # 예외 처리
    artist_id = Bookmark['artist_id']
    artist_name = Bookmark['artist_name']
    track_id = Bookmark['track_id']

    recommend_song = get_song_recommen(sp=sp, artist_id=artist_id, artist_name=artist_name, track_id=track_id)
    recommend_song = json.dumps(recommend_song, default=str, indent=5, sort_keys = True)
    return recommend_song

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0', port=80)
