# ⚡ 5 Dəqiqədə Başla

## 1️⃣ Cloudflare R2 (2 dəqiqə)

```bash
# https://dash.cloudflare.com
1. Sign up (pulsuz)
2. R2 → Create bucket → "musicmaker"
3. Settings → Public Access → Allow
4. Manage R2 API Tokens → Create
5. Məlumatları kopyala:
   - Access Key ID
   - Secret Access Key
   - Endpoint URL
```

## 2️⃣ Modal.com (1 dəqiqə)

```bash
# Terminal:
pip install modal
modal token new

# R2 credentials əlavə et:
modal secret create r2-credentials \
  R2_ENDPOINT_URL=https://YOUR-ACCOUNT.r2.cloudflarestorage.com \
  R2_ACCESS_KEY_ID=YOUR-KEY \
  R2_SECRET_ACCESS_KEY=YOUR-SECRET \
  R2_BUCKET=musicmaker \
  R2_PUBLIC_URL=https://pub-xxxxx.r2.dev

# Deploy:
modal deploy src/modal_app.py
```

## 3️⃣ GitHub (1 dəqiqə)

```bash
# Repository → Settings → Secrets → Actions
# Əlavə et:
MODAL_TOKEN_ID=xxx
MODAL_TOKEN_SECRET=xxx

# Token-ləri tap:
cat ~/.modal.toml
# və ya: https://modal.com/settings/tokens
```

## 4️⃣ İlk Musiqi (1 dəqiqə)

```bash
# JSON yarat:
cat > requests/test.json << 'EOF'
{
  "request_id": "test_001",
  "prompt": "happy upbeat music",
  "duration": 30
}
EOF

# Push et:
git add requests/test.json
git commit -m "Test music"
git push

# GitHub Actions → Logs-da URL görəcəksən
```

## ✅ Hazır!

İndi hər dəfə JSON push edəndə avtomatik musiqi yaranacaq.

**Daha ətraflı**: `TUTORIAL.md` oxu
