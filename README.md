# Surat Jalan Auditor — AI Reconciliation MVP

Cross-check otomatis antara **Surat Jalan** dan **Invoice** sebelum barang meninggalkan gudang.

Upload dua gambar dokumen → sistem mengekstrak field terstruktur → reconciliation engine membandingkan dan mengembalikan status **CLEARANCE APPROVED** atau **MISMATCH DETECTED** beserta rincian selisih.

---

## Cara Menjalankan (Docker Compose)

### Prasyarat
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 4.x
- Docker Compose plugin (sudah termasuk di Docker Desktop)

### Langkah

```bash
# 1. Clone repositori
git clone <url-repo>
cd <nama-folder>

# 2. Salin contoh environment
cp .env.example .env

# 3. Build dan jalankan semua service
docker compose up --build

# Frontend: http://localhost:3000
# Backend API docs (Swagger): http://localhost:8000/docs
# Backend health check: http://localhost:8000/health
```

> Pertama kali build membutuhkan beberapa menit (mengunduh layer Python + Node dan menginstall dependensi).

### Menghentikan

```bash
docker compose down
```

---

## Cara Menjalankan secara Lokal (Tanpa Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

Pastikan `BACKEND_INTERNAL_URL` di `.env` (atau environment) mengarah ke `http://localhost:8000` saat menjalankan secara lokal.

---

## Menjalankan Unit Test

```bash
cd backend
pip install -r requirements.txt   # kalau belum
pytest reconciliation/test_engine.py -v
```

Output yang diharapkan: **10 passed** (5 skenario approved, 5 skenario mismatch).

---

## Arsitektur Pipeline

```
[Upload 2 Dokumen via Browser]
         ↓
[POST /api/reconcile  ←  Next.js proxy  ←  FastAPI]
         ↓
[preprocessing/image_processor.py]   — OpenCV: deskew, crop, denoise
         ↓
[extraction/extractor.py]             — OCR + extraction model (STUB saat ini)
         ↓
[reconciliation/engine.py]            — rapidfuzz + exact compare (IMPLEMENTASI PENUH)
         ↓
[JSON Response → ResultPanel di UI]
```

## Struktur Direktori

```
.
├── README.md
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── main.py                     # FastAPI entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── schemas/
│   │   └── document.py             # Pydantic models (kontrak data)
│   ├── preprocessing/
│   │   └── image_processor.py      # OpenCV pipeline
│   ├── extraction/
│   │   └── extractor.py            # OCR/VLM stub + interface
│   └── reconciliation/
│       ├── engine.py               # Rule-based + fuzzy engine (full impl.)
│       └── test_engine.py          # Unit tests
└── frontend/
    ├── app/
    │   ├── layout.tsx
    │   └── page.tsx                # Single-page UI
    ├── components/
    │   ├── UploadZone.tsx          # Drag-and-drop upload
    │   ├── StatusBadge.tsx         # APPROVED / MISMATCH badge
    │   ├── MismatchTable.tsx       # Tabel rincian selisih
    │   └── ResultPanel.tsx         # Split-view hasil
    ├── types/
    │   └── api.ts                  # TypeScript types (mirror Pydantic)
    ├── next.config.ts
    └── Dockerfile
```

---

## Kontrak API

### `POST /api/reconcile`

**Request** — `multipart/form-data`:
| Field | Tipe | Deskripsi |
|-------|------|-----------|
| `surat_jalan` | file | Gambar Surat Jalan (JPEG/PNG) |
| `invoice` | file | Gambar Invoice (JPEG/PNG) |

**Response 200** — `application/json`:
```json
{
  "status": "MISMATCH_DETECTED",
  "mismatches": [
    {
      "field": "items[SKU-001].qty",
      "surat_jalan_value": "100",
      "invoice_value": "80",
      "severity": "high"
    }
  ],
  "extracted": {
    "surat_jalan": { "doc_type": "surat_jalan", "..." : "..." },
    "invoice":     { "doc_type": "invoice",     "..." : "..." }
  }
}
```

---

## Reconciliation Logic

| Field | Metode | Threshold |
|-------|--------|-----------|
| `pengirim`, `penerima` | fuzzy `token_sort_ratio` | ≥ 85 (env: `FUZZY_THRESHOLD`) |
| `alamat_tujuan` | fuzzy `token_sort_ratio` | ≥ 85 |
| `items[].qty` | exact match | — |
| `items[].berat_kg` | toleransi numerik | ±0.5 kg (env: `BERAT_KG_TOLERANCE`) |
| `total_harga` | exact match | — |

Konfigurasi dapat diubah melalui environment variable di `.env`.

---

## Known Limitations

> **Extraction masih stub/mock**
> 
> File `backend/extraction/extractor.py` saat ini mengembalikan data hardcoded alih-alih memproses gambar yang di-upload sesungguhnya. Semua lokasi yang perlu diganti ditandai dengan komentar:
> ```python
> # TODO: replace with fine-tuned model
> ```
> Lihat `extraction/extractor.py` untuk detail interface yang perlu diimplementasikan.

> **OpenCV preprocessing belum di-tune**
> 
> Fungsi deskew, crop, dan denoise sudah ada dan berjalan, tetapi parameter (Canny threshold, Hough parameter, filter strength) belum dioptimalkan untuk data scan nyata. Ditandai dengan:
> ```python
> # TODO: tune parameters
> ```

> **Tidak ada persistensi**
> 
> Sesuai scope kompetisi, tidak ada database. Setiap request adalah stateless.

---

## Environment Variables

| Variable | Default | Deskripsi |
|----------|---------|-----------|
| `FUZZY_THRESHOLD` | `85` | Skor minimum fuzzy matching (0–100) |
| `BERAT_KG_TOLERANCE` | `0.5` | Toleransi beda berat dalam kg |
| `BACKEND_INTERNAL_URL` | `http://backend:8000` | URL backend dari container frontend |

---

## Iterasi Berikutnya (Belum dikerjakan)

- [ ] Integrasi model vision-language fine-tuned (ganti stub di `extraction/extractor.py`)
- [ ] Dataset sintetik untuk fine-tuning (proses offline terpisah)
- [ ] Video proof of work

---

## Conventional Commits

Repositori ini menggunakan format [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — fitur baru
- `fix:` — perbaikan bug
- `refactor:` — refaktor kode tanpa perubahan perilaku
- `docs:` — perubahan dokumentasi
- `chore:` — setup, konfigurasi, dependency
