# Terpedia Models Not Visible in UI - Troubleshooting

## Current Status

✅ **API Endpoint**: `https://api.terpedia.com/v1/models` returns Terpedia models  
✅ **Configuration**: `librechat.yaml` includes all Terpedia models  
✅ **LibreChat**: Restarted and running  
❌ **UI**: Models not visible

## Steps to See Terpedia Models

### 1. Clear Browser Cache
- **Chrome/Edge**: `Ctrl+Shift+Delete` → Clear cached images and files
- **Firefox**: `Ctrl+Shift+Delete` → Clear cache
- **Safari**: `Cmd+Option+E` to empty caches
- Or use **Incognito/Private window**

### 2. Hard Refresh
- **Windows/Linux**: `Ctrl+Shift+R` or `Ctrl+F5`
- **Mac**: `Cmd+Shift+R`

### 3. Check Model Selector in UI
1. Go to https://chat.terpedia.com
2. Look for the **model selector** (usually dropdown at top of chat)
3. Click on it
4. Look for endpoint: **"Terpedia & OpenAI"**
5. Models should show:
   - terpedia/unified
   - terpedia/kb
   - terpedia/pubmed
   - terpedia/rdkit
   - gpt-4o
   - gpt-4o-mini
   - gpt-4-turbo
   - gpt-3.5-turbo

### 4. Check Settings
1. Go to **Settings** (gear icon)
2. Look for **"Endpoints"** or **"Models"** section
3. Verify **"Terpedia & OpenAI"** endpoint is enabled
4. Check if models are listed there

### 5. Verify Configuration is Loaded
```bash
# On server
gcloud compute ssh chat-server --zone=us-central1-a --project=terpedia
cd ~/chat.terpedia.com
sudo docker exec LibreChat cat /app/librechat.yaml
```

Should show all Terpedia models in the `default` list.

### 6. Check LibreChat Logs
```bash
sudo docker logs LibreChat 2>&1 | grep -i "terpedia\|model\|endpoint" | tail -30
```

Look for:
- Configuration loaded
- Models registered
- Any errors

### 7. Force Configuration Reload
If models still don't appear, try:
```bash
# On server
sudo docker-compose restart api
# Wait 30 seconds
# Then hard refresh browser
```

## Expected Behavior

Once working:
- **Model Selector**: Shows "Terpedia & OpenAI" endpoint
- **Models Available**: 8 models (4 Terpedia + 4 OpenAI)
- **Terpedia Models**: 
  - terpedia/unified
  - terpedia/kb
  - terpedia/pubmed
  - terpedia/rdkit

## If Still Not Visible

1. **Check if logged in**: Some LibreChat configs require login
2. **Check user permissions**: Admin vs regular user
3. **Check LibreChat version**: May need specific version
4. **Check browser console**: Look for JavaScript errors (F12)

## Verification Commands

```bash
# Test API models endpoint
curl https://api.terpedia.com/v1/models | jq '.data[] | select(.id | startswith("terpedia"))'

# Check LibreChat config
sudo docker exec LibreChat cat /app/librechat.yaml

# Check LibreChat logs
sudo docker logs LibreChat 2>&1 | tail -50
```

## Note About kb.terpedia.com Backend

The kb.terpedia.com origin is currently an S3 bucket (doesn't support POST). The Terpedia models will show in the UI, but when selected, they'll need the actual API backend deployed. For now, the models should be visible even if the backend isn't ready.
