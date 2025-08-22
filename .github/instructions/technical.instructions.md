# Technical Requirements

## Project Layout 

Project Structure:
├── behaviour/          # Business logic and behaviors
│   ├── src/            # Source code for business logic
│   └── tests/          # Business logic tests
├── contracts/          
│   ├── api/            # AsyncApi contract - https://www.asyncapi.com/en
│   └── data/           # Data product contract - https://datacontract.com/
├── data/               # Data product based on outcomes of behaviour
│   ├── src/            # Source code for data product outcomes
│   └── tests/          # Data product outcomes tests
├── experience/         # User experience components
│   ├── src/            # Source code for UI/UX components
│   └── tests/          # UI/UX component tests
├── outcomes/           # Reporting, metrics, and user experience outcomes
│   ├── src/            # Source code for reporting outcomes
│   └── tests/          # Reporting outcome validation tests
├── docs/               # Documentation (requirements, design, guides)
├── tools/              # Development tooling and scripts
├── README.md           # Project overview and setup instructions
├── CONTRIBUTING.md     # Contribution guidelines
├── LICENSE.md          # Project license information
├── CHANGELOG.md        # Project changelog
├── .gitignore          # Git ignore file
├── Taskfile.yml        # Taskfile for development commands
└── .github/            # CI/CD workflows and templates

## Methodologies#

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
- MinIO for the data product storage
- Delta file format

### Exclude

- Spark related technologies