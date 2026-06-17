# Rate Limit Troubleshooting Guide

## Current Situation

Your logs show that **all API keys are hitting rate limits**. This is happening because:

1. ✅ Key rotation is working correctly
2. ❌ All keys have been used recently and hit their limits
3. ❌ Key #5 was invalid (401 error) - now removed from rotation

## Why This Happens

### Groq Free Tier Limits (Per Key):
- **Requests per minute (RPM)**: 30
- **Requests per day (RPD)**: 14,400
- **Tokens per minute (TPM)**: 6,000

When you hit these limits, the key is blocked temporarily.

## Solutions

### Option 1: Wait for Rate Limits to Reset ⏰
Rate limits reset automatically:
- **Per-minute limits**: Reset after 1 minute
- **Per-day limits**: Reset at midnight UTC

**What to do:**
1. Wait 5-10 minutes
2. Try again - keys should work
3. The 60-second cooldown in the code will help

### Option 2: Get Fresh API Keys 🔑
Your current keys might be exhausted for the day.

**Steps:**
1. Go to https://console.groq.com/keys
2. Create 4-5 new API keys
3. Update `main.py` with new keys:
   ```python
   GROQ_API_KEYS = [
       os.getenv("GROQ_API_KEY"),
       "your_new_key_1",
       "your_new_key_2",
       "your_new_key_3",
       "your_new_key_4",
   ]
   ```
4. Restart backend

### Option 3: Upgrade to Paid Tier 💳
Groq offers higher limits on paid plans:
- Much higher RPM/RPD limits
- Better for production use
- More reliable service

Visit: https://console.groq.com/settings/billing

### Option 4: Implement Request Queuing 🚦
For high traffic, add a queue system:
- Queue incoming requests
- Process them slowly to stay under limits
- Users wait a bit longer but get responses

## Current Status

You now have **4 valid API keys** in rotation:
- Key #1: From .env file
- Key #2: gsk_DwCCD8w...
- Key #3: gsk_GFre6g...
- Key #4: gsk_WAopCr...

Key #5 was removed (invalid).

## Immediate Action

**Right now, you should:**

1. **Wait 5-10 minutes** for rate limits to reset
2. **Try a single request** to test
3. **Check key stats**: `curl http://localhost:8000/api/key-stats`

## Checking Key Status

```bash
curl http://localhost:8000/api/key-stats
```

Look for:
- `status: "available"` - Key is ready to use
- `status: "cooling_down"` - Key failed recently, wait 60s
- `last_failure_seconds_ago` - How long since last failure

## Prevention Tips

1. **Spread out requests** - Don't send many at once
2. **Monitor usage** - Check `/api/key-stats` regularly
3. **Add delays** - Wait between requests if testing
4. **Consider caching** - Cache common responses
5. **Upgrade if needed** - For production, use paid tier

## Testing After Waiting

After 5-10 minutes, restart backend and try:

```bash
# Restart backend
cd bhagvadgpt-backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then send ONE test request from the frontend.

## Error Messages Explained

- **"Rate limit hit"** - Key used too many requests, will reset soon
- **"Invalid API Key"** - Key is wrong or revoked (Key #5 had this)
- **"All API keys exhausted"** - All keys hit limits, wait and retry

---

**Radhe Radhe! 🙏**

The rotation system is working perfectly - it's just that all keys need time to reset their limits!
