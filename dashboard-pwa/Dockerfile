# Install dependencies using bun
FROM oven/bun:1.1-slim AS deps

WORKDIR /app

COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

# Build the application
FROM deps AS builder

COPY . .

# Environment variables must be present at build time
ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}

RUN bun run build

# Run the application
FROM deps AS runner

WORKDIR /app

# Copy the built application and necessary files
COPY --from=builder /app ./

# Re-define environment variables at run time
ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}

EXPOSE 3000

# Start the application using bun
CMD ["bun", "run", "start"]
