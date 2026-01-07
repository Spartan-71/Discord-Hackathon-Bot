# HackRadar

HackRadar is a **Discord Bot** that tracks upcoming hackathons from major platforms like MLH, Devpost, Devfolio, DoraHacks, and Unstop. It fetches data periodically and notifies your Discord server about new events.

## 🚀 Features

*   **Multi-Platform Scraping**: Supports MLH, Devpost, Devfolio, DoraHacks, and Unstop.
*   **Real-time Notifications**: Automatically posts new hackathons to your Discord server.
*   **Slash Commands**: Use `/fetch` to manually trigger updates.
*   **Database**: Uses PostgreSQL to store hackathon data and prevent duplicate notifications.
*   **Dockerized**: Easy deployment with Docker Compose.

## ⚡ Quick Start (Docker)

1.  **Configure Environment**:
    Copy the example environment file and fill in your details:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` with your Discord token and database credentials.

2.  **Run with Docker Compose**:
    ```bash
    docker compose build
    docker compose up -d
    ```

    The bot will start automatically and begin fetching hackathons.

## 🛠 Local Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/hackathon-bot.git
    cd hackathon-bot
    ```

2.  **Install dependencies**:
    This project uses `uv` for dependency management.
    ```bash
    uv pip install -e .
    ```

3.  **Set up PostgreSQL**:
    Ensure PostgreSQL is running locally and create a database (e.g., `hackradar`).

4.  **Configure Environment**:
    Create a `.env` file with your database credentials and Discord token.

5.  **Initialize Database**:
    ```bash
    python -m backend.init_db
    ```

6.  **Run the Bot**:
    ```bash
    python main.py
    ```

## ⚙️ Environment Variables
 
Refer to [`.env.example`](.env.example) for the complete list of required environment variables.
 
1.  **Copy the example file**:
    ```bash
    cp .env.example .env
    ```
2.  **Update the values** in `.env`:
    *   `DISCORD_TOKEN`: Your bot token.
    *   `POSTGRES_...`: Database credentials for Docker.
    *   `DATABASE_URL`: Connection string (only if running locally).

## 🤝 Contributing

Contributions are welcome! Please check the [CONTRIBUTING.md](CONTRIBUTING.md) guide before submitting pull requests.
