# Fixing 503 Errors in LibreChat

## Error Symptoms
- 503 errors on `/api/user` and `/api/admin` endpoints
- LibreChat UI not loading properly
- Service unavailable errors

## Common Causes

1. **LibreChat container not running**
2. **Port 3080 not accessible**
3. **Nginx proxy misconfiguration**
4. **Database connection issues**
5. **Service crash or restart loop**

## Troubleshooting Steps

### 1. Check Service Status
```bash
gcloud compute ssh chat-server --zone=us-central1-a --project=terpedia
cd ~/chat.terpedia.com
sudo docker-compose ps
```

All services should show "Up" status.

### 2. Check LibreChat Logs
```bash
sudo docker logs LibreChat --tail=50
```

Look for:
- Port binding errors
- Database connection errors
- Application crashes
- Startup errors

### 3. Restart Services
```bash
sudo docker-compose restart
# Wait 30 seconds
sudo docker-compose ps
```

### 4. Check Port Accessibility
```bash
# From inside container
sudo docker exec LibreChat curl http://localhost:3080/api/health

# From host
curl http://localhost:3080/api/health
```

### 5. Check Nginx Configuration
```bash
sudo docker logs chat-nginx --tail=50
sudo docker exec chat-nginx nginx -t
```

### 6. Verify Database Connections
```bash
sudo docker-compose ps mongodb
sudo docker logs chat-mongodb --tail=20
```

## Quick Fix

If services are down:
```bash
cd ~/chat.terpedia.com
sudo docker-compose down
sudo docker-compose up -d
sleep 30
sudo docker-compose ps
```

## Expected Status

After restart, all services should be:
- ✅ LibreChat: Up
- ✅ MongoDB: Up
- ✅ Meilisearch: Up
- ✅ VectorDB: Up
- ✅ RAG API: Up
- ✅ Nginx: Up

## Verification

Once services are up:
```bash
# Test API endpoint
curl https://chat.terpedia.com/api/user

# Check LibreChat health
curl http://localhost:3080/api/health
```

## If Issues Persist

1. Check disk space: `df -h`
2. Check memory: `free -h`
3. Check Docker: `sudo systemctl status docker`
4. Review all logs: `sudo docker-compose logs`
