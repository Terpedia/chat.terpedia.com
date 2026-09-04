# LibreChat Setup for chat.terpedia.com

This repository contains the configuration and deployment setup for LibreChat running on chat.terpedia.com, configured to use the OpenAI endpoint at kb.terpedia.com.

## Prerequisites

- Docker and Docker Compose installed
- Domain name: chat.terpedia.com
- Google Cloud Platform account (dan@syzygyx.com) with terpedia project
- Access to Google Cloud DNS for DNS configuration
- SSL certificates for HTTPS (Let's Encrypt recommended)
- OpenAI-compatible API endpoint at kb.terpedia.com

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a step-by-step guide.

**Prerequisites:**
- ✅ Authenticated with `gcloud auth login dan@syzygyx.com`
- ✅ Project set to terpedia

**Quick setup:**

1. **Complete Google Cloud setup:**
   ```bash
   ./scripts/complete-gcloud-setup.sh
   ```

2. **Configure and deploy DNS:**
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your DNS zone name
   ../scripts/deploy-dns.sh
   ```

3. **Set up LibreChat:**
   ```bash
   cp .env.example .env
   # Edit .env - set OPENAI_REVERSE_PROXY=https://kb.terpedia.com/v1
   ./setup.sh
   ```

## Configuration

### Environment Variables

Key configuration in `.env`:

- `DOMAIN_CLIENT` and `DOMAIN_SERVER`: Set to `https://chat.terpedia.com`
- `OPENAI_REVERSE_PROXY`: Set to `https://kb.terpedia.com/v1` to use the kb.terpedia.com endpoint
- `OPENAI_API_KEY`: Users will provide their own API keys
- `MEILI_MASTER_KEY`: Generate a secure key for Meilisearch

### OpenAI Endpoint Configuration

LibreChat is configured to use `kb.terpedia.com` as the OpenAI reverse proxy endpoint. This means:

- All OpenAI API requests will be routed through `https://kb.terpedia.com/v1`
- The endpoint should be compatible with OpenAI's API format
- Users can provide their own API keys through the LibreChat interface

### DNS Configuration

The Google Cloud DNS configuration in `terraform/dns.tf` sets up:

- A record for `chat.terpedia.com`
- Static IP address (if not providing existing IP)
- Optional Load Balancer support (commented out, uncomment if needed)

**To configure DNS:**

1. Ensure you're authenticated: `gcloud auth login dan@syzygyx.com`
2. Set the project: `gcloud config set project terpedia`
3. Update `terraform/terraform.tfvars` with your configuration:
   - `dns_zone_name`: Name of your Cloud DNS managed zone (e.g., "terpedia-com")
   - `server_ip`: Leave empty to create new static IP, or provide existing IP
4. Run `./scripts/deploy-dns.sh` or `terraform apply` to create the DNS records

**Note:** Ensure the Cloud DNS managed zone for terpedia.com exists before deploying.

## Services

The Docker Compose setup includes:

- **LibreChat API**: Main application server
- **MongoDB**: Database for user data and conversations
- **Meilisearch**: Search functionality
- **VectorDB (PostgreSQL with pgvector)**: Vector database for RAG
- **RAG API**: Retrieval Augmented Generation API
- **Nginx**: Reverse proxy with SSL termination

## Ports

- `80`: HTTP (redirects to HTTPS)
- `443`: HTTPS
- `3080`: LibreChat API (internal, proxied through Nginx)

## Maintenance

### View logs:
```bash
docker-compose logs -f api
```

### Restart services:
```bash
docker-compose restart
```

### Update LibreChat:
```bash
docker-compose pull
docker-compose up -d
```

### Backup MongoDB:
```bash
docker exec chat-mongodb mongodump --out /data/db/backup
```

## Security Notes

1. **SSL Certificates**: Ensure SSL certificates are properly configured and auto-renewed
2. **API Keys**: Users provide their own API keys - no keys are stored in the environment
3. **Firewall**: Ensure only ports 80 and 443 are exposed to the internet
4. **Rate Limiting**: Nginx is configured with rate limiting to prevent abuse
5. **Security Headers**: Security headers are configured in the Nginx configuration

## Troubleshooting

### LibreChat not connecting to kb.terpedia.com

1. Verify `OPENAI_REVERSE_PROXY` is set correctly in `.env`
2. Check that kb.terpedia.com is accessible and responding to OpenAI API requests
3. Check LibreChat logs: `docker-compose logs api`

### DNS not resolving

1. Verify Cloud DNS records are created: `terraform show`
2. Check DNS propagation: `dig chat.terpedia.com`
3. Verify Cloud DNS managed zone exists: `gcloud dns managed-zones list`
4. Ensure the server IP or static IP is correct

### SSL certificate issues

1. Verify certificates are in `nginx/ssl/` directory
2. Check Nginx logs: `docker-compose logs nginx`
3. Ensure certificates are valid and not expired

## Support

For LibreChat-specific issues, refer to the [LibreChat documentation](https://www.librechat.ai/docs).

For infrastructure issues, check the Terraform and Docker Compose configurations.
