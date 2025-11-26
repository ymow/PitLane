# PitLane - Global F1 News Platform

PitLane is a world-class, multi-language Formula 1 news aggregation platform designed to serve the global F1 fanbase. The platform aggregates news from premium sources, provides AI-powered translations, and delivers personalized content experiences across 10+ languages.

## 🏎️ Features

- **Multi-language Support**: 10+ languages including English, Chinese, Spanish, Portuguese, and more
- **AI-Powered Translation**: Claude AI provides high-quality, F1-specific translations
- **Real-time Updates**: News aggregation every 5 minutes from 15+ premium sources
- **Smart Categorization**: Automatic classification of breaking news, race reports, technical analysis, etc.
- **Entity Extraction**: Automatic tagging of drivers, teams, and topics
- **Fast Performance**: Server-side rendering with Redis caching for sub-2s page loads

## 🛠️ Technology Stack

### Backend
- **Django 5.x** - Web framework
- **Django REST Framework** - API layer
- **Celery** - Background task processing
- **Redis** - Caching and task queue
- **PostgreSQL** - Database
- **Anthropic Claude** - AI translation
- **python-i18n** - Internationalization

### Frontend (Coming Soon)
- **React 18** - UI framework
- **Vike** - SSR framework
- **Base UI** - Headless component library
- **Tailwind CSS** - Styling

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Anthropic API key (for translations)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pitlane.git
   cd pitlane
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec api python manage.py migrate
   ```

5. **Seed the database with F1 2025 data**
   ```bash
   docker-compose exec api python manage.py seed_data
   ```

6. **Create a superuser**
   ```bash
   docker-compose exec api python manage.py createsuperuser
   ```

7. **Access the application**
   - API: http://localhost:8000/api/v1/
   - Admin: http://localhost:8000/admin/

## 📚 API Endpoints

### Articles
- `GET /api/v1/articles/` - List articles (with pagination and filters)
- `GET /api/v1/articles/{slug}/` - Get article detail
- `GET /api/v1/articles/breaking/` - Get breaking news
- `GET /api/v1/articles/{id}/related/` - Get related articles

### Drivers
- `GET /api/v1/drivers/` - List all drivers
- `GET /api/v1/drivers/{code}/` - Get driver detail
- `GET /api/v1/drivers/{code}/articles/` - Get driver's articles

### Teams
- `GET /api/v1/teams/` - List all teams
- `GET /api/v1/teams/{code}/` - Get team detail
- `GET /api/v1/teams/{code}/articles/` - Get team's articles

### Other
- `GET /api/v1/i18n/?lang={code}` - Get UI translations
- `GET /api/v1/search/?q={query}&lang={code}` - Search articles

### Query Parameters
- `lang` - Language code (en, zh-TW, es, pt-BR, etc.)
- `category` - Filter by category (BREAKING, NEWS, RACE_REPORT, etc.)
- `driver` - Filter by driver code (VER, NOR, HAM, etc.)
- `team` - Filter by team code (RBR, MCL, FER, etc.)
- `page` - Page number for pagination
- `page_size` - Items per page (max 50)

## 🔧 Development

### Running Migrations
```bash
docker-compose exec api python manage.py makemigrations
docker-compose exec api python manage.py migrate
```

### Creating a Management Command
```bash
docker-compose exec api python manage.py <command_name>
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f celery
docker-compose logs -f celery-beat
```

### Running Tests
```bash
docker-compose exec api python manage.py test
```

### Accessing Django Shell
```bash
docker-compose exec api python manage.py shell
```

## 📦 Project Structure

```
PitLane/
├── backend/
│   ├── apps/
│   │   ├── news/          # Core models (Article, Driver, Team, etc.)
│   │   ├── api/           # REST API views and serializers
│   │   ├── fetcher/       # RSS feed fetching
│   │   ├── translator/    # Claude AI translation
│   │   ├── processor/     # Entity extraction, categorization
│   │   └── workers/       # Celery tasks and schedules
│   ├── config/            # Django settings
│   ├── locales/           # i18n translation files
│   └── manage.py
├── docker-compose.yml
└── README.md
```

## 🌍 Supported Languages

- 🇬🇧 English (en)
- 🇹🇼 繁體中文 Traditional Chinese (zh-TW)
- 🇪🇸 Español Spanish (es)
- 🇧🇷 Português Brazilian Portuguese (pt-BR)
- 🇨🇳 简体中文 Simplified Chinese (zh-CN)
- 🇮🇹 Italiano Italian (it)
- 🇳🇱 Nederlands Dutch (nl)
- 🇩🇪 Deutsch German (de)
- 🇯🇵 日本語 Japanese (ja)
- 🇫🇷 Français French (fr)

## 🏁 F1 2025 Grid

### Teams
- Red Bull Racing (RBR)
- Scuderia Ferrari (FER)
- McLaren F1 Team (MCL)
- Mercedes-AMG Petronas (MER)
- Aston Martin Aramco (AMR)
- Alpine F1 Team (ALP)
- Williams Racing (WIL)
- Racing Bulls (RBT)
- MoneyGram Haas F1 Team (HAA)
- Kick Sauber (SAU)

### Drivers
20 drivers including Verstappen, Hamilton, Leclerc, Norris, and more.

## 🔄 Background Tasks

PitLane uses Celery for background processing:

- **RSS Fetching**: High priority sources every 5 minutes
- **AI Translation**: Automatic translation to target languages
- **Entity Extraction**: Driver/team tagging
- **Categorization**: Automatic article classification
- **Cache Warming**: Hourly cache refresh
- **Cleanup**: Daily removal of old articles (90+ days)

## 📊 Architecture

```
┌─────────────────┐
│   Cloudflare    │  (Future: CDN)
└────────┬────────┘
         │
         ▼
┌─────────────────┐     REST API     ┌─────────────────┐
│  React + Vike   │◀────────────────▶│  Django API     │
│  (SSR)          │                   │  + Celery       │
└─────────────────┘                   └────────┬────────┘
                                               │
                      ┌────────────────────────┼────────┐
                      ▼                        ▼        ▼
                ┌──────────┐            ┌──────────┐  ┌──────┐
                │PostgreSQL│            │  Redis   │  │Claude│
                └──────────┘            └──────────┘  └──────┘
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- F1 data and schedules from official F1 sources
- News content from premium F1 media partners
- AI translations powered by Anthropic Claude
- 2025 F1 grid data

## 📞 Support

For issues and questions, please use the GitHub issue tracker.

---

Built with ❤️ for the global F1 community
