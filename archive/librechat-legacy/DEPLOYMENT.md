# Deployment Guide for chat.terpedia.com

This guide walks you through deploying LibreChat on chat.terpedia.com with Route 53 DNS configuration.

## Prerequisites

1. **Google Cloud Platform Account**: dan@syzygyx.com with access to terpedia project
2. **Domain**: terpedia.com must have a managed zone in Google Cloud DNS
3. **Server**: A server with Docker installed (can be GCE, VPS, etc.)
4. **SSL Certificates**: Let's Encrypt or other SSL certificate provider
5. **OpenAI Endpoint**: kb.terpedia.com must be accessible and serving OpenAI-compatible API
6. **gcloud CLI**: Installed and configured

## Step 1: Server Setup

### 1.1 Install Docker and Docker Compose

```bash
# On Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 1.2 Clone and Configure

```bash
cd /opt  # or your preferred directory
git clone <your-repo-url> chat.terpedia.com
cd chat.terpedia.com

# Copy and edit environment file
cp .env.example .env
nano .env  # Edit with your configuration
```

**Important configuration in `.env`:**
- Set `DOMAIN_CLIENT=https://chat.terpedia.com`
- Set `DOMAIN_SERVER=https://chat.terpedia.com`
- Set `OPENAI_REVERSE_PROXY=https://kb.terpedia.com/v1`
- Generate secure keys for `MEILI_MASTER_KEY`, `JWT_SECRET`, `JWT_REFRESH_SECRET`

### 1.3 Run Setup Script

```bash
./setup.sh
```

This will:
- Create necessary directories
- Generate Meilisearch master key if needed
- Pull Docker images
- Start services

## Step 2: SSL Certificate Setup

### 2.1 Using Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Stop nginx temporarily if running
docker-compose stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d chat.terpedia.com

# Copy certificates to nginx/ssl/
sudo cp /etc/letsencrypt/live/chat.terpedia.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/chat.terpedia.com/privkey.pem nginx/ssl/
sudo chmod 644 nginx/ssl/fullchain.pem
sudo chmod 600 nginx/ssl/privkey.pem

# Set up auto-renewal
sudo certbot renew --dry-run
```

### 2.2 Using Existing Certificates

If you have existing SSL certificates:

```bash
cp /path/to/your/fullchain.pem nginx/ssl/
cp /path/to/your/privkey.pem nginx/ssl/
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem
```

## Step 3: Google Cloud Setup and DNS Configuration

### 3.1 Set Up Google Cloud Authentication

```bash
# Run the setup script
./scripts/setup-gcloud.sh

# Or manually:
gcloud auth login dan@syzygyx.com
gcloud config set project terpedia
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
gcloud auth application-default login
```

### 3.2 Verify Cloud DNS Managed Zone

Ensure the managed zone for terpedia.com exists:

```bash
gcloud dns managed-zones list
```

If it doesn't exist, create it:

```bash
gcloud dns managed-zones create terpedia-com \
    --dns-name=terpedia.com \
    --description="DNS zone for terpedia.com" \
    --project=terpedia
```

Note the zone name (e.g., "terpedia-com") for the next step.

### 3.3 Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

Update with your values:
```hcl
gcp_project_id = "terpedia"
gcp_region     = "us-central1"
gcp_zone       = "us-central1-a"
dns_zone_name  = "terpedia-com"  # Name from step 3.2
server_ip      = ""  # Leave empty to create new static IP, or provide existing IP
environment    = "production"
domain_name    = "chat.terpedia.com"
```

### 3.4 Deploy DNS Configuration

```bash
# Option 1: Use the deployment script
../scripts/deploy-dns.sh

# Option 2: Manual deployment
terraform init
terraform plan
terraform apply
```

### 3.5 Verify DNS

After deployment, verify DNS is working:

```bash
dig chat.terpedia.com
nslookup chat.terpedia.com
```

DNS propagation can take a few minutes to several hours.

## Step 4: Start Services

```bash
cd /opt/chat.terpedia.com  # or your installation directory
docker-compose up -d
```

Check logs:

```bash
docker-compose logs -f
```

## Step 5: Verify Deployment

1. **Check services are running:**
   ```bash
   docker-compose ps
   ```

2. **Test HTTP redirect:**
   ```bash
   curl -I http://chat.terpedia.com
   # Should return 301 redirect to HTTPS
   ```

3. **Test HTTPS:**
   ```bash
   curl -I https://chat.terpedia.com
   # Should return 200 OK
   ```

4. **Access LibreChat:**
   - Open https://chat.terpedia.com in your browser
   - You should see the LibreChat interface

## Step 6: Configure OpenAI Endpoint

1. In LibreChat, go to Settings
2. Add an OpenAI endpoint
3. Set the base URL to: `https://kb.terpedia.com/v1`
4. Users can provide their own API keys

## Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Check if ports are in use
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

### SSL certificate errors

- Verify certificates are in `nginx/ssl/`
- Check file permissions
- Ensure certificates are not expired
- Verify domain matches certificate

### DNS not resolving

- Check Cloud DNS records: `terraform show` or `gcloud dns record-sets list --zone=terpedia-com`
- Verify Cloud DNS managed zone exists: `gcloud dns managed-zones list`
- Verify server IP is correct
- Wait for DNS propagation (can take up to 48 hours)
- Check firewall allows traffic on ports 80 and 443
- Verify you're authenticated: `gcloud auth list`

### LibreChat can't connect to kb.terpedia.com

- Verify `OPENAI_REVERSE_PROXY` in `.env`
- Test kb.terpedia.com endpoint:
  ```bash
  curl https://kb.terpedia.com/v1/models
  ```
- Check LibreChat logs: `docker-compose logs api`

## Maintenance

### Update LibreChat

```bash
docker-compose pull
docker-compose up -d
```

### Backup MongoDB

```bash
docker exec chat-mongodb mongodump --out /data/db/backup/$(date +%Y%m%d)
```

### Renew SSL Certificates

```bash
sudo certbot renew
sudo cp /etc/letsencrypt/live/chat.terpedia.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/chat.terpedia.com/privkey.pem nginx/ssl/
docker-compose restart nginx
```

## Security Checklist

- [ ] SSL certificates installed and auto-renewing
- [ ] Firewall configured (only ports 80, 443 open)
- [ ] Strong passwords/keys in `.env`
- [ ] Regular backups configured
- [ ] Monitoring and logging set up
- [ ] Rate limiting enabled (configured in nginx.conf)
- [ ] Security headers enabled (configured in nginx.conf)

## Notes

- **Google Cloud Platform**: Using GCP with dan@syzygyx.com account and terpedia project
- **Cloud DNS**: Using Google Cloud DNS instead of AWS Route 53
- **OpenAI Endpoint**: The setup assumes kb.terpedia.com serves an OpenAI-compatible API at `/v1` endpoint
- **Load Balancer**: For production, consider using a Google Cloud Load Balancer instead of a static IP (see commented sections in dns.tf)
- **Static IP**: If you provide an existing `server_ip`, Terraform will use it. Otherwise, it will create a new static IP address.
