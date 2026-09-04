# Fixing Models Not Visible in UI

## Current Status

✅ **Services**: All running  
✅ **Configuration**: librechat.yaml has Terpedia models  
✅ **API Endpoint**: api.terpedia.com returns models  
❌ **UI**: Models not visible

## Troubleshooting Steps

### 1. Verify Configuration is Loaded

```bash
# On server
gcloud compute ssh chat-server --zone=us-central1-a --project=terpedia
cd ~/chat.terpedia.com
sudo docker exec LibreChat cat /app/librechat.yaml
```

Should show all Terpedia models in the `default` list.

### 2. Check API Endpoint from Server

```bash
curl https://api.terpedia.com/v1/models | jq '.data[] | select(.id | startswith("terpedia"))'
```

Should return 4 Terpedia models.

### 3. Check LibreChat Models API

```bash
curl http://localhost:3080/api/models | jq '.'
```

This shows what LibreChat is exposing to the frontend.

### 4. Clear Browser Cache (Critical)

**This is the most common issue:**

1. **Hard Refresh**:
   - Windows/Linux: `Ctrl+Shift+R` or `Ctrl+F5`
   - Mac: `Cmd+Shift+R`

2. **Clear Cache**:
   - Chrome: `Ctrl+Shift+Delete` → Clear "Cached images and files"
   - Or use **Incognito/Private window**

3. **Clear Service Worker**:
   - Open DevTools (F12)
   - Application tab → Service Workers
   - Click "Unregister" if any are registered
   - Hard refresh again

### 5. Check Browser Console

Open DevTools (F12) and check:
- **Console tab**: Look for errors
- **Network tab**: Check if `/api/models` is being called
- **Application tab**: Check if models are cached

### 6. Verify User is Logged In

Some LibreChat configurations require authentication:
- Try logging out and back in
- Check if you need to create an account first

### 7. Check LibreChat Version

Current version: v0.8.2-rc2

Some versions handle model lists differently. The configuration format might need adjustment.

### 8. Force Model Refresh

If models still don't appear:

1. **Restart LibreChat**:
   ```bash
   sudo docker-compose restart api
   ```

2. **Wait 30 seconds** for full startup

3. **Clear browser cache** again

4. **Hard refresh** the page

## Expected Configuration

```yaml
endpoints:
  openAI:
    enabled: true
    title: "Terpedia & OpenAI"
    baseURL: "https://api.terpedia.com/v1"
    apiKey: "user_provided"
    models:
      default:
        - "terpedia/unified"
        - "terpedia/kb"
        - "terpedia/pubmed"
        - "terpedia/rdkit"
        - "gpt-4o"
        - "gpt-4o-mini"
        - "gpt-4-turbo"
        - "gpt-3.5-turbo"
      fetch: false
```

## Where to Find Models in UI

1. **Model Selector**: Usually a dropdown at the top of the chat
2. **Settings**: Gear icon → Models/Endpoints section
3. **New Chat**: When starting a new conversation, model selector appears

## If Still Not Visible

1. Check if you're logged in
2. Try a different browser
3. Check browser console for JavaScript errors
4. Verify LibreChat API is accessible: `curl http://localhost:3080/api/models`
5. Check if models endpoint requires authentication

## Debug Commands

```bash
# Check models API
curl http://localhost:3080/api/models

# Check endpoints
curl http://localhost:3080/api/endpoints

# Check LibreChat logs
sudo docker logs LibreChat --tail=50

# Verify config
sudo docker exec LibreChat cat /app/librechat.yaml
```

## Most Likely Solution

**Clear your browser cache and use a hard refresh.** LibreChat caches the model list in the browser, and the Terpedia models were added after the initial page load.

Try:
1. Open in **Incognito/Private window**
2. Or clear cache completely
3. Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
