# Stage 1: Build the virtual environment
FROM python:3.11-slim as builder

# Install uv
RUN pip install uv

# Create and activate a virtual environment
WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv venv
RUN uv sync --system

# Stage 2: Run the application
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /.venv
# Copy the application code
COPY ./app /app

# Activate the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
