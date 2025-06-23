# House Crush - Docker Deployment Guide

This guide explains how to deploy House Crush using Docker, including deployment to Hugging Face Spaces.

## 🐳 Docker Setup

### Prerequisites
- Docker installed on your system
- Docker Compose (optional, for local development)

### Quick Start with Docker

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd HouseCrush
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t housecrush .
   ```

3. **Run the container:**
   ```bash
   docker run -p 7860:7860 \
     -e TOGETHER_API_KEY=your_together_api_key \
     -e HUGGINGFACE_HUB_TOKEN=your_huggingface_token \
     housecrush
   ```

4. **Access the application:**
   Open your browser and go to [http://localhost:7860](http://localhost:7860)

### Using Docker Compose (Recommended for Development)

1. **Create a `.env` file with your API keys:**
   ```bash
   TOGETHER_API_KEY=your_together_api_key_here
   HUGGINGFACE_HUB_TOKEN=your_huggingface_token_here
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
   ```

2. **Start the application:**
   ```bash
   docker-compose up --build
   ```

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

## 🚀 Hugging Face Spaces Deployment

### Method 1: Using Hugging Face Spaces UI

1. **Go to [Hugging Face Spaces](https://huggingface.co/spaces)**
2. **Click "Create new Space"**
3. **Choose "Docker" as the SDK**
4. **Upload your project files or connect your GitHub repository**
5. **Configure environment variables in the Settings tab:**
   - `TOGETHER_API_KEY`
   - `HUGGINGFACE_HUB_TOKEN`
   - `GOOGLE_API_KEY`
   - `GOOGLE_SEARCH_ENGINE_ID`

### Method 2: Using GitHub Integration

1. **Push your code to GitHub**
2. **Create a new Space on Hugging Face**
3. **Connect your GitHub repository**
4. **Set environment variables in the Space settings**

### Environment Variables for Hugging Face Spaces

In your Hugging Face Space settings, add these environment variables:

```bash
TOGETHER_API_KEY=your_together_api_key
HUGGINGFACE_HUB_TOKEN=your_huggingface_token
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
FLASK_ENV=production
PORT=7860
```

## 🔧 Docker Configuration Details

### Dockerfile Features

- **Multi-stage build** for optimized image size
- **Python 3.11** for performance and compatibility
- **Playwright browsers** pre-installed for web scraping
- **Non-root user** for security
- **Health checks** for monitoring
- **Port 7860** (Hugging Face Spaces standard)

### Container Structure

```
/app/
├── app.py                 # Main Flask application
├── templates/             # HTML templates
├── data/                  # Data files
├── scripts/               # Utility scripts
├── results/               # Search results (volume mounted)
└── logs/                  # Application logs (volume mounted)
```

### Volume Mounts

- `./results:/app/results` - Persist search results
- `./logs:/app/logs` - Persist application logs

## 🛠️ Development with Docker

### Local Development

1. **Start in development mode:**
   ```bash
   docker-compose -f docker-compose.yml up --build
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f housecrush
   ```

3. **Access container shell:**
   ```bash
   docker-compose exec housecrush bash
   ```

### Production Deployment

1. **Build production image:**
   ```bash
   docker build -t housecrush:production .
   ```

2. **Run with production settings:**
   ```bash
   docker run -d \
     --name housecrush-prod \
     -p 7860:7860 \
     -e FLASK_ENV=production \
     -e TOGETHER_API_KEY=your_key \
     -e HUGGINGFACE_HUB_TOKEN=your_token \
     -v $(pwd)/results:/app/results \
     -v $(pwd)/logs:/app/logs \
     housecrush:production
   ```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using port 7860
   lsof -i :7860
   # Kill the process or use a different port
   docker run -p 7861:7860 housecrush
   ```

2. **Permission denied:**
   ```bash
   # Fix volume permissions
   sudo chown -R $USER:$USER ./results ./logs
   ```

3. **API keys not working:**
   - Verify environment variables are set correctly
   - Check API key permissions and quotas
   - Review application logs for specific errors

4. **Playwright browsers not working:**
   ```bash
   # Rebuild with fresh browsers
   docker build --no-cache -t housecrush .
   ```

### Logs and Debugging

1. **View application logs:**
   ```bash
   docker logs housecrush-prod
   ```

2. **Check container health:**
   ```bash
   docker inspect housecrush-prod | grep Health -A 10
   ```

3. **Access running container:**
   ```bash
   docker exec -it housecrush-prod bash
   ```

## 📊 Monitoring

### Health Checks

The container includes health checks that monitor:
- Application responsiveness
- Port availability
- Basic functionality

### Resource Usage

Monitor container resources:
```bash
docker stats housecrush-prod
```

## 🔒 Security Considerations

- **Non-root user**: Container runs as `appuser` (UID 1000)
- **Minimal base image**: Uses Python slim image
- **No sensitive data in image**: API keys via environment variables
- **Health checks**: Monitor application status
- **Volume isolation**: Separate data and logs

## 📝 Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TOGETHER_API_KEY` | Together AI API key | Yes | - |
| `HUGGINGFACE_HUB_TOKEN` | Hugging Face token | Yes | - |
| `GOOGLE_API_KEY` | Google Custom Search API key | No | - |
| `GOOGLE_SEARCH_ENGINE_ID` | Google Search Engine ID | No | - |
| `FLASK_ENV` | Flask environment | No | `production` |
| `PORT` | Application port | No | `7860` |
| `HOST` | Application host | No | `0.0.0.0` |

## 🚀 Performance Optimization

### Image Size Optimization

- Uses Python slim image
- Multi-stage build (if needed)
- Removes unnecessary files with `.dockerignore`

### Runtime Optimization

- Health checks for automatic restarts
- Volume mounts for data persistence
- Environment-based configuration

---

For more information, see the main [README.md](README.md) file. 