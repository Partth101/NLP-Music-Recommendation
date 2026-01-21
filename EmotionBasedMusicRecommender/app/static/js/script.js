// static/js/script.js

function displaySpotifyTrack() {
    var emotionInput = document.getElementById('emotion-input');
    var spotifyIframeDiv = document.getElementById('spotify-iframe');
    var recommendationMessage = document.getElementById('recommendation-message');

    if (emotionInput.value.trim() === '') {
        emotionInput.classList.add('empty-input');
        emotionInput.style.borderColor = 'red';
        emotionInput.placeholder = 'This field cannot be empty. Tell us about your day :)';
        recommendationMessage.style.display = 'none';
        spotifyIframeDiv.style.display = 'none';
        return;
    } else {
        fetch('/get_emotion_based_song', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: emotionInput.value.trim() })
        })
        .then(response => response.json())
        .then(data => {
            var trackId = data.track_id;
            var iframeHtml = `<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/${trackId}?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>`;
            spotifyIframeDiv.innerHTML = iframeHtml;
            spotifyIframeDiv.style.display = 'block';
            spotifyIframeDiv.style.opacity = 1;
            recommendationMessage.style.display = 'block';
            recommendationMessage.style.opacity = 1;
        })
        .catch(error => console.error('Error:', error));
    }
}

document.getElementById('emotion-input').addEventListener('focus', function() {
    this.classList.remove('empty-input');
    this.style.borderColor = '';
    this.placeholder = 'How are you feeling today?';
});
