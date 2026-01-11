# ✅ Sistem Yoxlanışı - Hazırdır!

## 📋 Sistem Strukturu

```
1 JSON = 1 MUSİQİ
```

### İş Axını:
1. `requests/my_music.json` yarat
2. GitHub-a push et
3. GitHub Actions işə düşür
4. Modal.com musiqi yaradır
5. GitHub Artifacts-ə yüklənir
6. 90 gün saxlanır

---

## ✅ Yoxlanılmış Komponentlər

### 1. Modal App (`src/modal_app.py`)
- ✅ MusicGenerator class (model yüklənir)
- ✅ process_request function (bytes return edir)
- ✅ Local test (düzgün işləyir)
- ✅ Error handling

### 2. GitHub Workflow (`.github/workflows/deploy.yml`)
- ✅ JSON dəyişikliyi detect edir
- ✅ Validation
- ✅ Modal deploy
- ✅ Process requests
- ✅ Upload artifacts
- ✅ MODAL_TOKEN_ID və MODAL_TOKEN_SECRET istifadə edir

### 3. Scripts
- ✅ `validate_request.py` - JSON schema yoxlayır
- ✅ `process_request.py` - Modal-dan bytes alır, local saxlayır

### 4. JSON Schema (`schemas/request.json`)
- ✅ Sadələşdirildi (lazımsız parametrlər çıxarıldı)
- ✅ Yalnız lazımlı parametrlər:
  - `request_id` (required)
  - `prompt` (required)
  - `duration` (optional, default: 60)
  - `model` (optional, default: medium)
  - `temperature`, `top_k`, `top_p` (optional)

### 5. Example JSON
- ✅ `example_001.json` - Tam parametrlərlə
- ✅ `minimal_example.json` - Minimal (yalnız required)

---

## 🎯 İstifadə Nümunələri

### Minimal (Ən Sadə):
```json
{
  "request_id": "req_001",
  "prompt": "happy upbeat music",
  "duration": 30
}
```

### Tam Parametrlərlə:
```json
{
  "request_id": "req_002",
  "prompt": "epic orchestral soundtrack with drums",
  "duration": 120,
  "model": "musicgen-large",
  "temperature": 1.2
}
```

---

## 🚀 Test Etmək

### Local Test:
```bash
# Modal deploy
modal deploy src/modal_app.py

# Test et
modal run src/modal_app.py --prompt "test music"

# Nəticə: output/test_001.wav
```

### GitHub Test:
```bash
# JSON yarat
cat > requests/test.json << 'EOF'
{
  "request_id": "req_test",
  "prompt": "calm piano music",
  "duration": 30
}
EOF

# Push et
git add requests/test.json
git commit -m "Test music generation"
git push

# GitHub Actions → Artifacts-dən yüklə
```

---

## ⚠️ Mühüm Qeydlər

1. **Bir JSON = Bir Musiqi**
   - Hər JSON faylı ayrı musiqi yaradır
   - Bir JSON-da bir neçə musiqi yoxdur

2. **Request ID Unique Olmalı**
   - Pattern: `req_[a-zA-Z0-9_-]+`
   - Nümunə: `req_001`, `req_test_piano`, `req_epic_2024`

3. **Duration Limiti**
   - Minimum: 5 saniyə
   - Maksimum: 300 saniyə (5 dəqiqə)

4. **Model Seçimi**
   - `small`: Sürətli, ucuz, orta keyfiyyət
   - `medium`: ⭐ Tövsiyə (balans)
   - `large`: Ən yaxşı, amma baha

5. **GitHub Artifacts**
   - 90 gün saxlanır
   - Sonra avtomatik silinir
   - Yenidən yaratmaq lazımsa, JSON-u yenidən push et

---

## 🐛 Problem Həlli

### Problem: "Modal token not found"
```bash
# Həll: GitHub Secrets yoxla
Repository → Settings → Secrets → Actions
MODAL_TOKEN_ID=xxx
MODAL_TOKEN_SECRET=xxx
```

### Problem: "Validation failed"
```bash
# Həll: JSON validate et
python scripts/validate_request.py requests/your_file.json
```

### Problem: "Model loading timeout"
```bash
# Həll: Kiçik model istifadə et
"model": "musicgen-small"
```

---

## ✅ Sistem Hazırdır!

Bütün komponentlər yoxlanıldı və düzəldildi:
- ✅ Modal app
- ✅ GitHub workflow
- ✅ Scripts
- ✅ JSON schema
- ✅ Examples

**Növbəti addım**: GitHub-a push et və test et! 🎵
