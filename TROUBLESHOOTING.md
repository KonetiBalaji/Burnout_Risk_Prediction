# Troubleshooting Guide - Burnout Risk Prediction System
**Created by Balaji Koneti**

## Common Issues and Solutions

### 1. Docker Build Issues

#### Issue: "nginx.conf not found" error
**Problem:** Frontend Dockerfile tries to copy nginx.conf that doesn't exist locally.

**Solution:** The nginx configuration is now embedded in the Dockerfile. If you still get this error:
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

#### Issue: "Module not found" errors
**Problem:** Dependencies not installed properly.

**Solution:**
```bash
# Clean and reinstall
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### 2. Database Connection Issues

#### Issue: "MongoDB connection failed"
**Problem:** MongoDB service not running or connection string incorrect.

**Solution:**
1. Check if MongoDB container is running:
   ```bash
   docker-compose ps
   ```

2. Verify MongoDB connection string in `backend/.env`:
   ```
   MONGODB_URI=mongodb://mongodb:27017/burnout-risk-prediction
   ```

3. Check MongoDB logs:
   ```bash
   docker-compose logs mongodb
   ```

### 3. Port Conflicts

#### Issue: "Port already in use"
**Problem:** Another service is using the required ports.

**Solution:**
1. Check what's using the ports:
   ```bash
   # Windows
   netstat -ano | findstr :3000
   netstat -ano | findstr :5173
   
   # Linux/Mac
   lsof -i :3000
   lsof -i :5173
   ```

2. Stop conflicting services or change ports in `docker-compose.yml`

### 4. Frontend Build Issues

#### Issue: "Vite build failed"
**Problem:** TypeScript compilation errors or missing dependencies.

**Solution:**
1. Check frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Check TypeScript errors:
   ```bash
   npm run build
   ```

3. Clear node_modules and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

### 5. Backend API Issues

#### Issue: "Cannot connect to backend"
**Problem:** Backend service not running or CORS issues.

**Solution:**
1. Check backend logs:
   ```bash
   docker-compose logs backend
   ```

2. Verify CORS configuration in `backend/src/index.ts`

3. Test API directly:
   ```bash
   curl http://localhost:3000/api/health
   ```

### 6. ML Service Issues

#### Issue: "ML service not responding"
**Problem:** Python dependencies not installed or service not running.

**Solution:**
1. Check ML service logs:
   ```bash
   docker-compose logs ml-service
   ```

2. Verify Python dependencies in `ml/requirements.txt`

3. Test ML service directly:
   ```bash
   curl http://localhost:8000/health
   ```

## Development Workflow

### Starting Development Environment

1. **Prerequisites:**
   - Docker Desktop installed and running
   - Git installed

2. **First-time setup:**
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd burnout-risk-prediction
   
   # Copy environment file
   cp backend/env.example backend/.env
   
   # Edit configuration
   # Edit backend/.env with your settings
   ```

3. **Start services:**
   ```bash
   # Using the startup script
   ./start-dev.sh  # Linux/Mac
   start-dev.bat   # Windows
   
   # Or manually
   docker-compose up --build
   ```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: This will delete all data)
docker-compose down -v
```

### Viewing Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs ml-service
docker-compose logs mongodb
```

### Database Management

```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh

# Backup database
docker-compose exec mongodb mongodump --out /backup

# Restore database
docker-compose exec mongodb mongorestore /backup
```

## Performance Optimization

### 1. Docker Resource Allocation
- Allocate at least 4GB RAM to Docker Desktop
- Enable Docker Desktop's "Use WSL 2" on Windows

### 2. Development vs Production
- Development: Uses `docker-compose.yml`
- Production: Use `docker-compose.prod.yml` (create this file)

### 3. Caching
- Use `.dockerignore` files to exclude unnecessary files
- Leverage Docker layer caching for faster builds

## Monitoring and Debugging

### 1. Health Checks
- Backend: `http://localhost:3000/api/health`
- Frontend: `http://localhost:5173`
- ML Service: `http://localhost:8000/health`

### 2. Database Monitoring
- MongoDB Express: `http://localhost:8081` (if enabled)
- MongoDB Compass: Connect to `mongodb://localhost:27017`

### 3. Log Analysis
- Backend logs: Check `backend/logs/` directory
- Docker logs: Use `docker-compose logs`
- Application logs: Check console output

## Getting Help

1. **Check this troubleshooting guide first**
2. **Review the logs** for specific error messages
3. **Check the documentation** in the `docs/` directory
4. **Verify your environment** matches the requirements
5. **Search for similar issues** in the project repository

## Contact

For additional support, contact: **Balaji Koneti**

---

*Last updated: $(date)*
