# Install dependencies using bun
FROM oven/bun:1.1-slim AS deps

WORKDIR /app

COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

# Build the application
FROM deps AS builder

COPY . .

# Environment variables must be present at build time
ARG ENV_VARIABLE
ENV ENV_VARIABLE=${ENV_VARIABLE}
ARG NEXT_PUBLIC_ENV_VARIABLE
ENV NEXT_PUBLIC_ENV_VARIABLE=${NEXT_PUBLIC_ENV_VARIABLE}

RUN bun run build

# Run the application
FROM deps AS runner

WORKDIR /app

# Copy the built application and necessary files
COPY --from=builder /app ./

# Re-define environment variables at run time
ARG ENV_VARIABLE
ENV ENV_VARIABLE=${ENV_VARIABLE}
ARG NEXT_PUBLIC_ENV_VARIABLE
ENV NEXT_PUBLIC_ENV_VARIABLE=${NEXT_PUBLIC_ENV_VARIABLE}

EXPOSE 3000

# Start the application using bun
CMD ["bun", "run", "start"]
