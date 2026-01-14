document.addEventListener("DOMContentLoaded", () => {
    const authSection = document.getElementById("auth-section");
    const appSection = document.getElementById("app-section");
    const loginForm = document.getElementById("login-form"); // Added this line
    const registerForm = document.getElementById("register-form"); // Added this line
    const loginContainer = document.getElementById("login-container");
    const registerContainer = document.getElementById("register-container");
    const showRegisterLink = document.getElementById("show-register-link");
    const showLoginLink = document.getElementById("show-login-link");
    const logoutBtn = document.getElementById("logout-btn");
    const themeSwitcher = document.getElementById("theme-switcher");

    const searchForm = document.getElementById("search-form");
    const searchResults = document.getElementById("search-results");
    const mySubscriptionsSection = document.getElementById("my-subscriptions");

    // Episode Modal Elements
    const episodeModal = new bootstrap.Modal(document.getElementById('episodeModal'));
    const modalPodcastTitle = document.getElementById('modal-podcast-title');
    const episodeList = document.getElementById('episode-list');
    const episodeAudioPlayer = document.getElementById('episode-audio-player');
    const addMarkerBtn = document.getElementById('add-marker-btn');
    const markerList = document.getElementById('marker-list');
    const audioTimeline = document.getElementById('audio-timeline');
    const adRemovalForm = document.getElementById('ad-removal-form');
    const adRemovalStrategy = document.getElementById('ad-removal-strategy');

    let token = localStorage.getItem("accessToken");
    let currentPodcastId = null;
    let currentEpisodeAudioUrl = null;
    let currentMarkers = []; // Stores marker times in seconds
    let currentTheme = localStorage.getItem("theme") || "light";

    // Apply initial theme
    applyTheme();

    if (token) {
        authSection.classList.add("d-none");
        appSection.classList.remove("d-none");
        fetchMySubscriptions(); // Fetch subscriptions if already logged in
    }

    //
    // Theme Switcher
    //
    function applyTheme() {
        if (currentTheme === "dark") {
            document.body.classList.add("dark-mode");
        } else {
            document.body.classList.remove("dark-mode");
        }
    }

    themeSwitcher.addEventListener("click", () => {
        currentTheme = currentTheme === "light" ? "dark" : "light";
        localStorage.setItem("theme", currentTheme);
        applyTheme();
    });

    //
    // Authentication UI Toggling
    //
    showRegisterLink.addEventListener("click", (e) => {
        e.preventDefault();
        loginContainer.classList.add("d-none");
        registerContainer.classList.remove("d-none");
    });

    showLoginLink.addEventListener("click", (e) => {
        e.preventDefault();
        registerContainer.classList.add("d-none");
        loginContainer.classList.remove("d-none");
    });

    logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("accessToken");
        location.reload();
    });

    //
    // Authentication API Calls
    //
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = e.target.elements["login-username"].value;
        const password = e.target.elements["login-password"].value;

        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch("/api/v1/users/login/access-token", {
                method: "POST",
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData,
            });

            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error("Login failed. Please check your username and password, or register if you don't have an account.");
                }
                throw new Error("Login failed");
            }

            const data = await response.json();
            token = data.access_token;
            localStorage.setItem("accessToken", token);
            authSection.classList.add("d-none");
            appSection.classList.remove("d-none");
            fetchMySubscriptions(); // Fetch subscriptions after successful login
        } catch (error) {
            console.error(error);
            alert(error.message);
        }
    });

    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = e.target.elements["register-username"].value;
        const password = e.target.elements["register-password"].value;

        try {
            const response = await fetch("/api/v1/users/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            if (!response.ok) {
                let errorMessage = "Registration failed";
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (e) {
                    errorMessage = await response.text();
                }
                throw new Error(errorMessage);
            }
            alert("Registration successful! Please login.");
            registerForm.reset();
            // Show login form after successful registration
            registerContainer.classList.add("d-none");
            loginContainer.classList.remove("d-none");

        } catch (error) {
            console.error(error);
            alert(error.message);
        }
    });

    //
    // Podcast Search
    //
    searchForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = e.target.elements["search-query"].value;
        
        try {
            const response = await fetch(`/api/v1/podcasts/search?query=${query}`, {
                headers: { Authorization: `Bearer ${token}` },
            });

            if (!response.ok) throw new Error("Search failed");

            const data = await response.json();
            displaySearchResults(data.feeds);

        } catch (error) {
            console.error(error);
            alert(error.message);
        }
    });

    function displaySearchResults(feeds) {
        searchResults.innerHTML = "";
        if (feeds.length === 0) {
            searchResults.innerHTML = "<p>No podcasts found.</p>";
            return;
        }
        feeds.forEach(feed => {
            const col = document.createElement("div");
            col.className = "col-md-4 mb-4";
            col.innerHTML = `
                <div class="card">
                    <img src="${feed.image}" class="card-img-top" alt="${feed.title}">
                    <div class="card-body">
                        <h5 class="card-title">${feed.title}</h5>
                        <button class="btn btn-primary btn-sm subscribe-btn" 
                                data-feed-url="${feed.url}" 
                                data-title="${feed.title}" 
                                data-image-url="${feed.image}">Subscribe</button>
                    </div>
                </div>
            `;
            searchResults.appendChild(col);
        });

        // Add event listeners to the new subscribe buttons
        document.querySelectorAll(".subscribe-btn").forEach(button => {
            button.addEventListener("click", async (e) => {
                const feedUrl = e.target.dataset.feedUrl;
                const title = e.target.dataset.title;
                const imageUrl = e.target.dataset.imageUrl;
                await subscribe(feedUrl, title, imageUrl);
            });
        });
    }

    async function subscribe(feedUrl, title, imageUrl) {
        try {
            const response = await fetch("/api/v1/subscriptions/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    podcast_feed_url: feedUrl,
                    podcast_title: title,
                    podcast_image_url: imageUrl,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Subscription failed");
            }

            const data = await response.json();
            alert(`Successfully subscribed to ${data.podcast_id}!`);
            fetchMySubscriptions(); // Refresh subscriptions after a new one is added
        } catch (error) {
            console.error("Subscription error:", error);
            alert(`Subscription failed: ${error.message}`);
        }
    }

    //
    // My Subscriptions
    //
    async function fetchMySubscriptions() {
        try {
            const response = await fetch("/api/v1/subscriptions/my", {
                headers: { Authorization: `Bearer ${token}` },
            });

            if (!response.ok) throw new Error("Failed to fetch subscriptions");

            const subscriptions = await response.json();
            displayMySubscriptions(subscriptions);
        } catch (error) {
            console.error("Error fetching subscriptions:", error);
            // Handle token expiration or invalid token by logging out
            if (error.status === 401) { // This might be too generic, consider specific HTTP status codes if available
                localStorage.removeItem("accessToken");
                location.reload(); // Reload to show login screen
            }
            alert(`Failed to load subscriptions: ${error.message}`);
        }
    }

    function displayMySubscriptions(subscriptions) {
        mySubscriptionsSection.innerHTML = "";
        if (subscriptions.length === 0) {
            mySubscriptionsSection.innerHTML = "<p>You have not subscribed to any podcasts yet.</p>";
            return;
        }
        subscriptions.forEach(sub => {
            const col = document.createElement("div");
            col.className = "col-md-4 mb-4";
            col.innerHTML = `
                <div class="card">
                    <img src="${sub.podcast_image_url}" class="card-img-top" alt="${sub.podcast_title}">
                    <div class="card-body">
                        <h5 class="card-title">${sub.podcast_title}</h5>
                        <p class="card-text">Feed: <a href="${sub.podcast_feed_url}" target="_blank">${sub.podcast_feed_url}</a></p>
                        <p class="card-text">My Custom Feed: <a href="/custom-feeds/${sub.custom_feed_slug}.xml" target="_blank">Link</a></p>
                        <button class="btn btn-info btn-sm view-episodes-btn" 
                                data-podcast-id="${sub.podcast_id}" 
                                data-podcast-title="${sub.podcast_title}"
                                data-subscription-id="${sub.subscription_id}">View Episodes</button>
                    </div>
                </div>
            `;
            mySubscriptionsSection.appendChild(col);
        });

        document.querySelectorAll(".view-episodes-btn").forEach(button => {
            button.addEventListener("click", (e) => {
                currentPodcastId = e.target.dataset.podcastId;
                const podcastTitle = e.target.dataset.podcastTitle;
                const subscriptionId = e.target.dataset.subscriptionId; // Get subscription_id
                modalPodcastTitle.textContent = podcastTitle;
                fetchEpisodesForPodcast(currentPodcastId);
                fetchAdRemovalRule(subscriptionId); // Fetch existing rule
                episodeModal.show();
            });
        });
    }

    //
    // Episode Modal Logic
    //
    async function fetchEpisodesForPodcast(podcastId) {
        try {
            const response = await fetch(`/api/v1/podcasts/${podcastId}/episodes`, {
                headers: { Authorization: `Bearer ${token}` },
            });

            if (!response.ok) throw new Error("Failed to fetch episodes");

            const episodes = await response.json();
            displayEpisodesInModal(episodes);
        } catch (error) {
            console.error("Error fetching episodes:", error);
            alert(`Failed to load episodes: ${error.message}`);
        }
    }

    function displayEpisodesInModal(episodes) {
        episodeList.innerHTML = "";
        if (episodes.length === 0) {
            episodeList.innerHTML = "<p>No episodes found for this podcast.</p>";
            return;
        }
        episodes.forEach(ep => {
            const li = document.createElement("li");
            li.className = "list-group-item d-flex justify-content-between align-items-center";
            li.innerHTML = `
                <span>${ep.title}</span>
                <button class="btn btn-sm btn-success play-episode-btn" data-audio-url="${ep.original_audio_url}">Play</button>
            `;
            episodeList.appendChild(li);
        });

        document.querySelectorAll(".play-episode-btn").forEach(button => {
            button.addEventListener("click", (e) => {
                currentEpisodeAudioUrl = e.target.dataset.audioUrl;
                episodeAudioPlayer.src = currentEpisodeAudioUrl;
                episodeAudioPlayer.play();
                // Markers are loaded from fetchAdRemovalRule, so no reset here unless it's a new podcast
                renderMarkers();
            });
        });
    }

    addMarkerBtn.addEventListener("click", () => {
        if (episodeAudioPlayer.src && !episodeAudioPlayer.paused && episodeAudioPlayer.currentTime > 0) {
            const markerTime = episodeAudioPlayer.currentTime;
            currentMarkers.push(markerTime);
            currentMarkers.sort((a, b) => a - b); // Keep markers sorted
            renderMarkers();
        } else {
            alert("Please play an episode to add a marker.");
        }
    });

    function renderMarkers() {
        markerList.innerHTML = "";
        audioTimeline.innerHTML = ""; // Clear existing timeline markers

        const duration = episodeAudioPlayer.duration;
        if (!isNaN(duration) && duration > 0) {
            currentMarkers.forEach((time, index) => {
                // List display
                const li = document.createElement("li");
                li.className = "list-group-item d-flex justify-content-between align-items-center";
                li.innerHTML = `
                    Marker ${index + 1}: ${formatTime(time)}
                    <button class="btn btn-danger btn-sm remove-marker-btn" data-index="${index}">Remove</button>
                `;
                markerList.appendChild(li);

                // Timeline display
                const position = (time / duration) * 100; // Percentage across the timeline
                const markerDiv = document.createElement("div");
                markerDiv.className = "timeline-marker";
                markerDiv.style.left = `${position}%`;
                markerDiv.title = formatTime(time);
                audioTimeline.appendChild(markerDiv);
            });
        }
        
        document.querySelectorAll(".remove-marker-btn").forEach(button => {
            button.addEventListener("click", (e) => {
                const indexToRemove = parseInt(e.target.dataset.index);
                currentMarkers.splice(indexToRemove, 1);
                renderMarkers();
            });
        });
    }

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
    }

    // Styling for timeline markers (add to your CSS or inject dynamically)
    const style = document.createElement('style');
    style.innerHTML = `
        .timeline-marker {
            position: absolute;
            top: 0;
            width: 2px;
            height: 100%;
            background-color: red;
            cursor: pointer;
            z-index: 10;
        }
    `;
    document.head.appendChild(style);


    adRemovalForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!currentPodcastId) {
            alert("Please select a podcast first.");
            return;
        }

        // Convert markers to milliseconds
        const markersInMs = currentMarkers.map(time => Math.round(time * 1000));

        const ruleData = {
            subscription_id: parseInt(document.querySelector('.view-episodes-btn').dataset.subscriptionId), // This needs to be dynamically set from the selected subscription
            strategy: adRemovalStrategy.value,
            markers: markersInMs.map((ms, index) => ({ marker_time_ms: ms, marker_order: index + 1 })),
        };

        try {
            const response = await fetch("/api/v1/ad-removal/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify(ruleData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to save ad removal rules.");
            }

            alert("Ad Removal Rules saved successfully!");
        } catch (error) {
            console.error("Error saving ad removal rules:", error);
            alert(`Error saving ad removal rules: ${error.message}`);
        }
    });

    async function fetchAdRemovalRule(subscriptionId) {
        try {
            const response = await fetch(`/api/v1/ad-removal/${subscriptionId}`, {
                headers: { Authorization: `Bearer ${token}` },
            });

            if (response.status === 404) {
                // No rule exists yet, reset form
                adRemovalStrategy.value = "none";
                currentMarkers = [];
                renderMarkers();
                return;
            }

            if (!response.ok) throw new Error("Failed to fetch ad removal rule.");

            const rule = await response.json();
            adRemovalStrategy.value = rule.strategy;
            currentMarkers = rule.markers.map(marker => marker.marker_time_ms / 1000); // Convert back to seconds
            renderMarkers();

        } catch (error) {
            console.error("Error fetching ad removal rule:", error);
            alert(`Error fetching ad removal rule: ${error.message}`);
        }
    }
});