# Terpedia Models Setup

## Status Check

### API Endpoint
- ✅ **Models Available**: `terpedia/unified`, `terpedia/kb`, `terpedia/pubmed`, `terpedia/rdkit`
- ✅ **Endpoint**: `https://api.terpedia.com/v1/models`

### LibreChat Configuration
- ✅ **Config File**: `librechat.yaml` includes all Terpedia models
- ✅ **Endpoint**: `https://api.terpedia.com/v1`
- ✅ **Models List**: All 8 models (4 Terpedia + 4 OpenAI)

## If Models Don't Appear in UI

### 1. Check LibreChat is Restarted
```bash
gcloud compute ssh chat-server --zone=us-central1-a --project=terpedia
cd ~/chat.terpedia.com
sudo docker-compose restart api
```

### 2. Verify Configuration
```bash
sudo docker exec LibreChat cat /app/librechat.yaml
```

Should show:
```yaml
models:
  default:
    - "terpedia/unified"
    - "terpedia/kb"
    - "terpedia/pubmed"
    - "terpedia/rdkit"
    - "gpt-4o"
    ...
```

### 3. Check LibreChat Logs
```bash
sudo docker logs LibreChat 2>&1 | tail -50
```

Look for:
- Configuration loaded
- Models registered
- Any errors

### 4. Clear Browser Cache
- Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Or clear browser cache for chat.terpedia.com

### 5. Check UI
1. Go to https://chat.terpedia.com
2. Click on model selector (usually top of chat)
3. Look for "Terpedia & OpenAI" endpoint
4. Models should include:
   - terpedia/unified
   - terpedia/kb
   - terpedia/pubmed
   - terpedia/rdkit

## Testing

### Test API Models Endpoint
```bash
curl https://api.terpedia.com/v1/models | jq '.data[] | select(.id | startswith("terpedia"))'
```

### Test Terpedia Backend
```bash
curl -X POST https://kb.terpedia.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"terpedia/unified","messages":[{"role":"user","content":"test"}]}'
```

## Troubleshooting

If models still don't appear:
1. ✅ Verify librechat.yaml is correct
2. ✅ Restart LibreChat container
3. ✅ Check logs for errors
4. ✅ Clear browser cache
5. ✅ Try incognito/private window
6. ✅ Check if user is logged in
7. ✅ Verify endpoint is accessible from server

## Expected Behavior

Once working:
- Models dropdown shows "Terpedia & OpenAI" endpoint
- 8 models available (4 Terpedia + 4 OpenAI)
- Selecting `terpedia/unified` routes to kb.terpedia.com backend
- Selecting `gpt-4o` routes to OpenAI
