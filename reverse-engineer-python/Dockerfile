# Multi-stage build for optimized re-cue container image
FROM python:3.9-slim as builder

WORKDIR /build

# Install build dependencies
RUN pip install --no-cache-dir build wheel

# Copy package files
COPY pyproject.toml setup.py README.md LICENSE ./
COPY reverse_engineer/ ./reverse_engineer/

# Build wheel
RUN python -m build --wheel

# Final stage
FROM python:3.9-slim

LABEL org.opencontainers.image.source="https://github.com/cue-3/re-cue"
LABEL org.opencontainers.image.description="RE-cue: Reverse Engineering for Cue - Generate UML diagrams from code"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /workspace

# Install the package from wheel
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Set entrypoint
ENTRYPOINT ["recue"]

# Default command shows help
CMD ["--help"]
