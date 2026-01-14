# Setup Status for chat.terpedia.com

## ✅ Completed

1. **Google Cloud Platform Setup**
   - ✅ Authenticated with dan@syzygyx.com
   - ✅ Project set to terpedia
   - ✅ Cloud DNS API enabled
   - ✅ Compute Engine API enabled
   - ✅ Cloud DNS managed zone created: `terpedia-com`

2. **DNS Zone Information**
   - Zone Name: `terpedia-com`
   - DNS Name: `terpedia.com`
   - Name Servers:
     - ns-cloud-c1.googledomains.com
     - ns-cloud-c2.googledomains.com
     - ns-cloud-c3.googledomains.com
     - ns-cloud-c4.googledomains.com
   
   **⚠️ IMPORTANT:** Update your domain registrar (where terpedia.com is registered) to use these name servers.

3. **Terraform Configuration**
   - ✅ Configuration files created
   - ✅ Terraform initialized
   - ✅ Configuration validated
   - ✅ terraform.tfvars configured

## ⚠️ Next Steps Required

### 1. Set Up Application Default Credentials

Terraform needs Application Default Credentials to authenticate. Run:

```bash
gcloud auth application-default login
```

This will open a browser for authentication. After completing, run:

```bash
gcloud auth application-default set-quota-project terpedia
```

### 2. Update Domain Registrar

Update your terpedia.com domain registrar to use the Google Cloud DNS name servers:
- ns-cloud-c1.googledomains.com
- ns-cloud-c2.googledomains.com
- ns-cloud-c3.googledomains.com
- ns-cloud-c4.googledomains.com

### 3. Deploy DNS Configuration

Once Application Default Credentials are set up:

```bash
cd terraform
terraform plan
terraform apply
```

This will:
- Create a static IP address (if server_ip is empty in terraform.tfvars)
- Create an A record for chat.terpedia.com pointing to that IP

### 4. Set Up LibreChat

After DNS is configured:

```bash
# Configure environment
cp .env.example .env
nano .env  # Set OPENAI_REVERSE_PROXY=https://kb.terpedia.com/v1

# Run setup
./setup.sh
```

### 5. Set Up SSL Certificates

Once DNS is pointing to your server:

```bash
# Install certbot if needed
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

## Current Terraform Plan

When you run `terraform plan`, it will create:
- 1 static IP address (chat-terpedia-ip) in us-central1 region
- 1 DNS A record (chat.terpedia.com) pointing to that IP

## Troubleshooting

### OAuth Error
If you see `oauth2: "invalid_grant"` errors:
1. Run `gcloud auth application-default login`
2. Complete the browser authentication
3. Run `gcloud auth application-default set-quota-project terpedia`

### DNS Not Resolving
1. Verify name servers are updated at your registrar
2. Wait for DNS propagation (can take up to 48 hours)
3. Check DNS records: `gcloud dns record-sets list --zone=terpedia-com --project=terpedia`

### Static IP
If you already have a server IP, update `terraform/terraform.tfvars`:
```
server_ip = "YOUR_EXISTING_IP_ADDRESS"
```

This will skip creating a new static IP and use your existing one.
