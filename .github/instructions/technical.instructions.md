# Technical Requirements

## Project Layout 

The repo is organised into three source-aligned zones — the domain owns behaviour,
contracts and events; experiences consume that one API; the platform runs the
supporting infrastructure and analytics.

Project Structure:
├── domain/                 # The source-aligned core (owns behaviour + contracts + events)
│   ├── api/                #   FastAPI behaviour service (src/ + tests/)
│   ├── contracts/          #   api/ AsyncAPI + data/ data-product contract
│   └── events/             #   Event payload schemas
├── experiences/            # Channels that consume the one domain API
│   ├── web/                #   Flask web frontend
│   ├── mobile/             #   Expo / React Native (web-exported for compose)
│   └── agent/              #   MCP server exposing the domain as agent tools
├── platform/               # Supporting infrastructure and analytics
│   ├── streaming/          #   Benthos (bento) NATS -> object-storage pipeline
│   ├── storage/            #   Object-storage config (S3-compatible)
│   └── analytics/          #   visualisation/ (Streamlit) + outcomes/ (pandas)
├── docs/                   # Documentation (requirements, design, guides)
├── README.md               # Project overview and setup instructions
├── Taskfile.yml            # Taskfile for development commands
├── docker-compose.yml      # Local, isolated multi-service stack
└── .github/                # CI/CD workflows and templates

## Methodologies#

- Always use conventional commits.
- Contract first development.
- Data contracts will conform to https://github.com/datacontract/datacontract-specification/blob/main/datacontract.schema.json
- Test driven development.
- Data outcomes and reporting will live alongside the application.
- Event driven patterns will be leveraged.
- The application behaviour will be decoupled from the data product.
- Local first and isolation.
- AsyncAPI will be used for API contracts.
- Data contract will be used for data contracts.
- Cloud events will be used for event data structures.

## Tech Stack

### Include

- Docker
- FastAPI for API
- Python for data engineering
- Event Hub for event broker
- Typescript for web application
- Streamlit for the reporting outcome
- SeaweedFS (S3-compatible, Apache-2.0) for the data product storage
- Delta file format

### Exclude

- Spark related technologies