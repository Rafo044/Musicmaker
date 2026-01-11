# 🚀 Quraşdırma (SADƏ)

## 1. Modal.com

### Hesab yarat
```bash
# https://modal.com - hesab aç
pip install modal
modal token new
```

### Secrets əlavə et
```bash
# Cloudflare R2 credentials
modal secret create r2-credentials \
  R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com \
  R2_ACCESS_KEY_ID=xxx \
  R2_SECRET_ACCESS_KEY=xxx \
  R2_BUCKET=musicmaker \
  R2_PUBLIC_URL=https://musicmaker.yourdomain.com
```

## 2. Cloudflare R2 (PULSUZ)

### Bucket yarat
1. Cloudflare Dashboard → R2
2. Create Bucket: `musicmaker`
3. Settings → Public Access → Allow
4. Custom Domain əlavə et (optional)

### API Token al
1. R2 → Manage R2 API Tokens
2. Create API Token
3. Copy Access Key ID və Secret

## 3. GitHub Secrets

Repository → Settings → Secrets → Actions:

```
MODAL_TOKEN_ID=xxx
MODAL_TOKEN_SECRET=xxx
```

## 4. İlk Deploy

```bash
# Local test
modal run src/modal_app.py --prompt "happy music"

# Deploy
modal deploy src/modal_app.py
```

## 5. İstifadə

### JSON yarat
```bash
cp requests/example_001.json requests/my_music.json
# Edit: prompt, duration, model
```

### GitHub-a push et
```bash
git add requests/my_music.json
git commit -m "Generate music"
git push
```

### Nəticə
- GitHub Actions işləyir (~1-3 dəqiqə)
- Logs-da JSON output görəcəksən:
```json
{
  "status": "success",
  "request_id": "req_001",
  "audio_url": "https://musicmaker.yourdomain.com/req_001/20260111_112233.wav",
  "duration": 60,
  "model": "musicgen-medium"
}
```

## 📊 Xərc

**Modal.com** (A10G GPU):
- $0.60/saat
- 60s musiqi ≈ 20s GPU ≈ $0.003
- 100 musiqi/gün = **~$9/ay**

**Cloudflare R2**:
- 10GB storage: **PULSUZ**
- Requests: **PULSUZ**

**TOPLAM: ~$10/ay** 🎉

## 🔧 Troubleshooting

### Model yüklənmir
```bash
# Volume-u sil və yenidən yüklə
modal volume delete musicgen-models
```

### R2 upload error
```bash
# Credentials yoxla
modal secret list
```

### Timeout
```bash
# Duration-u azalt və ya timeout artır (config.yaml)
```

## 📝 Qeydlər

- **duration**: 5-300 saniyə (5 dəqiqə max)
- **model**: small/medium/large (medium tövsiyə olunur)
- **output**: WAV format (32kHz stereo)
- **R2 URL**: 7 gün keçərlidir (config.yaml-da dəyişə bilərsən)
