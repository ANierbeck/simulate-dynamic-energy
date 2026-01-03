# 🐳 Docker Deployment for Dynamic Energy Analysis

This guide helps you deploy the Dynamic Energy Analysis application using Docker on your Raspberry Pi or any other system.

## 🚀 Quick Start

### 1. Build and Run with Docker Compose

```bash
# Build the image
docker-compose build

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f
```

### 2. Access the Application

After starting, the application will be available at:
- **URL**: `http://your-raspberry-pi:8501`
- **Port**: 8501 (configurable in docker-compose.yml)

## 📋 Configuration

### Environment Variables

Create a `.env` file in the same directory as `docker-compose.yml`:

```env
# InfluxDB Configuration
INFLUXDB_URL=http://your-influxdb-server:8086
INFLUXDB_TOKEN=your_influxdb_token
INFLUXDB_ORG=your_organization
INFLUXDB_BUCKET=your_bucket

# Application Settings
CURRENT_TARIFF=0.30
TIMEZONE=Europe/Berlin
```

### Docker Compose Configuration

Edit `docker-compose.yml` to match your setup:
- Change port mappings if needed
- Adjust volume mounts for data persistence
- Set environment variables

## 🐋 Raspberry Pi Specific Notes

### ARM Compatibility

The provided `Dockerfile` uses `python:3.11-slim` which works on most systems. For Raspberry Pi (ARM), you have two options:

#### Option 1: Use Multi-Arch Build (Recommended)
```bash
# Build for ARM
docker buildx build --platform linux/arm/v7 -t energy-analysis-arm .

# Run
docker run -d -p 8501:8501 --name energy-analysis energy-analysis-arm
```

#### Option 2: Use ARM-Specific Image
Uncomment the alternative service in `docker-compose.yml` and use:
```yaml
image: arm32v7/python:3.11-slim
```

### Performance Tips

1. **Use volume mounts** for data persistence
2. **Limit memory usage** if running on low-end Raspberry Pi
3. **Use `--restart unless-stopped`** for automatic recovery
4. **Monitor container logs** for performance issues

## 🔄 Updates

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Updating Dependencies

```bash
# Update requirements.txt and rebuild
docker-compose build --no-cache
```

## 📊 Monitoring

### View Logs
```bash
docker-compose logs -f
docker logs dynamic-energy-analysis -f
```

### Check Container Status
```bash
docker ps
docker-compose ps
```

### Health Check
```bash
docker-compose exec energy-analysis curl -f http://localhost:8501 || echo "Not healthy"
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find and kill process using port 8501
sudo lsof -i :8501
kill -9 <PID>
```

#### 2. InfluxDB Connection Issues
```bash
# Test connection from container
docker-compose exec energy-analysis curl -v http://your-influxdb-server:8086/ping
```

#### 3. Permission Issues
```bash
# Ensure data directory has correct permissions
chmod -R 755 ./data
chown -R 1000:1000 ./data
```

#### 4. ARM Compatibility Issues
```bash
# Use ARM-specific image
sed -i 's/python:3.11-slim/arm32v7\/python:3.11-slim/' Dockerfile
docker-compose build --no-cache
```

## 📈 Deployment Strategies

### Production Deployment
```bash
# Use proper logging
docker-compose up -d

# Set up log rotation
# Add to your crontab:
# 0 0 * * * docker system prune -f
```

### Development Deployment
```bash
# Mount code as volume for live updates
docker-compose down
docker-compose up --build
```

## 🎯 Best Practices

1. **Use environment variables** for sensitive data
2. **Enable health checks** for automatic monitoring
3. **Use volumes** for data persistence
4. **Set resource limits** for Raspberry Pi
5. **Monitor container performance**
6. **Regularly update** dependencies
7. **Backup your data** regularly

## 🔒 Security

1. **Never commit `.env` files** with real credentials
2. **Use Docker secrets** for production
3. **Keep containers updated**
4. **Limit container permissions**
5. **Use network isolation**

---

**🚀 Happy Dockerizing!**

For Raspberry Pi specific questions, check the [Raspberry Pi Docker documentation](https://www.raspberrypi.com/documentation/computers/software.html#docker).