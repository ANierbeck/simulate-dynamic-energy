# Docker Deployment Options

This guide explains the different ways to deploy the Dynamic Energy Analysis application using Docker.

## 📦 Deployment Options

### 1. Local Development (Build from Source)

Use this for development and testing:

```bash
# Build and run locally
docker-compose up -d

# Or build and run manually
docker build -t dynamic-energy-analysis .
docker run -d -p 8501:8501 --name dynamic-energy-analysis dynamic-energy-analysis
```

**File**: `docker-compose.yml`
- Builds the image from the local Dockerfile
- Good for development and testing changes
- Requires all source code to be present

### 2. Production Deployment (Use Pre-built Image)

Use this for production deployments:

```bash
# Pull and run the pre-built image from GHCR
docker-compose -f docker-compose.ghcr.yml up -d

# Or pull and run manually
docker pull ghcr.io/anierbeck/simulate-dynamic-energy:latest
docker run -d -p 8501:8501 --name dynamic-energy-analysis ghcr.io/anierbeck/simulate-dynamic-energy:latest
```

**File**: `docker-compose.ghcr.yml`
- Uses the pre-built image from GitHub Container Registry
- No need for source code (just the compose file)
- Automatically updated when new versions are pushed
- Recommended for production

### 3. Specific Version Deployment

To use a specific version (by commit SHA):

```bash
# Use a specific version
docker pull ghcr.io/anierbeck/simulate-dynamic-energy:abc1234
docker run -d -p 8501:8501 --name dynamic-energy-analysis ghcr.io/anierbeck/simulate-dynamic-energy:abc1234
```

Replace `abc1234` with the actual commit SHA you want to deploy.

## 🔧 Configuration

Both deployment methods support the same environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TZ` | Timezone | `Europe/Berlin` |
| `INFLUXDB_URL` | InfluxDB server URL | `http://your-influxdb-server:8086` |
| `INFLUXDB_TOKEN` | InfluxDB authentication token | (required) |
| `INFLUXDB_ORG` | InfluxDB organization | `homeassistant` |
| `INFLUXDB_BUCKET` | InfluxDB bucket | `homeassistant` |
| `CURRENT_TARIFF` | Current electricity tariff in €/kWh | `0.30` |

## 🐳 Docker Commands Cheat Sheet

### Build and Run
```bash
# Build image
docker build -t dynamic-energy-analysis .

# Run container
docker run -d -p 8501:8501 --name dynamic-energy-analysis dynamic-energy-analysis

# Run with environment variables
docker run -d -p 8501:8501 \
  --name dynamic-energy-analysis \
  -e INFLUXDB_TOKEN="your-token" \
  -e INFLUXDB_URL="http://influxdb:8086" \
  dynamic-energy-analysis
```

### Management
```bash
# Stop container
docker stop dynamic-energy-analysis

# Start container
docker start dynamic-energy-analysis

# Restart container
docker restart dynamic-energy-analysis

# Remove container
docker rm dynamic-energy-analysis

# Remove image
docker rmi dynamic-energy-analysis

# View logs
docker logs dynamic-energy-analysis

# View logs with follow
docker logs -f dynamic-energy-analysis
```

### Updates
```bash
# Pull latest image (GHCR version)
docker pull ghcr.io/anierbeck/simulate-dynamic-energy:latest

# Recreate container with new image
docker stop dynamic-energy-analysis
docker rm dynamic-energy-analysis
docker run -d -p 8501:8501 --name dynamic-energy-analysis ghcr.io/anierbeck/simulate-dynamic-energy:latest
```

## 📱 Raspberry Pi Deployment

For Raspberry Pi (ARM architecture), you have two options:

### Option 1: Use the standard image (recommended)
The standard image should work on most Raspberry Pi models with Docker installed.

### Option 2: Build specifically for ARM
Uncomment the alternative service in the docker-compose files and use:
```yaml
energy-analysis-arm:
  image: arm32v7/python:3.11-slim
  container_name: dynamic-energy-analysis-arm
  # ... rest of configuration
```

## 🌐 Accessing the Application

After deployment, access the application at:
- **Local**: `http://localhost:8501`
- **Network**: `http://your-server-ip:8501`

## 🔒 Security Notes

1. **Environment Variables**: Never commit secrets to version control
2. **Use .env files**: Create a `.env` file for sensitive data
3. **Network Security**: Consider using a reverse proxy with HTTPS
4. **Updates**: Regularly pull new images for security updates

## 🚀 Recommended Workflow

1. **Development**: Use `docker-compose.yml` (build from source)
2. **Testing**: Use specific commit versions for testing
3. **Production**: Use `docker-compose.ghcr.yml` (pre-built images)
4. **Updates**: Pull latest image and recreate container