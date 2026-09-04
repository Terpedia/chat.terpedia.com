# Quick Start Guide - chat.terpedia.com

## Current Status ✅

- ✅ Authenticated with dan@syzygyx.com
- ✅ Project set to terpedia
- ✅ Cloud DNS API enabled
- ✅ Compute Engine API enabled
- ⚠️  Application Default Credentials need setup (for Terraform)
- ⚠️  Cloud DNS managed zone needs to be created

## Next Steps

### 1. Set up Application Default Credentials

This is required for Terraform to authenticate with Google Cloud:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project terpedia
```

### 2. Create Cloud DNS Managed Zone (if needed)

If you don't have a managed zone for terpedia.com yet:

```bash
gcloud dns managed-zones create terpedia-com \
    --dns-name=terpedia.com \
    --description="DNS zone for terpedia.com" \
    --project=terpedia
```

**Important:** After creating the zone, update your domain registrar with the name servers shown by the command above.

### 3. Run Complete Setup Script

```bash
./scripts/complete-gcloud-setup.sh
```

This will:
- Verify your setup
- Set up Application Default Credentials
- Check/create DNS managed zone
- Guide you through any remaining steps

### 4. Configure Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

Update with your DNS zone name (e.g., `dns_zone_name = "terpedia-com"`)

### 5. Deploy DNS Configuration

```bash
./scripts/deploy-dns.sh
```

### 6. Set up LibreChat

```bash
# Copy and configure environment
cp .env.example .env
nano .env  # Set OPENAI_REVERSE_PROXY=https://kb.terpedia.com/v1

# Run setup
./setup.sh
```

## Verify Setup

Check your Google Cloud configuration:

```bash
./scripts/check-gcloud-setup.sh
```

## Troubleshooting

### Application Default Credentials

If Terraform fails with authentication errors:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project terpedia
```

### DNS Zone Not Found

List existing zones:
```bash
gcloud dns managed-zones list --project=terpedia
```

Create a new zone if needed (see step 2 above).

### Permission Errors

Ensure dan@syzygyx.com has the following roles in the terpedia project:
- DNS Administrator (roles/dns.admin)
- Compute Admin (roles/compute.admin) - if creating static IPs
