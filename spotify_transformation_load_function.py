import json
import boto3
from typing import Dict, List
import pandas as pd
from datetime import datetime
from io import StringIO 

def album_data(data: Dict) -> List[Dict]:
    """Extract album data from playlist tracks."""
    album_list = []
    for row in data["items"]:
        album = row["track"]["album"]
        album_element = {
            "album_id": album["id"],
            "name": album["name"],
            "release_date": album["release_date"],
            "total_tracks": album["total_tracks"],
            "url": album["external_urls"]["spotify"]
        }
        album_list.append(album_element)
    return album_list

def artist_data(data: Dict) -> List[Dict]:
    """Extract artist data from playlist tracks."""
    artist_list = []
    for row in data['items']:
        track = row.get("track", {})
        for artist in track.get('artists', []):
            artist_dict = {
                'artist_id': artist['id'],
                'artist_name': artist['name'],
                'external_url': artist['href']
            }
            artist_list.append(artist_dict)
    return artist_list

def song_data(data: Dict) -> List[Dict]:
    """Extract song data from playlist tracks."""
    song_list = []
    for row in data['items']:
        track = row["track"]
        song_element = {
            'song_id': track['id'],
            'song_name': track['name'],
            'duration_ms': track['duration_ms'],
            'url': track['external_urls']['spotify'],
            'popularity': track['popularity'],
            'song_added': row['added_at'],
            'album_id': track['album']['id'],
            'artist_id': track['album']['artists'][0]['id']
        }
        song_list.append(song_element)
    return song_list

def create_dataframe(data: List[Dict], drop_duplicates_col: str = None) -> pd.DataFrame:
    """Convert a list of dictionaries to a DataFrame, optionally dropping duplicates."""
    df = pd.DataFrame.from_dict(data)
    if drop_duplicates_col:
        df = df.drop_duplicates(subset=[drop_duplicates_col])
    return df

def process_dates(df: pd.DataFrame, date_cols: List[str]) -> pd.DataFrame:
    """Convert specified columns to datetime format."""
    for col in date_cols:
        df[col] = pd.to_datetime(df[col])
    return df

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    Bucket = 'spotify-etl-project-gnavarrolema'
    Key = 'raw_data/to-be-processed/'

    spotify_data = []
    spotify_keys = []
    for file in s3.list_objects(Bucket=Bucket, Prefix=Key)['Contents']:
        file_key = file['Key']
        if file_key.split('.')[-1] == 'json':
            response = s3.get_object(Bucket=Bucket, Key=file_key)
            content = response['Body']
            json_object = json.loads(content.read())
            spotify_data.append(json_object)
            spotify_keys.append(file_key)
    
    for data in spotify_data:
        album_list = album_data(data)
        artist_list = artist_data(data)
        song_list = song_data(data)

        album_df = create_dataframe(album_list, drop_duplicates_col='album_id')
        artist_df = create_dataframe(artist_list, drop_duplicates_col='artist_id')
        song_df = create_dataframe(song_list)

        album_df = process_dates(album_df, ['release_date'])
        song_df = process_dates(song_df, ['song_added'])

        song_key = 'transformed_data/songs_data/songs_transformed_' + str(datetime.now()) + '.csv'
        song_buffer = StringIO()
        song_df.to_csv(song_buffer, index=False)
        song_content = song_buffer.getvalue()  
        s3.put_object(Bucket=Bucket, Key=song_key, Body=song_content)

        album_key = 'transformed_data/album_data/album_transformed_' + str(datetime.now()) + '.csv'
        album_buffer = StringIO()
        album_df.to_csv(album_buffer, index=False)
        album_content = album_buffer.getvalue()  
        s3.put_object(Bucket=Bucket, Key=album_key, Body=album_content)

        artist_key = 'transformed_data/artist_data/artist_transformed_' + str(datetime.now()) + '.csv'
        artist_buffer = StringIO()
        artist_df.to_csv(artist_buffer, index=False)
        artist_content = artist_buffer.getvalue()  
        s3.put_object(Bucket=Bucket, Key=artist_key, Body=artist_content)

    s3_resource = boto3.resource('s3')
    for key in spotify_keys:
        copy_source = {
            'Bucket': Bucket,
            'Key' : key
        }
        s3_resource.meta.client.copy(copy_source, Bucket, 'raw_data/processed/' + key.split('/')[-1])
        s3_resource.Object(Bucket, key).delete()        
