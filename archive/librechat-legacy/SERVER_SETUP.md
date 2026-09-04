# Server Setup Guide

## ✅ Server Created Successfully

- **Instance Name**: `chat-server`
- **Zone**: `us-central1-a`
- **IP Address**: `104.197.255.123` (static IP)
- **Status**: Running
- **Machine Type**: e2-medium
- **OS**: Ubuntu 22.04 LTS
- **Docker**: Pre-installed via startup script

## Manual Setup Instructions

Since there are permission restrictions for automated deployment, follow these steps to complete the setup:

### 1. Connect to the Server

```bash
gcloud compute ssh chat-server --zone=us-central1-a --project=terpedia
```

If you get permission errors, you may need to:
- Grant yourself Compute Instance Admin role, or
- Use a service account with proper permissions

### 2. Once Connected, Set Up LibreChat

```bash
# Create directory
mkdir -p ~/chat.terpedia.com
cd ~/chat.terpedia.com

# Copy files from your local machine (run from your local terminal):
# gcloud compute scp docker-compose.yml .env.example chat-server:~/chat.terpedia.com/ --zone=us-central1-a --project=terpedia
# gcloud compute scp --recurse nginx/ chat-server:~/chat.terpedia.com/ --zone=us-central1-a --project=terpedia
```

Or manually create the files on the server:

#### Create docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
# Docker Compose configuration for LibreChat on chat.terpedia.com

services:
  api:
    container_name: LibreChat
    ports:
      - "3080:3080"
    depends_on:
      - mongodb
      - rag_api
    image: ghcr.io/danny-avila/librechat-dev:latest
    restart: always
    environment:
      - HOST=0.0.0.0
      - MONGO_URI=mongodb://mongodb:27017/LibreChat
      - MEILI_HOST=http://meilisearch:7700
      - RAG_PORT=8000
      - RAG_API_URL=http://rag_api:8000
    volumes:
      - type: bind
        source: ./.env
        target: /app/.env
      - ./images:/app/client/public/images
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    networks:
      - librechat-network

  mongodb:
    container_name: chat-mongodb
    image: mongo:latest
    restart: always
    volumes:
      - ./data-node:/data/db
    command: mongod --noauth
    networks:
      - librechat-network

  meilisearch:
    container_name: chat-meilisearch
    image: getmeili/meilisearch:v1.12.3
    restart: always
    environment:
      - MEILI_HOST=http://meilisearch:7700
      - MEILI_NO_ANALYTICS=true
      - MEILI_MASTER_KEY=${MEILI_MASTER_KEY}
    volumes:
      - ./meili_data_v1.12:/meili_data
    networks:
      - librechat-network

  vectordb:
    container_name: vectordb
    image: pgvector/pgvector:0.8.0-pg15-trixie
    environment:
      POSTGRES_DB: mydatabase
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    restart: always
    volumes:
      - pgdata2:/var/lib/postgresql/data
    networks:
      - librechat-network

  rag_api:
    container_name: rag_api
    image: ghcr.io/danny-avila/librechat-rag-api-dev-lite:latest
    environment:
      - DB_HOST=vectordb
      - RAG_PORT=8000
    restart: always
    depends_on:
      - vectordb
    env_file:
      - .env
    networks:
      - librechat-network

  nginx:
    container_name: chat-nginx
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - librechat-network

volumes:
  pgdata2:

networks:
  librechat-network:
    driver: bridge
EOF
```

#### Create .env file

```bash
cat > .env << 'EOF'
HOST=0.0.0.0
PORT=3080

MONGO_URI=mongodb://mongodb:27017/LibreChat

DOMAIN_CLIENT=https://chat.terpedia.com
DOMAIN_SERVER=https://chat.terpedia.com

NO_INDEX=false
TRUST_PROXY=1

DEBUG_LOGGING=true
DEBUG_CONSOLE=false

ENDPOINTS=openAI

OPENAI_API_KEY=user_provided
OPENAI_REVERSE_PROXY=https://kb.terpedia.com/v1
OPENAI_MODELS=gpt-4o,gpt-4o-mini,gpt-4-turbo,gpt-3.5-turbo

SEARCH=true
MEILI_NO_ANALYTICS=true
MEILI_HOST=http://meilisearch:7700
MEILI_MASTER_KEY=$(openssl rand -hex 32)

ALLOW_EMAIL_LOGIN=true
ALLOW_REGISTRATION=true
ALLOW_SOCIAL_LOGIN=false
ALLOW_SOCIAL_REGISTRATION=false
ALLOW_PASSWORD_RESET=true
ALLOW_UNVERIFIED_EMAIL_LOGIN=true

SESSION_EXPIRY=1000 * 60 * 15
REFRESH_TOKEN_EXPIRY=(1000 * 60 * 60 * 24) * 7

JWT_SECRET=$(openssl rand -hex 32)
JWT_REFRESH_SECRET=$(openssl rand -hex 32)

CREDS_KEY=f34be427ebb29de8d88c107a71546019685ed8b241d8f2ed00c3df97ad2566f0
CREDS_IV=e2341419ec3dd3d19b13a1a87fafcbfb

RAG_PORT=8000

APP_TITLE=Terpedia Chat
HELP_AND_FAQ_URL=https://terpedia.com
EOF

# Generate secure keys
MEILI_KEY=$(openssl rand -hex 32)
JWT_KEY=$(openssl rand -hex 32)
JWT_REFRESH_KEY=$(openssl rand -hex 32)

sed -i "s|MEILI_MASTER_KEY=\$(openssl rand -hex 32)|MEILI_MASTER_KEY=$MEILI_KEY|g" .env
sed -i "s|JWT_SECRET=\$(openssl rand -hex 32)|JWT_SECRET=$JWT_KEY|g" .env
sed -i "s|JWT_REFRESH_SECRET=\$(openssl rand -hex 32)|JWT_REFRESH_SECRET=$JWT_REFRESH_KEY|g" .env
```

#### Create nginx directory and config

```bash
mkdir -p nginx/ssl

cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=30r/s;

    upstream librechat_api {
        server api:3080;
    }

    server {
        listen 80;
        server_name chat.terpedia.com;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    server {
        listen 443 ssl http2;
        server_name chat.terpedia.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        client_max_body_size 100M;

        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        location / {
            limit_req zone=general_limit burst=20 nodelay;
            proxy_pass http://librechat_api;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        location /api/ {
            limit_req zone=api_limit burst=10 nodelay;
            proxy_pass http://librechat_api;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        location /socket.io/ {
            proxy_pass http://librechat_api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
EOF
```

### 3. Create Required Directories

```bash
mkdir -p images uploads logs data-node meili_data_v1.12
```

### 4. Start Services

```bash
# Pull images
docker-compose pull

# Start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### 5. Set Up SSL Certificates

```bash
# Install certbot
sudo apt-get update
sudo apt-get install -y certbot

# Stop nginx temporarily
docker-compose stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d chat.terpedia.com

# Copy certificates
sudo cp /etc/letsencrypt/live/chat.terpedia.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/chat.terpedia.com/privkey.pem nginx/ssl/
sudo chmod 644 nginx/ssl/fullchain.pem
sudo chmod 600 nginx/ssl/privkey.pem
sudo chown $USER:$USER nginx/ssl/*.pem

# Restart services
docker-compose up -d
```

### 6. Set Up Auto-Renewal

```bash
sudo tee /etc/cron.monthly/renew-chat-terpedia-cert > /dev/null << 'EOF'
#!/bin/bash
certbot renew --quiet --deploy-hook "cd /home/$USER/chat.terpedia.com && sudo cp /etc/letsencrypt/live/chat.terpedia.com/fullchain.pem nginx/ssl/ && sudo cp /etc/letsencrypt/live/chat.terpedia.com/privkey.pem nginx/ssl/ && sudo chmod 644 nginx/ssl/fullchain.pem && sudo chmod 600 nginx/ssl/privkey.pem && sudo chown $USER:$USER nginx/ssl/*.pem && docker-compose restart nginx"
EOF

sudo chmod +x /etc/cron.monthly/renew-chat-terpedia-cert
```

## Alternative: Fix Permissions

If you want to use automated deployment, grant yourself the necessary permissions:

```bash
# Grant Compute Instance Admin role
gcloud projects add-iam-policy-binding terpedia \
    --member="user:dan@syzygyx.com" \
    --role="roles/compute.instanceAdmin"
```

Then you can use the deployment scripts:
- `./scripts/deploy-to-server.sh`
- `./scripts/setup-ssl.sh`

## Verification

After setup, verify everything is working:

```bash
# Check services
docker-compose ps

# Check logs
docker-compose logs api

# Test HTTP (should redirect to HTTPS)
curl -I http://chat.terpedia.com

# Test HTTPS
curl -I https://chat.terpedia.com
```

## Server Information

- **IP**: 104.197.255.123
- **Domain**: chat.terpedia.com
- **SSH**: `gcloud compute ssh chat-server --zone=us-central1-a --project=terpedia`
- **Firewall**: Ports 80 and 443 are open

## Troubleshooting

### Permission Errors
- Grant yourself Compute Instance Admin role (see above)
- Or use manual setup instructions

### Docker Issues
- Check Docker is running: `sudo systemctl status docker`
- Add user to docker group: `sudo usermod -aG docker $USER` (then logout/login)

### SSL Certificate Issues
- Ensure DNS is resolving correctly first
- Verify port 80 is accessible (required for Let's Encrypt)
- Check certificate files: `ls -la nginx/ssl/`

### Services Not Starting
- Check logs: `docker-compose logs`
- Verify .env file is correct
- Ensure all directories exist and have proper permissions
