import pandas as pd
import os
from app import app

def select_best_matching_song(predicted_emotions):
    # Load the songs dataset
    file_path = os.path.join(app.root_path, '..', 'data', 'processed_songs.csv')
    songs_df = pd.read_csv(file_path)

    # Filter songs based on predicted emotions and compute match count
    matching_songs = songs_df.loc[:, predicted_emotions].sum(axis=1)
    songs_df['Matched_Emotions'] = matching_songs

    # Find the maximum matched emotions count
    max_matched_emotions = matching_songs.max()

    # Select songs that match the highest number of predicted emotions
    best_matching_songs = songs_df[songs_df['Matched_Emotions'] == max_matched_emotions]

    # If multiple songs have the same highest `Matched_Emotions`, choose the one with the least `Times_played`
    if len(best_matching_songs) > 1:
        best_matching_songs = best_matching_songs.sort_values(by='Times_played', ascending=True)

    # Select the top song
    top_song = best_matching_songs.iloc[0]

    # Increment the Times_played for the top song
    songs_df.loc[top_song.name, 'Times_played'] += 1

    # Save the updated DataFrame back to the CSV
    songs_df.to_csv(file_path, index=False)

    # Return the track ID of the top song
    return top_song['Track_ID']

