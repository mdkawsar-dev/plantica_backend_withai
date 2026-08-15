# Plantica Backend — Smart Agriculture & AI Gardening Engine

Plantica is a robust, production-grade backend engine designed for modern smart agriculture, urban gardening, plant disease diagnostics, hyperlocal agro-meteorology, and an agricultural marketplace.

---

## Key Features & Architectural Modules

```
                               +------------------------------------------------+
                               |               Plantica Backend                 |
                               +-----------------------+------------------------+
                                                       |
         +---------------------+-----------------------+-----------------------+---------------------+
         |                     |                       |                       |                     |
  +---------------+     +---------------+       +---------------+       +---------------+     +---------------+
  | Dual Disease  |     | Agro-Weather  |       | AI Voice/Chat |       | Garden & Care |     | Marketplace & |
  |  Diagnostics  |     | Intelligence  |       |   Assistant   |       |  Management   |     |   Community   |
  +---------------+     +---------------+       +---------------+       +---------------+     +---------------+
  - Multimodal AI       - Open-Meteo            - Bengali NLP           - Plant Catalog       - Seed & Plants
  - EfficientNetV2      - Reverse Geocode       - Voice Notes           - Custom Care Log     - Cart & Orders
  - 97-Class Masking    - Farming Alerts        - Image In-Chat         - Task Scheduler      - Feed & Posts
```

### 1. Dual-Engine Disease Detection
- **Pure Generative AI Vision Engine (`/api/v1/disease/detect/ai/`)**: Analyzes plant leaf photos without requiring prior plant species knowledge. Detects condition, health, severity, and generates an exact 4-step organic/chemical treatment plan and prevention guide in Bengali.
- **EfficientNetV2 Deep Learning Model Engine (`/api/v1/disease/detect/ml/`)**: 97-class fine-tuned model with botanical masking to filter plant-specific diseases based on user input.

### 2. Multimodal AI Agricultural Chatbot & Voice Assistant (`/api/v1/ai/chat/`)
- Specialized agricultural advice for Bangladesh's 6 seasons, climate, soil preparation, fertilizers (Urea, TSP, Boron, Organic compost), and pest control.
- Supports **Bengali Text Queries**, **Leaf/Plant/Soil Photos**, and **Bengali Voice Recordings (`.m4a`, `.mp3`, `.wav`)**.
- Returns markdown guidance, spoken summaries for Text-To-Speech (TTS), and automated follow-up suggestions.

### 3. Hyperlocal Agro-Weather Intelligence (`/api/v1/plants/weather/`)
- Real-time weather forecasting using Open-Meteo and reverse geocoding.
- Smart farming alerts (rain probability, irrigation advice, extreme weather warnings, 7-day temperature trends).

### 4. Plants, Nurseries & Care Management
- Plant database with growth stages, watering cycles, and sunshine needs.
- Live Geolocation search for nearby nurseries.
- Scheduled watering and care reminders.

### 5. Marketplace, Community & Expenses
- Plants, gardening tools, fertilizers, and seed marketplace with cart and checkout.
- Social community feed for gardeners to share updates and seek advice.
- Garden expense tracking and analytics.

---

## Technology Stack

- **Framework**: Django 4.2 LTS & Django REST Framework (DRF)
- **Authentication**: JWT (JSON Web Tokens) via `djangorestframework-simplejwt`
- **Machine Learning**: TensorFlow 2.x, Keras 3.x, NumPy, Pillow
- **Generative AI**: Google Gemini Multimodal APIs (Flash Vision & Audio)
- **Database**: PostgreSQL (Production) / SQLite (Local Dev)
- **Web Server**: Gunicorn with WhiteNoise (Compressed Static Storage)

---

## Repository Structure

```
plantica_backend/
├── build.sh                      # Render automated build & migration script
├── Procfile                      # Web process definition for Gunicorn
├── render.yaml                   # Infrastructure-as-Code Blueprint for Render
├── requirements.txt              # Production Python dependencies
├── .env.example                  # Environment variables template
├── plantica_core/                # Django project root
│   ├── manage.py
│   ├── authentication/           # User registration, JWT auth, profiles
│   ├── plants/                   # Plant library, weather intelligence, nurseries
│   ├── disease/                  # Dual-engine disease detection (ML & AI Vision)
│   │   ├── ml_models/            # Model weights (best_model.keras, classes.json)
│   │   ├── gemini_vision_service.py
│   │   ├── model_loader.py
│   │   └── openai_services.py
│   ├── ai_assistant/             # Multimodal AI Chatbot & Voice Assistant
│   ├── tasks/                    # Automated gardening task scheduler
│   ├── community/                # Social feed, posts, comments
│   ├── marketplace/              # Products, cart, orders, checkout
│   ├── expenses/                 # Expense tracking & financial analytics
│   ├── notifications/            # In-app notification center
│   └── plantica_core/            # Main settings, URLs, WSGI
└── README.md
```

---

## API Endpoint Reference

### Authentication (`/api/v1/auth/`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register/` | Create a new user account |
| `POST` | `/api/v1/auth/login/` | Obtain JWT access and refresh tokens |
| `POST` | `/api/v1/auth/token/refresh/` | Refresh expired access token |
| `GET` | `/api/v1/auth/profile/` | Get current user profile |

---

### Disease Detection (`/api/v1/disease/`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/disease/detect/ai/` | Pure Generative AI Vision detection from image |
| `POST` | `/api/v1/disease/detect/ml/` | Kaggle EfficientNetV2 ML model detection |
| `POST` | `/api/v1/disease/detect/` | Unified detection endpoint (`mode='ai'` or `'ml'`) |

#### Sample Request (`multipart/form-data`):
- `image`: *(File - plant leaf image)*
- `plant_name`: *(Optional string - e.g. "টমেটো")*

#### Sample Response:
```json
{
  "status": true,
  "message": "এআই ভিশন দিয়ে রোগ সফলভাবে সনাক্ত করা হয়েছে",
  "data": {
    "detection_engine": "Generative AI Vision",
    "plant_name": "টমেটো",
    "formatted_title": "টমেটো: আর্লি ব্লাইট (পাতার দাগ রোগ)",
    "raw_disease_label": "Early Blight (Alternaria solani)",
    "confidence_percentage": 94.5,
    "confidence_text": "৯৪.৫% নিশ্চিত",
    "severity": "মাঝারি ঝুঁকি",
    "treatment_plan": [
      "১. আক্রান্ত পাতাগুলো কেটে ফেলে দিন বা পুড়িয়ে ফেলুন।",
      "২. ডাইথেন এম-৪৫ (ম্যানকোজেব) প্রতি লিটার পানিতে ২ গ্রাম হারে স্প্রে করুন।",
      "৩. নিম তেল ও সাবান পানির মিশ্রণ পাতার উভয় পিঠে স্প্রে করুন।",
      "৪. বিকেলে স্প্রে করুন এবং গাছে অতিরিক্ত পানি দেওয়া বন্ধ রাখুন।"
    ],
    "prevention_guide": [
      "১. জমিতে সবসময় পর্যাপ্ত আলো-বাতাস চলাচলের ব্যবস্থা রাখুন।",
      "২. সেচ দেওয়ার সময় পানি সরাসরি পাতায় না ফেলে গোড়ায় দিন।",
      "৩. রোগ প্রতিরোধী জাতের বীজ ব্যবহার করুন।",
      "৪. শস্য পর্যায়ক্রম (Crop Rotation) মেনে চলুন।"
    ]
  },
  "code": 200
}
```

---

### AI Agricultural Chatbot & Voice Assistant (`/api/v1/ai/`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/ai/chat/` | Send message (Text, Image, or Voice) |
| `POST` | `/api/v1/ai/voice/` | Dedicated Bengali Voice query endpoint |
| `GET` | `/api/v1/ai/chat/history/<conversation_id>/` | Fetch thread conversation history |
| `GET` | `/api/v1/ai/chat/conversations/` | List past conversation sessions |

---

### Weather Intelligence (`/api/v1/plants/`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/plants/weather/?lat=23.8103&lon=90.4125` | Hyperlocal weather & farming advice |
| `GET` | `/api/v1/plants/nurseries/search/?lat=...&lon=...` | Find nearby physical plant nurseries |

---

## Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/plantica_backend.git
cd plantica_backend
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Fill in the required keys in `.env` (Database credentials, Gemini API key, etc.).

### 5. Run Migrations & Start Server
```bash
cd plantica_core
python manage.py migrate
python manage.py runserver
```
Backend will be live at `http://127.0.0.1:8000/`.

---

## Render Production Deployment

### Option A: Using Render Blueprint (Recommended)
1. Push this repository to GitHub.
2. Go to Render Dashboard -> Blueprints -> New Blueprint Instance.
3. Connect your repository. Render will automatically provision:
   - Free Managed PostgreSQL Database
   - Free Python Web Service with automated migrations and WhiteNoise static asset serving.

### Option B: Manual Web Service Setup on Render
1. Create a New Web Service connected to your repository.
2. Set the following parameters:
   - Environment: Python 3
   - Build Command: `./build.sh`
   - Start Command: `gunicorn --chdir plantica_core plantica_core.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`
3. Add the following Environment Variables in Render Dashboard:
   - `PYTHON_VERSION` = `3.10.14`
   - `DEBUG` = `False`
   - `SECRET_KEY` = `<your-secure-django-secret-key>`
   - `DATABASE_URL` = `<your-postgresql-internal-database-url>`
   - `GEMINI_API_KEY` = `<your-google-gemini-api-key>`
   - `EMAIL_HOST_USER` = `<your-smtp-email>`
   - `EMAIL_HOST_PASSWORD` = `<your-smtp-app-password>`

---

## Security & Privacy Best Practices

- All API keys, database credentials, and SMTP email passwords are kept strictly inside private environment variables.
- Sensitive files (`.env`, `db.sqlite3`, `media/`) are excluded from version control via `.gitignore`.
- Production builds use SSL verification, CORS validation, and token rotation safeguards.

---

## License
This project is licensed under the MIT License — feel free to use and customize it for your agricultural and gardening applications.
