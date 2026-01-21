# Emotion-based Music Recommender

Discover music that matches your mood with the Emotion-based Music Recommender. Express your emotions or describe your day, and let the app recommend the perfect music track based on your feelings.

## How It Works

1. Visit the web application in your browser.

2. Enter your emotions, thoughts, or describe your day in the provided text box.

3. Click the "Submit" button.

4. The app will analyze your input and determine the underlying emotions.

5. You'll receive a personalized Spotify music track recommendation that aligns with your current emotional state.

## Enjoy Music That Resonates

Explore new music genres and artists that match your mood. Whether you're feeling happy, sad, excited, or anything in between, this app helps you find the perfect soundtrack for your emotions.

**Note:** This README provides a high-level overview for end users. Developers can refer to the full documentation for technical details shared below.

# Methodology:
## Emotion Detection Model

We will be using dialogues from all ten seasons of the TV show Friends, renowned for its richness in emotions as our dataset.
Since we scraped the dialogues from the web, the data has a lot of noise and we will be extensively preprocessing it using the insights picked up from HW02.
These dialogues will be labeled with emotions like Happiness, Sadness, Anger, Fear, Surprise, Disgust, Love, Excitement, Anticipation, Contentment, Confusion, Frustration, Nostalgia etc by querying ChatGPT using the open ai api. Each dialogue will be multi-labeled with 2-3 emotions.
Additionally we might consider including posts from subreddits like r/happy, r/sad, and r/angry, following the same labeling process.
Our emotion detection model will be implemented using advanced deep learning neural network architectures, specifically BERT and GPT, to achieve a nuanced understanding of emotion detection.

## Music Database

We will have a self curated Spotify playlist with 250-300 songs, each representing various emotions from our set.
Each song's emotional content will be analyzed based on lyrics, again with the help of ChatGPT, and cataloged in a CSV file with details like song name, emotions, and track ID(Spotify song ID). Each song is expected to be labelled with 3 emotions from our predetermined emotion list.

## User Interface

A simple UI where users can input their current emotional state in the form of a text.
The system will then process this text to identify the underlying emotions by utilizing the emotion detection model which we had trained.
Music Recommendation Process

We will retrieve the song that mapped most closely to the user's text and send the Spotify track ID back to the UI, then this song would be displayed on the UI with the ability to play it.
We still need to consider how we will handle the scenario when two or more songs equally match the user's emotions as we plan to return just a single song to the UI. One thought I have is to return the song which has been played the most number of times among these songs.
