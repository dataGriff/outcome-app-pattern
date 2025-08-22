# Development Instructions

## Order of Work

### First: Behavioural Contract

1. Behavioural Asyncapi contract that conforms to AsyncAPI yaml schema.
2. Validate and lint the AsyncAPI schema to ensure that it is valid.

### Second: Data Contract

1. Data product data contract that confirms to data contract yaml schema.
2. Validate and lint the data contract schema to ensure that it is valid.

## Third: Infrastructure

1. Any resource required as part of the infrastructure should be created using docker compose.

## Fourth: Behavioural Implementation

1. Tests for behavioural implementation logic
2. Behavioural implementation logic to meet AsyncApi contract requirements and tests.
3. Behavioural implementation logic passes contract and behavioural tests.
4. Dockerfile and docker compose updates.

## Fifth: Data Product Implementation

1. Tests for data streaming or data pipeline implementation logic.
2. Data streaming or data pipeline implementation logic to meet data contract requirements and tests.
3. Data streaming or data pipeline implementation logic passes contract and data tests.
4. Dockerfile and docker compose updates.

### Sixth: Experience for Application

1. Tests for user experience components.
2. User experience components to meet design requirements and tests.
3. User experience components pass design and implementation tests.
4. Dockerfile and docker compose updates.

### Seventh: Experience for Reporting

4. Tests for reporting outcomes.
5. Reporting outcomes to meet requirements and tests.
6. Reporting outcomes pass validation tests.
4. Dockerfile and docker compose updates.

### Eighth: Entire Application

1. The application should now work via the experience UI.
2. The data product should be updating and reflecting changes in real-time in the reporting UI.

## Important

For any repetitive development tasks that we will also need as part of continuous integration, start building up a taskfile.

Repetitive development tasks:

- Contract linting and validation.
- Code linting.
- Testing.
- Deployment.
- Running application.
