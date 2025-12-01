FROM python:3.12-slim

WORKDIR /app

# Install uv for faster dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv pip install --system --no-cache -e .

# Copy application code
COPY . .

# Expose port
EXPOSE 5050

# Run migrations on startup, then start app
ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "4", "run:app"]
