# Changelog

All notable changes to HackRadar will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-21

### 🎉 Initial Release

HackRadar v1.0.0 is the first stable release of the Discord Hackathon Bot! This release includes a comprehensive set of features for tracking and notifying users about hackathons from multiple platforms.

### ✨ Features

#### Core Functionality
- **Multi-Platform Hackathon Aggregation**: Automatically fetches hackathons from 7 major platforms:
  - Devfolio
  - Devpost
  - Unstop
  - DoraHacks
  - MLH (Major League Hacking)
  - Hack2Skill
  - Kaggle Competitions

- **Automated Notifications**: Background task runs every 12 hours to fetch new hackathons and notify configured servers
- **PostgreSQL Database**: Persistent storage for hackathons, guild configurations, and user subscriptions
- **Docker Support**: Fully containerized deployment with Docker Compose

#### Discord Commands

**Server Setup (Admin Only)**
- `/setup` - Interactive setup wizard with platform and theme selection
- `/pause` - Pause automatic notifications for the server
- `/resume` - Resume automatic notifications
- `/set_channel` - Configure notification channel (deprecated in favor of `/setup`)

**Search & Browse**
- `/search [keyword]` - Search hackathons by keyword
- `/upcoming [days]` - Get hackathons starting in the next X days
- `/platform [name] [count]` - Filter hackathons by platform

**Personal Subscriptions**
- `/subscribe [theme]` - Subscribe to DM notifications for specific themes
- `/unsubscribe [theme]` - Unsubscribe from theme notifications

**Information**
- `/help` - Display all available commands
- `/about` - Information about the bot
- `/hi` - Welcome message with quick start guide

#### User Experience
- **Rich Embeds**: Beautiful Discord embeds with hackathon details including:
  - Event title with random emoji
  - Duration, location, mode, and status
  - Prize pool, team size, and eligibility
  - Banner images
  - Direct registration links

- **Interactive Setup**: User-friendly setup wizard with dropdown menus for:
  - Platform selection (or default to all)
  - Theme selection (AI/ML, Blockchain, Web Development, etc.)
  - Channel selection

- **Welcome Messages**: Automatic welcome message when bot joins a new server
- **Permission Checks**: Proper permission validation for admin commands

#### Filtering & Preferences
- **Platform Filtering**: Subscribe to specific platforms or all platforms
- **Theme Filtering**: Filter by themes (AI/ML, Blockchain, Web3, Mobile, Data Science, IoT, Cloud, Cybersecurity)
- **Default to All**: If no preferences selected, receive all hackathon notifications

#### Notification Control
- **Pause/Resume**: Server admins can pause and resume automatic notifications
- **Manual Commands Work During Pause**: `/search`, `/upcoming`, and `/platform` continue to work when notifications are paused
- **Persistent State**: Pause state persists across bot restarts

### 🗄️ Database Schema

**Tables**
- `hackathons` - Stores hackathon data from all platforms
- `guild_configs` - Server-specific configuration (channel, platforms, themes, pause state)
- `user_subscriptions` - User theme subscriptions for DM notifications

**Key Fields**
- Hackathon: title, url, source, start_date, end_date, location, mode, status, tags, prize_pool, team_size, eligibility, banner_url
- Guild Config: guild_id, channel_id, subscribed_platforms, subscribed_themes, notifications_paused

### 🔧 Technical Details

- **Framework**: Discord.py with slash commands (app_commands)
- **Database**: SQLAlchemy ORM with PostgreSQL
- **Task Scheduling**: Discord.py tasks extension for periodic fetching
- **Environment Management**: python-dotenv for configuration
- **Dependency Management**: UV package manager
- **Containerization**: Docker with multi-stage builds

### 📝 Documentation

- `README.md` - Project overview and setup instructions
- `CONTRIBUTING.md` - Contribution guidelines
- `docs/terms_of_service.md` - Terms of Service
- `docs/privacy_policy.md` - Privacy Policy

### 🐛 Bug Fixes

- Fixed module import issues with proper PYTHONPATH configuration
- Fixed permission checks for channel access
- Fixed database connection handling in Docker environment
- Resolved command syncing issues on guild join

### 🔒 Security & Privacy

- No personal data collection beyond Discord IDs for subscriptions
- Secure environment variable handling
- Proper permission validation for admin commands
- GDPR-compliant data deletion on guild removal

### 📦 Deployment

**Docker Deployment** (Recommended)
```bash
docker compose up -d
```

**Local Deployment**
```bash
uv pip install -e .
python bot.py
```

### 🙏 Acknowledgments

- Built with Discord.py
- Hackathon data sourced from Devfolio, Devpost, Unstop, DoraHacks, MLH, Hack2Skill, and Kaggle
- Created by [@Spartan-71](https://github.com/Spartan-71)

### 📊 Statistics

- **Total Commands**: 12
- **Supported Platforms**: 7
- **Theme Categories**: 8
- **Lines of Code**: ~3,500+

---

**Full Changelog**: https://github.com/Spartan-71/Discord-Hackathon-Bot/commits/v1.0.0
