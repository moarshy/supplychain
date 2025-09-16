# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI4SupplyChain is an AI-powered dynamic inventory and demand planning system designed for small to medium-sized businesses. It combines conversational AI with intelligent forecasting and optimization to transform reactive inventory management into proactive intelligence.

## Architecture & Structure

This project follows a layered architecture with clear separation between backend and frontend:

**Backend** (`backend/`)
- **Layer 1: Data Foundation** (`backend/src/data/`) - SQLAlchemy models and database schemas
- **Layer 2: Business Logic** (`backend/src/services/`) - Core business operations, forecasting, optimization
- **Layer 3: AI Agent** (`backend/src/agent/`) - LLM-powered conversational AI system
- **Layer 4: API** (`backend/src/api/`) - FastAPI REST endpoints with automatic documentation

**Frontend** (`frontend/`)
- React with TypeScript for type safety
- Bun for package management
- Component-based architecture with real-time updates

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Package Manager**: UV (ultra-fast Python package installer)
- **Database**: SQLite for MVP (PostgreSQL migration path)
- **AI/ML**: LLM library + OpenAI GPT-4o mini + Anthropic Claude
- **Frontend**: Streamlit for rapid prototyping, React planned for future
- **OCR**: Tesseract OCR + cloud APIs for document processing
- **Container**: Docker for deployment

## Development Commands

### Backend Setup and Development
```bash
# Navigate to backend directory
cd backend

# Install UV package manager first
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Setup development environment
python scripts/setup_dev.py

# Generate sample data
python scripts/generate_sample_data.py

# Start FastAPI backend
uvicorn src.api.main:app --reload

# Run backend tests
pytest tests/ -v

# Code quality checks
black src tests
isort src tests
flake8 src tests
mypy src
```

### Frontend Development
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
bun install

# Start development server
bun run dev

# Build for production
bun run build

# Run tests
bun test

# Type checking
bun run type-check
```

### Full Stack Development
```bash
# Run with Docker (both backend and frontend)
docker-compose up --build

# Run all tests (from project root)
./scripts/test-all.sh
```

## Key Features (MVP)

1. **Product Master Data Management** - Complete product catalog with SKUs, categories, supplier relationships
2. **Smart Inventory Management** - Real-time stock tracking across multiple locations with automated alerts
3. **Supplier Management** - Vendor database with lead times, pricing, and performance monitoring
4. **Transaction Processing with OCR** - Manual entry plus automated document processing for POs/DOs
5. **Intelligent Forecasting** - Demand prediction using multiple algorithms with seasonal detection
6. **Optimization Engine** - EOQ calculations, reorder point optimization, safety stock management
7. **Conversational AI Assistant** - Natural language interface for business intelligence and reporting
8. **Visual Dashboard** - Charts, reports, and analytics with real-time updates

## Data Storage Structure

The `storage/` directory maintains runtime data separate from source code:
- `database/` - SQLite database files (persistent)
- `sample_data/` - CSV files with sample products, suppliers, locations, transactions
- `uploads/` - Temporary files for OCR and imports
- `exports/` - Generated reports, forecasts, and backups
- `logs/` - Application, AI agent, and API logs

## Development Workflow

### Adding New Features
1. **Backend**: Start with data models in `backend/src/data/`
2. **Backend**: Implement business logic in `backend/src/services/`
3. **Backend**: Add API endpoints in `backend/src/api/`
4. **Frontend**: Create UI components in `frontend/src/components/`
5. **Testing**: Add comprehensive tests in respective `tests/` directories

### AI Agent Development
- Tools are defined in `backend/src/agent/tools.py`
- Agent orchestration uses LLM library in `backend/src/agent/agent.py`
- Memory management handles conversation context
- Cost-effective API usage with GPT-4o mini (~$1-5/month even with heavy usage)

### Frontend Guidelines
- Use React with TypeScript for type safety
- Bun for package management (faster than npm/yarn)
- Follow component-based architecture
- Implement real-time updates for inventory data

## Testing Strategy

- **Backend Unit Tests**: Individual components and business logic (`backend/tests/`)
- **Backend Integration Tests**: API endpoints and database operations
- **AI Agent Tests**: LLM interactions and tool functionality
- **Frontend Unit Tests**: React components and utilities (`frontend/tests/`)
- **End-to-End Tests**: Complete user scenarios across both backend and frontend

## Production Considerations

- SQLite scales to PostgreSQL for production
- Local file storage can migrate to cloud storage (S3, Azure Blob)
- Implement log rotation and centralized logging
- Automated backup strategies for database and exports
- Container orchestration with Docker Compose or Kubernetes

## Cost Management

API-based AI approach keeps costs predictable:
- Development: ~$0.34/month
- Light production: ~$0.56/month  
- Heavy usage: ~$1.88/month
- Fallback between OpenAI and Anthropic for reliability