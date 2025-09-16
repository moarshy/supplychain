# AI4SupplyChain Development Makefile

.PHONY: help install-backend install-frontend install dev-backend dev-frontend dev stop clean test lint format

# Default target
help:
	@echo "AI4SupplyChain Development Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup:"
	@echo "  install           Install all dependencies (backend + frontend)"
	@echo "  install-backend   Install backend dependencies with UV"
	@echo "  install-frontend  Install frontend dependencies with Bun"
	@echo ""
	@echo "Development:"
	@echo "  backend       Run backend development server only"
	@echo "  frontend      Run frontend development server only"
	@echo ""
	@echo "Utilities:"
	@echo "  clean             Clean build artifacts and cache"

# Installation targets
install: install-backend install-frontend
	@echo "✅ All dependencies installed successfully"

install-backend:
	@echo "🔧 Installing backend dependencies..."
	cd backend && uv sync
	@echo "✅ Backend dependencies installed"

install-frontend:
	@echo "🔧 Installing frontend dependencies..."
	cd frontend && bun install
	@echo "✅ Frontend dependencies installed"

backend:
	@echo "🐍 Starting backend development server..."
	cd backend && uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	@echo "⚛️  Starting frontend development server..."
	cd frontend && bun run dev

# Code quality targets
lint:
	@echo "🔍 Running linting..."
	cd backend && uv run ruff check src tests
	cd frontend && bun run lint

format:
	@echo "✨ Formatting code..."
	cd backend && uv run ruff format src tests
	cd backend && uv run ruff check --fix src tests
	cd frontend && bun run format

# Utility targets
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf backend/.pytest_cache
	rm -rf backend/__pycache__
	rm -rf backend/src/__pycache__
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	rm -rf frontend/.next
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "✅ Cleanup completed"
