# Podcast Ad Remover

This project is a self-hosted podcast ad remover. It fetches podcast feeds, downloads episodes, and provides a custom, ad-free feed for you to use in your favorite podcast player.

## How it Works

The application has a few main components:

- **Backend (FastAPI):** An API built with FastAPI that manages podcast subscriptions, fetches new episodes, and handles ad removal.
- **Frontend (Vanilla JS):** A simple web interface to manage your podcast subscriptions.
- **NGINX:** Acts as a reverse proxy and serves the frontend and media files.
- **Storage:** Stores the downloaded and processed podcast episodes.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+ and Pip
- NGINX
- A MySQL database

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/aboxfulloftide/podcast.git
    cd podcast
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    ```

## Configuration

### 1. Environment Variables

The backend uses a `.env` file for configuration. Create a file named `.env` in the root of the project and add the following variables:

```
# backend/app/core/config.py

# Database settings
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_NAME=your_db_name
DB_PORT=your_db_port

# Podcast Index API settings
PODCAST_INDEX_API_KEY=your_podcast_index_api_key
PODCAST_INDEX_API_SECRET=your_podcast_index_api_secret

# JWT settings
SECRET_KEY=a_very_secret_key # Replace with a real secret key

```

### 2. NGINX

The `nginx.conf` file is included in the project. You will need to customize it for your environment.

**Important:** The paths in `nginx.conf` are hardcoded. You **must** update them to match the absolute path of the project on your system.

-   `root /home/matheau/code/podcast_v2/frontend;` -> `root /your/path/to/podcast_v2/frontend;`
-   `alias /home/matheau/code/podcast_v2/frontend/static/;` -> `alias /your/path/to/podcast_v2/frontend/static/;`
-   `alias /home/matheau/code/podcast_v2/storage/feeds/;` -> `alias /your/path/to/podcast_v2/storage/feeds/;`
-   `alias /home/matheau/code/podcast_v2/storage/podcasts/;` -> `alias /your/path/to/podcast_v2/storage/podcasts/;`

Once you have updated the paths, you can either replace your system's `nginx.conf` with this one, or include it in your existing NGINX configuration.

After configuring, start or reload NGINX:

```bash
sudo systemctl start nginx
# or
sudo systemctl reload nginx
```

## Running the Application

The `start.sh` script is provided to run the backend server.

```bash
./start.sh
```

This will:
1.  Navigate to the `backend` directory.
2.  Install the required python packages.
3.  Start a Gunicorn server with Uvicorn workers, listening on `0.0.0.0:8000`.

With NGINX and the backend server running, you should be able to access the frontend in your browser at `http://localhost` (or the domain you configured in `nginx.conf`).

## Project Structure

```
.
├── backend/        # FastAPI application
├── frontend/       # Static frontend files (HTML, JS)
├── nginx.conf      # NGINX configuration
├── scripts/        # Database schema
├── start.sh        # Script to start the backend server
└── storage/        # Storage for podcasts and feeds
```
