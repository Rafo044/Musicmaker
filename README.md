# 🎤 Musicmaker - AI Lyrics to Song (DiffRhythm)

> **Lyrics → Full Song with Vocals in 10 seconds!**

## 🎯 Sistem

```
Lyrics (LRC format) → GitHub → Modal.com → DiffRhythm → Full Song (Vocals + Instrumental) → GitHub Artifacts
```

## ⚡ 3 Addımda Başla

### 1️⃣ Modal.com Setup
```bash
pip install modal
modal token new
modal deploy src/modal_app.py
```

### 2️⃣ GitHub Secrets
```bash
# Repository → Settings → Secrets → Actions
MODAL_TOKEN_ID=xxx
MODAL_TOKEN_SECRET=xxx
```

### 3️⃣ İlk Mahnı
```bash
# Lyrics yaz (LRC format)
cat > requests/my_song.json << 'EOF'
{
  "request_id": "req_001",
  "lyrics": "[00:00.00] Verse\n[00:05.00] Your lyrics here\n\n[00:20.00] Chorus\n[00:21.00] More lyrics",
  "genre": "rock",
  "duration": 95
}
EOF

# Push et
git add requests/my_song.json
git push
```

## 🎸 Lyrics Format (LRC)

DiffRhythm **LRC format** istifadə edir (timestamps ilə):

```
[00:00.00] Intro
[00:05.00] First line of lyrics
[00:10.00] Second line of lyrics

[00:20.00] Chorus
[00:21.00] Chorus lyrics here
[00:25.00] More chorus lyrics
```

**Format**:
- `[MM:SS.mm]` - Timestamp (minutes:seconds.milliseconds)
- Sonra lyrics
- Boş sətir section ayırır

## 📝 JSON Nümunələri

### Rock Mahnı (95s):
```json
{
  "request_id": "req_rock_001",
  "lyrics": "[00:00.00] Verse 1\n[00:05.00] Walking through the shadows\n\n[00:25.00] Chorus\n[00:26.00] I will rise above",
  "genre": "rock",
  "duration": 95
}
```

### Metal Mahnı (285s - uzun):
```json
{
  "request_id": "req_metal_001",
  "lyrics": "[00:00.00] Intro\n[00:05.00] Thunder roars\n\n[00:25.00] Chorus\n[00:26.00] Rise from the ashes",
  "genre": "metal",
  "duration": 285
}
```

## 🎵 Dəstəklənən Janrlar

- **rock** - Rock music
- **metal** - Heavy metal
- **indie** - Indie rock
- **pop** - Pop music
- **electronic** - Electronic/EDM
- **folk** - Folk music
- **jazz** - Jazz
- **blues** - Blues
- **country** - Country
- **hip-hop** - Hip hop
- **r&b** - R&B
- **classical** - Classical

## 📊 Parametrlər

| Parametr | Tələb | Default | Açıqlama |
|----------|-------|---------|----------|
| `request_id` | ✅ | - | Unique ID (req_xxx) |
| `lyrics` | ✅ | - | LRC format lyrics |
| `genre` | ❌ | rock | Musiqi janrı |
| `duration` | ❌ | 95 | 95s və ya 285s |

## 💰 Xərc

**Modal.com** (A10G - 24GB):
- $0.60/saat
- 95s mahnı ≈ 10s generasiya = $0.002
- **10 mahnı/ay**: ~$0.20/ay
- **50 mahnı/ay**: ~$1/ay
- **100 mahnı/ay**: ~$2/ay

**GitHub Artifacts**: PULSUZ (90 gün)

**TOPLAM**: **$1-3/ay** 🎉

## ⚡ Performans

- **95s mahnı** → ~10s generasiya
- **285s mahnı** → ~15s generasiya
- **VRAM**: 8-24GB (A10G kifayət edir)

## 📥 Mahnını Yükləmək

1. GitHub → Actions
2. Workflow-u aç
3. Artifacts → Download ZIP
4. WAV faylı

## 🎼 Lyrics Yazma Tövsiyələri

### Timestamp Qaydaları:
```
[00:00.00] - Başlanğıc (0 saniyə)
[00:05.00] - 5 saniyə
[00:10.00] - 10 saniyə
[01:30.00] - 1 dəqiqə 30 saniyə
```

### 95s Mahnı Strukturu:
```
[00:00.00] Intro/Verse 1 (0-20s)
[00:20.00] Chorus (20-40s)
[00:40.00] Verse 2 (40-60s)
[01:00.00] Chorus (60-80s)
[01:20.00] Outro (80-95s)
```

### 285s Mahnı Strukturu:
```
[00:00.00] Intro (0-10s)
[00:10.00] Verse 1 (10-40s)
[00:40.00] Chorus (40-70s)
[01:10.00] Verse 2 (70-100s)
[01:40.00] Chorus (100-130s)
[02:10.00] Bridge (130-160s)
[02:40.00] Chorus (160-190s)
[03:10.00] Outro (190-285s)
```

## 🛠️ Texnologiyalar

- **Model**: DiffRhythm (ASLP-lab)
- **GPU**: Modal.com A10G (24GB)
- **Output**: Full song with vocals + instrumental
- **Storage**: GitHub Artifacts (90 gün)
- **Speed**: 10-15 saniyə generasiya

## 📝 Nümunələr

Repo-da nümunələr:
- `example_001.json` - Rock (95s)
- `metal_example.json` - Metal (95s)
- `indie_example.json` - Indie (285s)

---

**Suallar?** Issues aç və ya documentation oxu.

**DiffRhythm haqqında**: https://github.com/ASLP-lab/DiffRhythm
