# API Key Handling Guide for chat.terpedia.com

## Current Configuration

**API Key Mode**: `user_provided`

This means users must enter their own API keys in the LibreChat interface.

## How It Works

### For Users:
1. Log into LibreChat at https://chat.terpedia.com
2. Go to **Settings** → **Endpoints**
3. Select the **OpenAI** endpoint
4. Enter their API key for kb.terpedia.com
5. Key is encrypted and stored in the database

### For Administrators:
- Keys are stored encrypted in MongoDB
- Each user can have their own key
- Keys are not visible to administrators

## Configuration Options

### Option 1: User-Provided Keys (Current) ✅

**`.env`:**
```bash
OPENAI_API_KEY=user_provided
```

**`librechat.yaml`:**
```yaml
endpoints:
  openAI:
    apiKey: "user_provided"
```

**Pros:**
- Users control their own keys
- More secure (keys encrypted in DB)
- No shared key management

**Cons:**
- Users must provide their own keys
- Requires users to have valid kb.terpedia.com API keys

### Option 2: Shared API Key

If you want all users to use the same API key:

**1. Update `.env`:**
```bash
OPENAI_API_KEY=your-actual-api-key-here
```

**2. Update `librechat.yaml`:**
```yaml
endpoints:
  openAI:
    apiKey: "${OPENAI_API_KEY}"  # References .env variable
```

**3. Restart:**
```bash
sudo docker-compose restart api
```

**Pros:**
- No user action required
- Single key to manage
- Works immediately for all users

**Cons:**
- All users share the same key
- Key stored in configuration files
- Less secure if compromised

### Option 3: Environment Variable (Recommended for Shared Key)

**`.env`:**
```bash
OPENAI_API_KEY=your-shared-key-here
```

**`librechat.yaml`:**
```yaml
endpoints:
  openAI:
    apiKey: "${OPENAI_API_KEY}"
```

**Pros:**
- Key in .env (not hardcoded in YAML)
- Easy to change
- Can use different keys per environment

## Switching Between Modes

### To Switch to Shared Key:

```bash
# On server
cd ~/chat.terpedia.com

# Edit .env
nano .env
# Change: OPENAI_API_KEY=your-actual-key

# Edit librechat.yaml
nano librechat.yaml
# Change: apiKey: "${OPENAI_API_KEY}"

# Restart
sudo docker-compose restart api
```

### To Switch Back to User-Provided:

```bash
# Edit .env
OPENAI_API_KEY=user_provided

# Edit librechat.yaml
apiKey: "user_provided"

# Restart
sudo docker-compose restart api
```

## Security Best Practices

1. **File Permissions:**
   ```bash
   chmod 600 .env
   chmod 644 librechat.yaml
   ```

2. **Never Commit Keys:**
   - `.env` should be in `.gitignore`
   - Don't commit real keys to version control

3. **Use Environment Variables:**
   - Prefer `${OPENAI_API_KEY}` over hardcoded keys
   - Easier to rotate keys

4. **Key Rotation:**
   - If using shared key, rotate periodically
   - Update `.env` and restart services

## Testing API Keys

### Test from Server:
```bash
# Test with a key
curl -k -X POST https://kb.terpedia.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "test"}]
  }'
```

### Check LibreChat Logs:
```bash
sudo docker logs LibreChat | grep -i "api.*key\|401\|403\|authentication"
```

## Troubleshooting

### Users Can't Connect:
1. Verify kb.terpedia.com endpoint is accessible
2. Check API key format (should be valid for kb.terpedia.com)
3. Verify endpoint accepts the key format

### 401 Unauthorized:
- API key might be invalid
- Check key format with kb.terpedia.com documentation
- Verify key hasn't expired

### 403 Forbidden:
- CloudFront/CDN might be blocking requests
- Check kb.terpedia.com configuration
- Verify POST requests are allowed

### 404 Not Found:
- Endpoint path might be incorrect
- Verify `/v1` path is correct
- Check if kb.terpedia.com actually serves OpenAI API

## Current Status

- **Mode**: User-provided keys
- **Endpoint**: https://kb.terpedia.com/v1
- **Configuration**: Both `.env` and `librechat.yaml` configured
- **Note**: kb.terpedia.com endpoint appears to return 404/403 errors - may need endpoint configuration on kb.terpedia.com side

## Recommendation

**For Production:**
- Keep `user_provided` if users have their own kb.terpedia.com API keys
- Use shared key only if kb.terpedia.com provides a single shared key
- Ensure kb.terpedia.com endpoint is properly configured to accept API requests

**For Testing:**
- Can temporarily use a shared key to test connectivity
- Switch back to `user_provided` for production
