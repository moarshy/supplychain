### Document Information
- **Version**: 1.0
- **Date**: 9/2025
- **Product Name**: AI4SupplyChain
- **Document Owner**: Development Team
### Development Phases: 
Start MVP phase first, gradually add more features for future phases, keep updating this document for features/phases


# Start MVP: AI-Powered Inventory System
## API-Based Architecture for Rapid Development

### Core Features We'll Build
1. **Product Master Data Management**: Complete product catalog with SKU setup, categorization, and supplier linking
2. **Smart Inventory Management**: Track products, stock levels, transactions across multiple locations
3. **Supplier Management**: Vendor database with lead times, pricing, and performance tracking
4. **Transaction Processing with OCR**: Manual entry plus automated document processing for POs/DOs
5. **Intelligent Forecasting**: Predict demand using historical data and multiple algorithms
6. **Optimization Engine**: Calculate optimal reorder points, EOQ, and safety stock levels
7. **Conversational AI**: Chat interface powered by GPT-4o mini/Claude
8. **Visual Dashboard**: Charts, reports, and analytics
9. **Data Simulation**: Generate realistic test data for development

### What Makes This Special
- **Professional AI**: GPT-4o mini and Claude 3.5 Haiku from day one
- **Predictable Costs**: ~$1-5/month even with heavy usage
- **Rapid Development**: Working prototype in 2-3 weeks
- **Production Ready**: Built with enterprise-grade APIs and best practices

## 🏗️ Complete Architecture & Project Structure

```
ai4supplychain/
├── pyproject.toml              # Project metadata and scripts
├── README.md                   # Project documentation
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore patterns
├── docker-compose.yml          # Local development setup
├── src/
│   └── config.py               # Single configuration file for backend
├── data/                       # Runtime data directory (gitignored)
│   ├── *.db                    # SQLite database files
│   ├── uploads/                # OCR documents and imports
│   ├── exports/                # Generated reports and backups
│   ├── logs/                   # Application logs
│   └── sample_data/            # Sample CSV files
├── Makefile                    # Development convenience commands
│
├── backend/                    # Backend API and services
│   ├── pyproject.toml          # Backend dependencies (UV)
│   ├── src/                    # Main backend package
│   │   ├── __init__.py
│   │   │
│   │   │ ┌─────────────────────────────────────────────────────────────┐
│   │   │ │                    LAYER 1: DATA FOUNDATION                 │
│   │   │ └─────────────────────────────────────────────────────────────┘
│   │   ├── data/               # Data models and schemas
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # Base model classes
│   │   │   ├── inventory.py    # Product, Stock, Transaction, Location models
│   │   │   ├── suppliers.py    # Supplier models and relationships
│   │   │   ├── forecast.py     # Forecast results and metadata
│   │   │   └── database.py     # Database setup and connection
│   │   │
│   │   │ ┌─────────────────────────────────────────────────────────────┐
│   │   │ │                   LAYER 2: BUSINESS LOGIC                   │
│   │   │ └─────────────────────────────────────────────────────────────┘
│   │   ├── services/           # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── inventory.py    # Inventory CRUD operations
│   │   │   ├── suppliers.py    # Supplier management and performance tracking
│   │   │   ├── transactions.py # Transaction processing with OCR integration
│   │   │   ├── forecasting.py  # Demand prediction algorithms
│   │   │   ├── optimization.py # EOQ, reorder point calculations
│   │   │   └── simulation.py   # Test data generation
│   │   │
│   │   │ ┌─────────────────────────────────────────────────────────────┐
│   │   │ │                 LAYER 3: AI AGENT (API-Based)               │
│   │   │ └─────────────────────────────────────────────────────────────┘
│   │   ├── agent/              # Conversational AI system
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py   # OpenAI/Anthropic API integration
│   │   │   ├── tools.py        # Business function tools
│   │   │   ├── agent.py        # LLM agent orchestration
│   │   │   └── memory.py       # Conversation memory management
│   │   │
│   │   │ ┌─────────────────────────────────────────────────────────────┐
│   │   │ │                        LAYER 4: API                        │
│   │   │ └─────────────────────────────────────────────────────────────┘
│   │   └── api/                # FastAPI REST endpoints
│   │       ├── __init__.py
│   │       ├── main.py         # FastAPI app and configuration
│   │       ├── inventory.py    # Inventory management endpoints
│   │       ├── suppliers.py    # Supplier management endpoints
│   │       ├── transactions.py # Transaction processing endpoints
│   │       ├── forecast.py     # Forecasting endpoints
│   │       └── chat.py         # Chat/agent endpoints
│   │
│   ├── tests/                  # Backend test suite
│   │   ├── __init__.py
│   │   ├── conftest.py         # Test configuration and fixtures
│   │   ├── test_models.py      # Data model tests
│   │   ├── test_services.py    # Business logic tests
│   │   ├── test_agent.py       # AI agent tests
│   │   └── test_api.py         # API endpoint tests
│   │
│   └── scripts/                # Backend utility scripts
│       ├── setup_dev.py        # Development environment setup
│       ├── generate_sample_data.py # Sample data generation
│       └── run_tests.py        # Test runner with coverage
│
├── frontend/                   # React frontend
│   ├── package.json            # Frontend dependencies (Bun)
│   ├── bun.lockb               # Bun lock file
│   ├── tsconfig.json           # TypeScript configuration
│   ├── .gitignore              # Git ignore for frontend
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   ├── components.json         # shadcn/ui configuration
│   │
│   ├── src/                    # Frontend source code
│   │   ├── components/         # Reusable React components
│   │   │   ├── ui/             # shadcn/ui base components
│   │   │   ├── charts/         # Chart components (using Recharts)
│   │   │   ├── tables/         # Table components (using TanStack Table)
│   │   │   └── forms/          # Form components (using React Hook Form)
│   │   │
│   │   ├── pages/              # Page components
│   │   │   ├── Dashboard.tsx   # Main dashboard
│   │   │   ├── Products.tsx    # Product management
│   │   │   ├── Inventory.tsx   # Inventory tracking
│   │   │   ├── Suppliers.tsx   # Supplier management
│   │   │   ├── Transactions.tsx # Transaction processing
│   │   │   ├── Forecasting.tsx # Demand forecasting
│   │   │   └── Chat.tsx        # AI chat interface
│   │   │
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API integration services
│   │   ├── types/              # TypeScript type definitions
│   │   └── utils/              # Utility functions
│   │
│   ├── tests/                  # Frontend test suite
│   │   ├── components/         # Component tests
│   │   ├── pages/              # Page tests
│   │   └── utils/              # Utility tests
│   │
│   └── public/                 # Static assets
│       ├── index.html
│       └── favicon.ico
│
│
├── docs/                       # Documentation
│   ├── setup.md                # Detailed setup instructions
│   ├── api.md                  # API documentation
│   ├── user_guide.md           # End-user guide
│   └── development.md          # Development guidelines
│
└── scripts/                    # Utility scripts
    ├── setup_dev.py            # Development environment setup
    ├── generate_sample_data.py # Sample data generation
    ├── run_tests.py            # Test runner with coverage
    └── deploy.py               # Deployment utilities
```

## 🏗️ Architecture Layers Explained

**Layer 1: Data Foundation** - SQLAlchemy models and database connections
**Layer 2: Business Logic** - Core services implementing business rules  
**Layer 3: AI Agent** - LangChain-powered conversational AI with tools
**Layer 4: API & Interface** - FastAPI REST endpoints and Streamlit UI
**Runtime Data Storage** - Persistent data, uploads, exports, and logs

### 🗄️ Storage Architecture Details

The `storage/` directory implements a **separation of concerns** approach, keeping runtime data completely separate from source code. This design ensures clean deployments, secure data handling, and easy backup strategies.

#### **Key Design Principles:**
- **🔒 Security**: Sensitive data (databases, uploads) never gets committed to version control
- **🚀 Deployment Ready**: Directory structure exists in Git via `.gitkeep` files, but actual data is created at runtime
- **📦 Portable**: Entire `storage/` folder can be backed up, moved, or mounted as a Docker volume
- **🔄 Environment Agnostic**: Same structure works for development, staging, and production

#### **Data Lifecycle Management:**
- **Persistent Data**: `database/`, `sample_data/` - Long-term storage requiring backups
- **Temporary Data**: `uploads/` - Processing files, cleaned periodically  
- **Generated Data**: `exports/`, `logs/` - Created by application, archived as needed

#### **Production Considerations:**
- **Database**: SQLite sufficient for most use cases, PostgreSQL available if needed
- **File Storage**: Local storage can be replaced with cloud storage (S3, Azure Blob)
- **Logging**: Log rotation and centralized logging (ELK stack) for production monitoring
- **Backups**: Automated backup strategies for `database/` and critical `exports/`

## 🛠️ Technology Stack (API-Based)

### Core Technologies
```yaml
Language: Python 3.11+
Package Manager: UV (ultra-fast Python package installer)
Database: SQLite (serverless, zero setup)
ORM: SQLModel (Pydantic + SQLAlchemy integration)
Web Framework: FastAPI (modern, fast, auto-docs)
UI Framework: Streamlit (pure Python, rapid development)

AI/ML Stack:
  Primary LLM: OpenAI GPT-4o mini (best cost/performance)
  Fallback LLM: Anthropic Claude 3.5 Haiku (reliable alternative)
  Agent Framework: LLM library (flexible choice)
  OCR Processing: Tesseract OCR + Google Vision API / AWS Textract
  ML Libraries: pandas, numpy, scipy, statsmodels
  Visualization: plotly, matplotlib

Development:
  Testing: pytest + coverage
  Containerization: Docker
  Code Quality: black, isort, flake8, mypy
```

### Why These Choices?

**API-Based LLMs**: Professional quality from day 1
- **GPT-4o mini**: $0.15/$0.60 per 1M tokens (excellent cost/performance)
- **Claude 3.5 Haiku**: $0.25/$1.25 per 1M tokens (reliable fallback)
- **Consistent performance**: No hardware dependencies or setup complexity
- **Latest capabilities**: Always get the newest model improvements
- **Enterprise reliability**: 99.9% uptime SLA

**UV Package Manager**: Next-generation Python tooling
- **10-100x faster** than pip/Poetry for installations
- **Modern design**: Built from ground up with current best practices
- **Drop-in replacement**: Compatible with existing Python workflows
- **Excellent dependency resolution**: Handles complex dependency trees efficiently

**SQLite + SQLModel**: Perfect for MVP
- **SQLite**: Zero configuration, handles millions of records, ACID compliant
- **SQLModel**: Type-safe models that work with both FastAPI and SQLAlchemy
- **Automatic validation**: Pydantic integration provides data validation
- **Easy migration**: SQLModel makes PostgreSQL migration seamless if needed

**FastAPI**: Modern web framework
- Automatic OpenAPI documentation generation
- Built-in validation with Pydantic models
- WebSocket support for real-time chat
- Production-ready performance

**Streamlit**: Rapid UI development
- Pure Python (no HTML/CSS/JavaScript needed)
- Built-in components perfect for data applications
- Real-time updates and interactivity
- Easy deployment and sharing

## 💰 Cost Analysis (API Approach)

### Modern API Pricing (2024)

| Provider | Model | Input Cost | Output Cost | Best For |
|----------|-------|------------|-------------|----------|
| **OpenAI** | GPT-4o mini | $0.15/1M tokens | $0.60/1M tokens | General purpose, cost-effective |
| **OpenAI** | GPT-4o | $2.50/1M tokens | $10.00/1M tokens | Complex reasoning tasks |
| **Anthropic** | Claude 3.5 Haiku | $0.25/1M tokens | $1.25/1M tokens | Fast, structured responses |
| **Anthropic** | Claude 3.5 Sonnet | $3.00/1M tokens | $15.00/1M tokens | Advanced reasoning |

### Realistic MVP Usage Costs

#### **Development Phase (Months 1-3)**
```
Daily usage during development:
- Testing/debugging: ~5K tokens/day
- Feature development: ~10K tokens/day
- Total: ~15K tokens/day × 30 days = 450K tokens/month

Cost with GPT-4o mini: ~$0.34/month
Cost with Claude 3.5 Haiku: ~$0.56/month

Essentially free during development! 🎉
```

#### **Light Production Usage**
```
Typical business usage:
- 50 inventory queries/day
- Average 500 tokens per interaction
- Total: 25K tokens/day × 30 days = 750K tokens/month

Cost with GPT-4o mini: ~$0.56/month
Still incredibly affordable!
```

#### **Heavy Usage (Successful Product)**
```
High-volume usage:
- 500 queries/day across multiple users
- 250K tokens/month

Cost with GPT-4o mini: ~$1.88/month
Even heavy usage is very affordable!
```


