# ❓ Tez-tez Verilən Suallar (FAQ)

## 🎵 Musiqi Generasiyası

### S: Maksimum musiqi uzunluğu nə qədərdir?
**C**: 5 dəqiqə (300 saniyə). Daha uzun lazımsa, bir neçə hissəyə böl.

### S: Hansı model daha yaxşıdır?
**C**: 
- **small**: Sürətli, ucuz, orta keyfiyyət
- **medium**: ⭐ Tövsiyə - balans
- **large**: Ən yaxşı keyfiyyət, amma baha və yavaş

### S: Generasiya nə qədər vaxt aparır?
**C**: 
- 30s musiqi → ~10s generasiya
- 60s musiqi → ~20s generasiya
- 300s musiqi → ~90s generasiya

### S: Prompt necə yazmalıyam?
**C**: İngilis dilində, aydın:
```
✅ Yaxşı: "upbeat electronic dance music with heavy bass and energetic synths"
❌ Pis: "mahnı yarat"
```

## 💰 Xərc

### S: Nə qədər xərc olacaq?
**C**: 
- R2 storage: **PULSUZ** (10GB)
- Modal GPU: ~$0.003 per 60s musiqi
- 100 musiqi/gün ≈ **$9/ay**

### S: Necə xərc azaltmaq olar?
**C**:
1. `musicgen-small` istifadə et
2. Qısa musiqi yarat (30s)
3. A10G GPU-dan istifadə et (default)

## 🔧 Texniki

### S: R2 public URL harada tapım?
**C**: 
```bash
# Custom domain varsa:
https://music.yourdomain.com

# Yoxdursa, R2 bucket settings-də:
https://pub-xxxxx.r2.dev
```

### S: Modal token harada?
**C**:
```bash
# Terminal:
cat ~/.modal.toml

# Və ya:
https://modal.com/settings/tokens
```

### S: GitHub Actions niyə fail olur?
**C**:
1. Secrets yoxla (MODAL_TOKEN_ID, MODAL_TOKEN_SECRET)
2. JSON validate et: `python scripts/validate_request.py requests/file.json`
3. Modal deploy yoxla: `modal app list`

### S: R2 upload error
**C**:
```bash
# Credentials yoxla:
modal secret list

# Yenidən yarat:
modal secret delete r2-credentials
modal secret create r2-credentials ...
```

## 📊 İstifadə

### S: Bir neçə musiqi eyni anda yarada bilərəmmi?
**C**: Bəli! Bir neçə JSON faylı eyni anda push et:
```bash
git add requests/*.json
git push
```

### S: Musiqini necə yükləyim?
**C**:
```bash
# Browser-də URL-i aç
# Və ya:
wget "https://your-r2-url.com/path/to/file.wav"
```

### S: Köhnə musiqi fayllarını necə siləcəm?
**C**: 
1. R2 dashboard → musicmaker bucket
2. Files → Select → Delete
3. Və ya lifecycle policy qur (30 gündən köhnələri avtomatik sil)

## 🎛️ Parametrlər

### S: `temperature` nə deməkdir?
**C**: Kreativlik:
- 0.5-0.8: Konservativ, sabit
- 1.0: Default, balans
- 1.2-1.5: Kreativ, eksperimental
- 1.5+: Çox random

### S: `top_k` və `top_p` nədir?
**C**: Sampling parametrləri (advanced):
- Default qiymətlər kifayətdir
- Dəyişdirmə, bilmirsənsə

## 🔒 Təhlükəsizlik

### S: R2 faylları public-dir?
**C**: Bəli, URL bilən hər kəs yükləyə bilər. Private lazımsa:
1. Public access söndür
2. Signed URLs istifadə et (kod dəyişikliyi lazım)

### S: Modal secrets təhlükəsizdirmi?
**C**: Bəli, encrypted saxlanılır. Heç vaxt GitHub-a push etmə.

## 🚀 Performans

### S: Necə sürətləndirə bilərəm?
**C**:
1. Kiçik model: `musicgen-small`
2. Qısa duration: 30s
3. Parallel requests: bir neçə JSON eyni anda

### S: Cold start nədir?
**C**: İlk request yavaş ola bilər (~30s), model yüklənir. Sonrakılar sürətli.

## 📝 Digər

### S: Kommersial istifadə edə bilərəmmi?
**C**: Bəli, MusicGen Apache 2.0 lisenziyası ilə açıq mənbəlidir.

### S: Vokal əlavə edə bilərəmmi?
**C**: Xeyr, MusicGen yalnız instrumental. Vokal üçün başqa model lazım (Suno, Udio - amma ödənişli).

### S: Melody conditioning nədir?
**C**: Mövcud melodiya əsasında musiqi yaratmaq. Hazırda deaktivdir, amma kod-da var.

### S: Daha çox kömək?
**C**: 
- `TUTORIAL.md` - Ətraflı guide
- `SETUP.md` - Quraşdırma
- GitHub Issues - Problem bildir
