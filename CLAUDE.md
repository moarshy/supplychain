# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI4SupplyChain is an AI-powered dynamic inventory and demand planning system designed for small to medium-sized businesses. It combines conversational AI with intelligent forecasting and optimization to transform reactive inventory management into proactive intelligence.

## Architecture & Structure

This project follows a layered architecture with clear separation between backend and frontend:

**Backend** (`backend/`)
- **Layer 1: Data Foundation** (`backend/src/data/`) - SQLModel models and SQLite database
- **Layer 2: Business Logic** (`backend/src/services/`) - Core business operations, forecasting, optimization
- **Layer 3: AI Agent** (`backend/src/agent/`) - LLM-powered conversational AI system
- **Layer 4: API** (`backend/src/api/`) - FastAPI REST endpoints with automatic documentation

**Frontend** (`frontend/`)
- React with TypeScript for type safety
- shadcn/ui component library
- Tailwind CSS for styling
- Bun for package management
- Component-based architecture with real-time updates

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Package Manager**: UV (ultra-fast Python package installer)
- **Database**: SQLite with SQLModel ORM
- **AI/ML**: LLM library + OpenAI GPT-4o mini + Anthropic Claude
- **Frontend**: React + TypeScript + shadcn/ui + Tailwind CSS
- **OCR**: Tesseract OCR + cloud APIs for document processing
- **Container**: Docker for deployment

## Development Commands

### Quick Development Setup
```bash
# Install all dependencies (backend + frontend)
make install

# Run both backend and frontend in development
make dev

# Or run individually
make dev-backend    # Backend only (http://localhost:8000)
make dev-frontend   # Frontend only (http://localhost:3000)
```

### Backend Development
```bash
# Install UV package manager first (one time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Backend specific commands
make install-backend
make dev-backend
make test-backend

# Manual commands if needed
cd backend && uv sync
cd backend && uv run uvicorn src.api.main:app --reload
```

### Frontend Development
```bash
# Frontend specific commands
make install-frontend
make dev-frontend
make test-frontend

# Manual commands if needed
cd frontend && bun install
cd frontend && bun run dev    # Uses Bun's built-in dev server
cd frontend && bun run build  # Uses Bun's built-in bundler
```

### Testing and Quality
```bash
# Run all tests
make test

# Code quality
make lint
make format
make clean
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

The `data/` directory at project root contains all runtime data during development:
- `*.db`, `*.sqlite` - SQLite database files
- `uploads/` - Temporary files for OCR and imports
- `exports/` - Generated reports, forecasts, and backups
- `logs/` - Application, AI agent, and API logs
- `sample_data/` - CSV files with sample products, suppliers, locations, transactions

**Note**: The entire `data/` folder is gitignored to prevent committing sensitive data.

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
- shadcn/ui for consistent, accessible UI components
- Tailwind CSS for utility-first styling
- Bun for package management (faster than npm/yarn)
- Follow component-based architecture with proper separation of concerns
- Implement real-time updates for inventory data

### UI Theme Customization with tweakcn
To customize the application's visual theme during development:

1. **Install tweakcn** (if not already installed):
   ```bash
   cd frontend && bun add tweakcn
   ```

2. **Access tweakcn theme generator**:
   - Visit https://tweakcn.com or use local tweakcn tools
   - Import your current shadcn/ui theme configuration
   - Use the visual editor to customize colors, typography, spacing

3. **Apply theme changes**:
   ```bash
   # Generate new theme CSS
   npx tweakcn generate --config tailwind.config.js --output src/styles/themes.css
   
   # Or use the online tool and export the generated CSS
   # Copy the generated CSS to src/styles/themes.css
   ```

4. **Theme development workflow**:
   - Edit colors, fonts, and spacing in tweakcn visual editor
   - Export generated CSS and Tailwind config
   - Replace `src/styles/themes.css` with new theme
   - Update `tailwind.config.js` with new color tokens if needed
   - Test theme across all components and pages

5. **Theme file structure**:
   ```
   frontend/src/styles/
     globals.css          # Global CSS and Tailwind imports
     themes.css          # tweakcn generated theme definitions
     components.css      # Component-specific overrides (if needed)
   ```

**Note**: Always test theme changes across the entire application to ensure consistency and accessibility.

## Testing Strategy

- **Backend Unit Tests**: Individual components and business logic (`backend/tests/`)
- **Backend Integration Tests**: API endpoints and database operations
- **AI Agent Tests**: LLM interactions and tool functionality
- **Frontend Unit Tests**: React components and utilities (`frontend/tests/`)
- **End-to-End Tests**: Complete user scenarios across both backend and frontend

## Production Considerations

- SQLite is sufficient for most use cases, PostgreSQL migration available if needed
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