# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal portfolio/CV website built with FastAPI backend and vanilla HTML/CSS/JavaScript frontend. Data-driven design loads CV content from JSON. Deployed via Docker with Nginx reverse proxy.

## Common Commands

```bash
make py    # Build and start Docker containers
make rm    # Stop and remove Docker containers
make rpy   # Stop containers and rebuild
```

Manual Docker commands:
```bash
docker compose up -d --build   # Start with rebuild
docker compose down            # Stop containers
```

## Architecture

**Stack:** FastAPI (Python 3.11) + Jinja2 templates + vanilla JS/CSS + Docker + Nginx

**Key Files:**
- `main.py` - FastAPI application with routes and CV data loading
- `templates/index.html` - Jinja2 template for the portfolio page
- `static/style.css` - All styling with responsive design
- `static/script.js` - Frontend interactivity (animations, sidebar, etc.)
- `data/cv_data.json` - CV content data (not tracked in git)
- `config/nginx.conf` - Nginx reverse proxy configuration

**API Endpoints:**
- `GET /` - Main portfolio page
- `GET /api/cv` - JSON CV data
- `GET /api/contact` - Contact info JSON
- `GET /api/reload` - Reload CV data from file
- `GET /download-cv` - PDF CV download

**Data Flow:** CV data loaded from `data/cv_data.json` at startup → passed to Jinja2 template → rendered as responsive HTML with animated sections

## Development Notes

- Profile photos are auto-resized to 300x300px via Pillow
- CV data file (`data/cv_data.json`) and images are gitignored - use templates (`.tpl` files) as reference
- No test framework currently configured
- Application runs on port 8000 inside container, Nginx proxies from port 80
