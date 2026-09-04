# Deployment Complete! ✅

## Successfully Deployed

### 1. Google Cloud Infrastructure ✅

- **Static IP Address Created**: `104.197.255.123`
  - Resource: `chat-terpedia-ip`
  - Region: `us-central1`
  - Project: `terpedia`

- **DNS Record Created**: `chat.terpedia.com` → `104.197.255.123`
  - Type: A record
  - TTL: 300 seconds
  - Zone: `terpedia-com`

### 2. DNS Configuration ✅

Current DNS records in `terpedia-com` zone:
```
chat.terpedia.com.  A  104.197.255.123  TTL: 300
```

### 3. Name Servers (Update Your Registrar) ⚠️

**IMPORTANT:** Update your terpedia.com domain registrar to use these Google Cloud DNS name servers:

- `ns-cloud-c1.googledomains.com`
- `ns-cloud-c2.googledomains.com`
- `ns-cloud-c3.googledomains.com`
- `ns-cloud-c4.googledomains.com`

Once updated, DNS propagation typically takes 15 minutes to 48 hours.

## Next Steps

### 1. Verify DNS Propagation

After updating name servers, verify DNS is working:

```bash
dig chat.terpedia.com
nslookup chat.terpedia.com
```

You should see: `104.197.255.123`

### 2. Set Up Your Server

Point your server to use the static IP `104.197.255.123`. You can:

**Option A: If using Google Compute Engine**
- Create a VM instance and assign the static IP:
  ```bash
  gcloud compute instances create chat-server \
    --zone=us-central1-a \
    --address=104.197.255.123 \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-medium \
    --project=terpedia
  ```

**Option B: If using an existing server**
- Configure your server's network to use the static IP `104.197.255.123`
- Or set up port forwarding/NAT to route traffic to your server

### 3. Set Up LibreChat

Once your server is accessible at `104.197.255.123`:

```bash
cd /Users/danielmcshan/GitHub/chat.terpedia.com

# Configure environment
cp .env.example .env
nano .env  # Edit and set:
           # - OPENAI_REVERSE_PROXY=https://kb.terpedia.com/v1
           # - DOMAIN_CLIENT=https://chat.terpedia.com
           # - DOMAIN_SERVER=https://chat.terpedia.com

# Run setup
./setup.sh
```

### 4. Set Up SSL Certificates

Once DNS is pointing to your server and it's accessible:

```bash
# Install certbot if needed
sudo apt-get update
sudo apt-get install certbot

# Stop nginx temporarily
docker-compose stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d chat.terpedia.com

# Copy certificates
sudo cp /etc/letsencrypt/live/chat.terpedia.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/chat.terpedia.com/privkey.pem nginx/ssl/
sudo chmod 644 nginx/ssl/fullchain.pem
sudo chmod 600 nginx/ssl/privkey.pem

# Restart services
docker-compose up -d
```

### 5. Configure Firewall

Ensure your server allows traffic on ports 80 and 443:

```bash
# If using GCP, create firewall rules:
gcloud compute firewall-rules create allow-http-https \
  --allow tcp:80,tcp:443 \
  --source-ranges 0.0.0.0/0 \
  --target-tags chat-server \
  --project=terpedia
```

## Current Infrastructure

- **Static IP**: `104.197.255.123` (reserved in us-central1)
- **DNS Record**: `chat.terpedia.com` → `104.197.255.123`
- **DNS Zone**: `terpedia-com` (Google Cloud DNS)

## Verification Commands

```bash
# Check static IP
gcloud compute addresses describe chat-terpedia-ip --region=us-central1 --project=terpedia

# Check DNS records
gcloud dns record-sets list --zone=terpedia-com --project=terpedia

# Test DNS resolution (after name servers are updated)
dig chat.terpedia.com
nslookup chat.terpedia.com
```

## Troubleshooting

### DNS Not Resolving
1. Verify name servers are updated at your registrar
2. Wait for DNS propagation (can take up to 48 hours)
3. Check: `dig chat.terpedia.com @ns-cloud-c1.googledomains.com`

### Server Not Accessible
1. Verify firewall rules allow ports 80 and 443
2. Check if server is running and listening on those ports
3. Test: `curl http://104.197.255.123`

### SSL Certificate Issues
1. Ensure DNS is resolving correctly first
2. Verify port 80 is accessible (required for Let's Encrypt validation)
3. Check certificate files exist: `ls -la nginx/ssl/`

## Summary

✅ Static IP created: `104.197.255.123`
✅ DNS A record created: `chat.terpedia.com` → `104.197.255.123`
⚠️  **Action Required**: Update domain registrar with Google Cloud DNS name servers
📋 Next: Set up server, configure LibreChat, and obtain SSL certificates
