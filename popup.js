document
  .getElementById("fetch-liked-songs")
  .addEventListener("click", async () => {
    const response = await fetch("http://127.0.0.1:5000/get_liked_songs"); // Flask endpoint for liked songs
    const likedSongs = await response.json();
    displayLikedSongs(likedSongs);
  });

function displayLikedSongs(songs) {
  const likedSongsDiv = document.getElementById("liked-songs");
  likedSongsDiv.innerHTML = ""; // Clear previous songs
  songs.forEach((song) => {
    const songElement = document.createElement("div");
    songElement.textContent = song.name; // Adjust as per your song object structure
    likedSongsDiv.appendChild(songElement);
  });
  document.getElementById("create-playlist").style.display = "block"; // Show create playlist button
}

document
  .getElementById("create-playlist")
  .addEventListener("click", async () => {
    const songs = []; // Gather song IDs or URIs from displayed liked songs
    const response = await fetch("http://127.0.0.1:5000/create_playlist", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ songs }),
    });

    if (response.ok) {
      alert("Playlist created successfully!");
    } else {
      alert("Failed to create playlist.");
    }
  });
