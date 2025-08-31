# IT Analytics Platform

This is a monorepo for the IT Analytics Platform, managed with [Turborepo](https://turbo.build/).

## Monorepo Structure

This repository contains the following applications:

-   `frontend`: A [Next.js](https://nextjs.org/) application for the user interface.
-   `backend`: A [FastAPI](https://fastapi.tiangolo.com/) application for the API and machine learning models.

## Getting Started

### Prerequisites

-   [Node.js](https://nodejs.org/) (v18 or later)
-   [npm](https://www.npmjs.com/) (v8 or later)
-   [Python](https://www.python.org/) (v3.11 or later)
-   [uv](https://docs.astral.sh/uv/)

### Installation

To install the dependencies for all applications, run the following command from the root of the project:

```bash
npm install
```

This will install the dependencies for the root, the `frontend`, and the `backend`.

## Development

To start the development servers for both the `frontend` and `backend`, run the following command from the root of the project:

```bash
npm run dev
```

This will start the following services:
-   The `frontend` application at [http://localhost:3000](http://localhost:3000)
-   The `backend` application at [http://localhost:8000](http://localhost:8000)

## Build

To build both applications for production, run the following command from the root of the project:

```bash
npm run build
```

This will create optimized builds of the `frontend` and `backend` applications.

## Testing

To run the tests for both applications, run the following command from the root of the project:

```bash
npm run test
```

## Clean

To clean up the project by removing all `node_modules` and build artifacts, run the following command from the root of the project:

```bash
npm run clean
```
