### TheMovieDb ###  Does movies but also series, for which i call it tsdb in metadata id ##
# tt0412142   1408  House md   http://www.omdbapi.com/?i=tt0412142 tvdb 73255
# tt0186151  10559  Frequency  http://www.omdbapi.com/?i=tt0186151
# tt5311514         Your Name
#TMDB_SEARCH_BY_IMDBID       = "https://api.TheMovieDb.org/3/find/tt0412142?api_key=7f4a0bd0bd3315bb832e17feda70b5cd&external_source=imdb_id"

### Imports ###
import common
from   common import SaveDict, Dict, Log, DictString
import os
### Variables ###  Accessible in this module (others if 'from MyAnimeList import xxx', or 'import MyAnimeList.py' calling them with 'MyAnimeList.Variable_name'
  
### ###
def GetMetadata (media, movie, TVDBid, TMDbid, IMDbid):
  Log.Info("=== TheMovieDb.GetMetadata() ===".ljust(157, '='))
  TMDB_MOVIE_SEARCH_BY_TMDBID = 'http://api.tmdb.org/3/movie/%s?api_key=7f4a0bd0bd3315bb832e17feda70b5cd&append_to_response=releases,credits,trailers,external_ids&language=en'  #Work with IMDbid
  TMDB_SERIE_SEARCH_BY_TVDBID = "http://api.TheMovieDb.org/3/find/%s?api_key=7f4a0bd0bd3315bb832e17feda70b5cd&external_source=tvdb_id&append_to_response=releases,credits,trailers,external_ids&language=en"
  TMDB_CONFIG_URL             = 'http://api.tmdb.org/3/configuration?api_key=7f4a0bd0bd3315bb832e17feda70b5cd'
  #TMDB_MOVIE_GENRE_LIST       = "https://api.TheMovieDb.org/3/genre/movie/list?api_key=7f4a0bd0bd3315bb832e17feda70b5cd&language=en-US"
  #TMDB_SERIE_GENRE_LIST       = "https://api.TheMovieDb.org/3/genre/tv/list?api_key=7f4a0bd0bd3315bb832e17feda70b5cd&language=en-US"
  TheMovieDb_dict = {}
  TSDbid          = ""
  
  Log.Info("TVDBid: '{}', TMDbid: '{}', IMDbid: '{}'".format(TVDBid, TMDbid, IMDbid))
  if   TMDbid:            url, filename = TMDB_MOVIE_SEARCH_BY_TMDBID % TMDbid, "TMDB-"+TMDbid+".json"
  elif IMDbid:            url, filename = TMDB_MOVIE_SEARCH_BY_TMDBID % IMDbid, "IMDb-"+IMDbid+".json"
  elif TVDBid.isdigit():  url, filename = TMDB_SERIE_SEARCH_BY_TVDBID % TVDBid, "TVDB-"+TVDBid+".json"
  else:                   return TheMovieDb_dict, TSDbid, TMDbid, IMDbid
  
  mode        = "movie" if movie else "tv"
  Log.Info(("--- %s ---" % mode).ljust(157, '-'))
  json        = common.LoadFile(filename=filename,               relativeDirectory=os.path.join('TheMovieDb', 'json'), url=url,             cache=CACHE_1WEEK)
  config_dict = common.LoadFile(filename="TMDB_CONFIG_URL.json", relativeDirectory="TheMovieDb",                       url=TMDB_CONFIG_URL, cache=CACHE_1DAY *30)
  if not json:  Log.Info("TMDB - url: failed to get json" + TMDB_MOVIE_SEARCH_BY_TMDBID % TMDbid)
  else:  
    if   'tv_results'    in json and json['tv_results'   ]:  json, mode = json['tv_results'   ][0], "tv"
    elif 'movie_results' in json and json['movie_results']:  json, mode = json['movie_results'][0], "movie"
    
    Log.Info("[ ] title: {}"                  .format(SaveDict( Dict(json, 'title' if mode=="movie" else 'name'), TheMovieDb_dict, 'title'                  )))
    Log.Info("[ ] rating: {}"                 .format(SaveDict( Dict(json, 'vote_average'),                       TheMovieDb_dict, 'rating'                 )))  #if 'vote_count' in json and json['vote_count'] > 3:  SaveDict( Dict(json, 'vote_average'), TheMovieDb_dict, 'rating')
    Log.Info("[ ] tagline: {}"                .format(SaveDict( Dict(json, 'tagline'),                            TheMovieDb_dict, 'tagline'                )))
    Log.Info("[ ] summary: {}"                .format(SaveDict( Dict(json, 'overview'),                           TheMovieDb_dict, 'summary'                )))
    Log.Info("[ ] duration: {}"               .format(SaveDict( Dict(json, 'runtime'),                            TheMovieDb_dict, 'duration'               )))
    Log.Info("[ ] countries: {}"              .format(SaveDict( Dict(json, 'origin_country'),                     TheMovieDb_dict, 'countries'              )))
    Log.Info("[ ] originally_available_at: {}".format(SaveDict( Dict(json, 'first_air_date'),                     TheMovieDb_dict, 'originally_available_at')))
    if Dict(json, 'belongs_to_collection', 'name'):  Log.Info("[ ] collections: {}".format(SaveDict( [ Dict(json, 'belongs_to_collection', 'name')],                          TheMovieDb_dict, 'collections')))
    if Dict(json, 'genres'                       ):  Log.Info("[ ] genres: {}"     .format(SaveDict( sorted([ Dict(genre, 'name') for genre in Dict(json, 'genres') or [] ]), TheMovieDb_dict, 'genres'     )))
    if Dict(json, 'poster_path'                  ):  TheMovieDb_dict['posters'] = { config_dict['images']['base_url']+'original'+json['poster_path'  ]: (os.path.join('TheMovieDb', 'poster',  json['poster_path'  ].lstrip('/')), 90, None)}
    if Dict(json, 'backdrop_path'                ):  TheMovieDb_dict['art'    ] = { config_dict['images']['base_url']+'original'+json['backdrop_path']: (os.path.join('TheMovieDb', 'artwork', json['backdrop_path'].lstrip('/')), 90, config_dict['images']['base_url']+'w300'+json['backdrop_path']) }
    try:     Log.Info("[ ] duration: {}".format(SaveDict( int(Dict(json, 'duration')) * 60 * 1000,  TheMovieDb_dict, 'duration')))
    except:  pass
    if mode=='tv':   TSDbid = str(Dict(json, 'id'))
    elif not TMDbid: TMDbid = str(Dict(json, 'id'))
    if not IMDbid:   IMDbid = Dict(json, 'imdb_id')
    
    for studio in Dict(json, 'production_companies') or []:
      if studio['id'] <= json['production_companies'][0]['id']:
        Log.Info("[ ] studio: {}".format(SaveDict( studio['name'].strip(), TheMovieDb_dict, 'studio')))
  
  ### More pictures ###
  Log.Info("--- pictures.more ---".ljust(157, '-'))
  Log.Info("TMDbid: '{}', TSDbid: '{}', IMDbid: '{}'".format(TMDbid, TSDbid, IMDbid))
  for id in IMDbid.split(',') if ',' in IMDbid else []:
    TMDB_MOVIE_IMAGES_URL = 'https://api.tmdb.org/3/{mode}/{id}/images?api_key=7f4a0bd0bd3315bb832e17feda70b5cd'
    json                  = common.LoadFile(filename="TMDB-"+(IMDbid or TMDbid)+".json", relativeDirectory="TMDB", url=TMDB_MOVIE_IMAGES_URL.format(id=id, mode=mode), cache=CACHE_1WEEK)
    for index, poster in enumerate(Dict(json, 'posters') or []):
      if Dict(poster, 'file_path'):    Log.Info("[ ] poster: {}" .format(SaveDict((os.path.join('TheMovieDb', 'poster', "%s-%s.jpg" % (TMDbid, index)), 40, None), TheMovieDb_dict, 'posters', config_dict['images']['base_url'] + 'original' + poster['file_path'])))
    for index, backdrop in enumerate(Dict(json, 'backdrops') or []):
      if Dict(backdrop, 'file_path'):  Log.Info("[ ] artwork: {}".format(SaveDict((os.path.join('TheMovieDb', 'artwork', "%s-%s-art.jpg" % (TMDbid, index)), 40, config_dict['images']['base_url'] + 'w300'+ backdrop['file_path']), TheMovieDb_dict, 'art', config_dict['images']['base_url']+'original'+ backdrop['file_path'])))
  
  Log.Info("--- return ---".ljust(157, '-'))
  Log.Info("TheMovieDb_dict: {}".format(DictString(TheMovieDb_dict, 4)))
  return TheMovieDb_dict, TSDbid, TMDbid, IMDbid

### TMDB movie search ###
def Search(results, media, lang, manual, movie):
  Log.Info("=== TheMovieDb.Search() ===".ljust(157, '='))
  #'Uchiage Hanabi, Shita kara Miru ka？ Yoko kara Miru ka？ 打ち上げ花火、下から見るか？横から見るか？' Failed with: TypeError: not all arguments converted during string formatting
  #Fixed with:tmdb_url = TMDB_MOVIE_SEARCH.format(String.Quote(orig_title)) Log.Info("TMDB - url: " + tmdb_url) try: json = JSON.ObjectFromURL(tmdb_url, sleep=2.0, headers={'Accept': 'application/json'}, cacheTime=CACHE_1WEEK * 2) except Exception as e: Log.Error("get_json - Error fetching JSON page '%s', Exception: '%s'" % (tmdb_url, e) )
  TMDB_MOVIE_SEARCH = 'http://api.tmdb.org/3/search/movie?api_key=7f4a0bd0bd3315bb832e17feda70b5cd&query={}&year=&language=en&include_adult=true'
  orig_title = String.Quote(media.name if manual and movie else media.title if movie else media.show)
  maxi = 0
  
  Log.Info("TMDB  - url: " + TMDB_MOVIE_SEARCH.format(orig_title))
  try:                    json = JSON.ObjectFromURL(TMDB_MOVIE_SEARCH.format(orig_title), sleep=2.0, headers={'Accept': 'application/json'}, cacheTime=CACHE_1WEEK * 2)
  except Exception as e:  Log.Error("get_json - Error fetching JSON page '%s', Exception: '%s'" %( TMDB_MOVIE_SEARCH % orig_title, e)) # json   = common.get_json(TMDB_MOVIE_SEARCH % orig_title, cache_time=CACHE_1WEEK * 2)
  else:
    if isinstance(json, dict) and 'results' in json:
      for movie in json['results']:
        a, b  = orig_title, movie['title'].encode('utf-8')
        score = 100 - 100*Util.LevenshteinDistance(a,b) / max(len(a),len(b)) if a!=b else 100
        if maxi<score:  maxi = score
        Log.Info("TMDB  - score: '%3d', id: '%6s', title: '%s'" % (score, movie['id'],  movie['title']) )
        results.Append(MetadataSearchResult(id="tmdb-"+str(movie['id']), name="{} [{}-{}]".format(movie['title'], "tmdb", movie['id']), year=None, lang=lang, score=score) )
        if '' in movie and movie['adult']!="null":  Log.Info("adult: '{}'".format(movie['adult']))
  return maxi
### Trailers (Movie Library Only) ###
### For when youtube mp4 url can be gotten again
'''
  YOUTUBE_VIDEO_DETAILS = 'https://m.youtube.com/watch?ajax=1&v=%s'
  TYPE_MAP =  { 'primary_trailer'   : TrailerObject,          'trailer'           : TrailerObject,       'interview'         : InterviewObject,
                'behind_the_scenes' : BehindTheScenesObject,  'scene_or_sample'   : SceneOrSampleObject
              }  #https://github.com/plexinc-agents/PlexMovie.bundle/blob/master/Contents/Code/__init__.py
  #metadata.extras.add(Trailer(title=title, file=os.path.join(folder_path, f)))  #https://github.com/gboudreau/XBMCnfoMoviesImporter.bundle/blob/master/Contents/Code/__init__.py
  extras = []
  if movie:  # https://github.com/sander1/YouTube-Agent.bundle/blob/master/Contents/Code/__init__.py
    if 'trailers' in json and json['trailers']:
      if "quicktime" in json['trailers'] and json['trailers']["quicktime"]:
        for trailer in json['trailers']["quicktime"]:
          Log.Info("Trailer detected: " + str (json['trailers']["quicktime"]))
          #metadata.extras.add( TrailerObject(url = "???"+trailer["source"]), title = trailer["name"], thumb = None) )
      if "youtube" in json['trailers'] and json['trailers']["youtube"]:
        for trailer in json['trailers']["youtube"]:
          Log.Info("Trailer detected: name: '%s', size: '%s', source: '%s', type: '%s', link: '%s'" % (trailer["name"], trailer["size"], trailer["source"], trailer["type"], "https://www.youtube.com/watch?v="+trailer["source"]))
          json_obj = None
          try:     json_obj = JSON.ObjectFromString( HTTP.Request(YOUTUBE_VIDEO_DETAILS % trailer["source"]).content[4:] )['content']
          except:  Log("TheMovieDb.GetMetadata() - Trailers - Could not retrieve data from YouTube for: '%s'" % trailer["source"])
          if json_obj:
            Log.Info("TheMovieDb.GetMetadata() - Trailers - json_obj: '%s'" % str(json_obj))
            #metadata.extras.add( TrailerObject(url = "https://www.youtube.com/watch?v="+trailer["source"]), title = json_obj['video']['title'], thumb = 'https://%s' % (json_obj['video']['thumbnail_for_watch'].split('//')[-1])) )
            #metadata.extras.add( TrailerObject(url = "https://www.youtube.com/watch?v="+trailer["source"]), title = json_obj['video']['title'], thumb = Proxy.Preview(HTTP.Request('https://%s' % (json_obj['video']['thumbnail_for_watch'].split('//')[-1])  ).content, sort_order=1))
            metadata.extras.add(TrailerObject(url                     = "https://www.youtube.com/watch?v="+trailer["source"],
                                              title                   = json_obj['video']['title'],
                                              #year                    = avail.year,
                                              #originally_available_at = avail,
                                              thumb                   = 'https://%s' % (json_obj['video']['thumbnail_for_watch'].split('//')[-1]) if 'thumbnail_for_watch' in json_obj['video'] else None
                                             )
                               )
            #metadata.title                   = json_obj['video']['title']
            #metadata.duration                = json_obj['video']['length_seconds'] * 1000
            #thumb                            = 'https://%s' % (json_obj['video']['thumbnail_for_watch'].split('//')[-1])
            #metadata.posters[thumb]          = Proxy.Preview(HTTP.Request(thumb).content, sort_order=1)
            #metadata.summary                 = json_obj['video_main_content']['contents'][0]['description']['runs'][0]['text']
            #date                             = Datetime.ParseDate(json_obj['video_main_content']['contents'][0]['date_text']['runs'][0]['text'].split('Published on ')[-1])
            #metadata.originally_available_at = date.date()
            #metadata.year                    = date.year
            # Add YouTube user as director
             #metadata.directors.clear()
            #if Prefs['add_user_as_director']:
            #  meta_director = metadata.directors.new()
            #  meta_director.name  = json_obj['video_main_content']['contents'][0]['short_byline_text']['runs'][0]['text']
            #  meta_director.photo = json_obj['video_main_content']['contents'][0]['thumbnail']['url'].replace('/s88-', '/s512-')
            #	
  '''
  