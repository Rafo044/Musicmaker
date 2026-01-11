# 🎓 Addım-addım Tutorial

## 📋 Ümumi Baxış

Bu sistem belə işləyir:
1. Sən JSON faylı GitHub-a atırsan
2. GitHub Actions avtomatik işə düşür
3. Modal.com-da MusicGen modeli musiqi yaradır
4. Musiqi Cloudflare R2-yə yüklənir (PULSUZ storage)
5. Sənə JSON output-da URL gəlir

---

## 🚀 Addım 1: Cloudflare R2 Quraşdırma

### 1.1 Cloudflare hesabı yarat
1. https://dash.cloudflare.com - gir
2. Sign up et (pulsuz)
3. Email verify et

### 1.2 R2 Bucket yarat
```bash
# Cloudflare Dashboard-da:
1. Sol menüdən "R2" seç
2. "Create bucket" düyməsi
3. Bucket adı: "musicmaker"
4. Location: Automatic
5. "Create bucket"
```

### 1.3 Public Access qur
```bash
# Bucket settings-də:
1. Bucket-i aç (musicmaker)
2. "Settings" tab
3. "Public Access" bölməsi
4. "Allow Access" düyməsi
5. Təsdiq et
```

### 1.4 Custom Domain əlavə et (optional amma tövsiyə olunur)
```bash
# R2 bucket-də:
1. "Settings" → "Custom Domains"
2. "Connect Domain" düyməsi
3. Domain daxil et: music.yourdomain.com
4. DNS records əlavə et (avtomatik göstərəcək)
5. Gözlə (5-10 dəqiqə)

# Əgər domain yoxdursa:
# R2 default URL istifadə edəcəksən:
# https://pub-xxxxx.r2.dev
```

### 1.5 API Token yarat
```bash
# Cloudflare Dashboard:
1. R2 → "Manage R2 API Tokens"
2. "Create API Token"
3. Token adı: "musicmaker-token"
4. Permissions: 
   - Object Read & Write
   - Bucket: musicmaker
5. "Create API Token"

# ⚠️ ÖNƏMLİ: Bu məlumatları yadda saxla:
# - Access Key ID: xxxxxxxxxxxxx
# - Secret Access Key: yyyyyyyyyyyyyy
# - Endpoint URL: https://<account-id>.r2.cloudflarestorage.com
```

**Nümunə**:
```
Access Key ID: a1b2c3d4e5f6g7h8i9j0
Secret Access Key: k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
Endpoint URL: https://abc123def456.r2.cloudflarestorage.com
```

---

## 🔧 Addım 2: Modal.com Quraşdırma

### 2.1 Modal hesabı yarat
```bash
# https://modal.com
1. Sign up (GitHub ilə)
2. Email verify et
```

### 2.2 Modal CLI quraşdır
```bash
# Terminal-da:
pip install modal

# Token yarat:
modal token new

# Browser açılacaq, login et
# Terminal-da "Successfully logged in" görməlisən
```

### 2.3 R2 credentials-i Modal-a əlavə et
```bash
# Terminal-da (öz məlumatlarınla):
modal secret create r2-credentials \
  R2_ENDPOINT_URL=https://abc123def456.r2.cloudflarestorage.com \
  R2_ACCESS_KEY_ID=a1b2c3d4e5f6g7h8i9j0 \
  R2_SECRET_ACCESS_KEY=k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6 \
  R2_BUCKET=musicmaker \
  R2_PUBLIC_URL=https://music.yourdomain.com

# Əgər custom domain yoxdursa:
# R2_PUBLIC_URL=https://pub-xxxxx.r2.dev
```

**Yoxla**:
```bash
modal secret list
# "r2-credentials" görməlisən
```

---

## 🎯 Addım 3: GitHub Quraşdırma

### 3.1 Repository secrets əlavə et
```bash
# GitHub-da:
1. Repository-ni aç
2. Settings → Secrets and variables → Actions
3. "New repository secret"

# İki secret əlavə et:

Secret 1:
Name: MODAL_TOKEN_ID
Value: [Modal dashboard-dan al]

Secret 2:
Name: MODAL_TOKEN_SECRET
Value: [Modal dashboard-dan al]
```

**Modal token-ləri necə tapmaq**:
```bash
# Terminal-da:
cat ~/.modal.toml

# Və ya Modal dashboard:
# https://modal.com/settings/tokens
```

### 3.2 İlk deploy
```bash
# Local-da test et:
cd /home/rafael/Documents/Musicmaker
modal run src/modal_app.py --prompt "happy music"

# Əgər işləyirsə, deploy et:
modal deploy src/modal_app.py

# "Deployed!" görməlisən
```

---

## 🎵 Addım 4: İlk Musiqi Yarat

### 4.1 JSON request yarat
```bash
cd /home/rafael/Documents/Musicmaker

# Yeni JSON faylı yarat:
cat > requests/my_first_music.json << 'EOF'
{
  "request_id": "req_first_001",
  "prompt": "upbeat electronic dance music with energetic synths and heavy bass",
  "duration": 30,
  "model": "musicgen-medium",
  "temperature": 1.0
}
EOF
```

### 4.2 GitHub-a push et
```bash
git add requests/my_first_music.json
git commit -m "Generate first music"
git push
```

### 4.3 Nəticəni izlə
```bash
# GitHub-da:
1. Repository → Actions tab
2. Ən son workflow-u aç
3. "generate-music" job-u aç
4. "Process requests" step-də JSON output görəcəksən:

{
  "status": "success",
  "request_id": "req_first_001",
  "audio_url": "https://music.yourdomain.com/req_first_001/20260111_123456.wav",
  "duration": 30,
  "model": "musicgen-medium",
  "prompt": "upbeat electronic dance music..."
}
```

### 4.4 Musiqini yüklə
```bash
# URL-i kopyala və browser-də aç
# Və ya wget ilə yüklə:
wget "https://music.yourdomain.com/req_first_001/20260111_123456.wav"
```

---

## 🔍 R2-yə Necə Göndərilir? (Texniki Detallar)

### Kod izahı:

```python
# src/modal_app.py-də bu hissə:

# 1. Boto3 ilə R2-yə qoşul (S3 API istifadə edir)
s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv("R2_ENDPOINT_URL"),  # R2 endpoint
    aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),  # Sənin key-in
    aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),  # Secret
)

# 2. Fayl adı yarat (unique)
bucket = "musicmaker"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
s3_key = f"{request_id}/{timestamp}.wav"
# Nümunə: "req_001/20260111_123456.wav"

# 3. Audio bytes-i R2-yə yüklə
s3_client.put_object(
    Bucket=bucket,           # musicmaker bucket-inə
    Key=s3_key,              # fayl yolu
    Body=audio_bytes,        # musiqi data-sı
    ContentType="audio/wav", # fayl tipi
)

# 4. Public URL yarat
r2_public_url = os.getenv("R2_PUBLIC_URL")
audio_url = f"{r2_public_url}/{s3_key}"
# Nümunə: "https://music.yourdomain.com/req_001/20260111_123456.wav"

# 5. URL-i return et
return {
    "status": "success",
    "audio_url": audio_url,  # Bu URL-i istifadə edirsən
    ...
}
```

### Niyə R2?
- ✅ **PULSUZ**: 10GB storage, unlimited requests
- ✅ **Sürətli**: Cloudflare CDN
- ✅ **S3 compatible**: Boto3 ilə işləyir
- ✅ **Public access**: Direct link ilə yüklə

### Alternativlər:
- AWS S3 (ödənişli)
- Google Cloud Storage (ödənişli)
- Azure Blob Storage (ödənişli)

---

## 📊 İstifadə Nümunələri

### Nümunə 1: Qısa musiqi (30s)
```json
{
  "request_id": "req_short_001",
  "prompt": "calm piano melody",
  "duration": 30
}
```

### Nümunə 2: Uzun musiqi (5 dəqiqə)
```json
{
  "request_id": "req_long_001",
  "prompt": "epic orchestral soundtrack with drums",
  "duration": 300
}
```

### Nümunə 3: Eksperimental
```json
{
  "request_id": "req_exp_001",
  "prompt": "futuristic synthwave with retro vibes",
  "duration": 120,
  "temperature": 1.5,
  "top_k": 500
}
```

**Parametrlər**:
- `duration`: 5-300 saniyə
- `model`: small/medium/large (medium tövsiyə)
- `temperature`: 0.1-2.0 (1.0 default, yüksək = daha kreativ)
- `top_k`: 0-500 (250 default)
- `top_p`: 0.0-1.0 (0.0 default)

---

## 🐛 Problemlər və Həllər

### Problem 1: "R2 upload failed"
```bash
# Həll:
# 1. Credentials yoxla:
modal secret list

# 2. Yenidən yarat:
modal secret delete r2-credentials
modal secret create r2-credentials ...

# 3. Bucket public access yoxla
```

### Problem 2: "Model loading timeout"
```bash
# Həll:
# 1. Kiçik model istifadə et:
"model": "musicgen-small"

# 2. Və ya timeout artır (config.yaml):
timeout: 900  # 15 dəqiqə
```

### Problem 3: "GitHub Actions failed"
```bash
# Həll:
# 1. Secrets yoxla (MODAL_TOKEN_ID, MODAL_TOKEN_SECRET)
# 2. JSON validation yoxla:
python scripts/validate_request.py requests/your_file.json

# 3. Logs-u oxu:
# GitHub → Actions → Failed workflow → Logs
```

### Problem 4: "Audio URL 404"
```bash
# Həll:
# 1. R2 bucket public access yoxla
# 2. Custom domain DNS yoxla
# 3. Default R2 URL istifadə et:
R2_PUBLIC_URL=https://pub-xxxxx.r2.dev
```

---

## 💡 Pro Tips

### Tip 1: Batch generation
```bash
# Çoxlu musiqi yaratmaq üçün:
for i in {1..10}; do
  cat > requests/batch_$i.json << EOF
{
  "request_id": "batch_$i",
  "prompt": "random music style $i",
  "duration": 60
}
EOF
done

git add requests/batch_*.json
git commit -m "Batch generation"
git push
```

### Tip 2: Local test
```bash
# GitHub-a push etməzdən əvvəl local test et:
modal run src/modal_app.py --prompt "test music"
```

### Tip 3: Xərc monitorinqi
```bash
# Modal dashboard-da:
# https://modal.com/usage
# GPU istifadəni izlə
```

### Tip 4: R2 storage təmizləmə
```bash
# Köhnə faylları sil (R2 dashboard):
# Bucket → Files → Select → Delete
# Və ya lifecycle policy qur (30 gündən köhnələri avtomatik sil)
```

---

## 📞 Kömək

Sual varsa:
1. `SETUP.md` oxu
2. GitHub Actions logs yoxla
3. Modal logs yoxla: `modal app logs musicmaker`
4. R2 dashboard yoxla

Uğurlar! 🎵
