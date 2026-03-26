# ⚡ NexaSales AI — Enterprise Sales Forecasting Platform

A full-stack DevOps + AI project with a company-grade marketing website, multi-environment deployment, and advanced analytics dashboard.

---

## 🚀 What's New (v2 — Advanced)

| Feature | Old | New |
|---|---|---|
| Landing page | None | Full company marketing website with stock ticker, KPI cards, 5 live charts |
| Prediction inputs | 3 (marketing, visits, price) | **7** (+ season, region, ad channel, discount) |
| Prediction output | Single number | Predicted revenue + **AI insights** + **3 scenario charts** |
| Historical data | None | 3-year trend (2022–2024), quarterly split, YoY comparison |
| Data storage | None | **SQLite (default)** — switch to Postgres/MySQL via env var |
| Environments | 3 containers | 3 containers with **isolated named volumes** per environment |
| Charts | 1 bar chart | **10+ charts** across landing + dashboard |

---

## 📁 Project Structure

```
ai-devops-project/
├── app.py              ← Flask backend (all routes + DB logic)
├── train_model.py      ← ML model training
├── sales_model.pkl     ← Trained model
├── requirements.txt
├── Dockerfile
├── docker-compose.yml  ← DEV(8081) · TEST(8082) · PROD(8083)
├── Jenkinsfile         ← CI/CD pipeline
├── templates/
│   ├── landing.html    ← Company marketing website (opens on container start)
│   └── dashboard.html  ← Advanced analytics dashboard
└── static/
```

---

## 🏁 Quick Start

```bash
# Build & start all 3 environments
docker-compose up -d --build

# Open in browser:
# Landing page  → http://localhost:8081  (DEV)
#               → http://localhost:8082  (TEST)
#               → http://localhost:8083  (PROD)
#
# Dashboard     → http://localhost:8081/dashboard
```

---

## 💾 Data Storage

Every prediction made by users is **automatically stored** in a database.

| Storage | How to configure |
|---|---|
| **SQLite** (default) | Nothing to change — `DB_PATH=sales_data.db` |
| **PostgreSQL** | Set `DB_PATH=postgresql://user:pass@host:5432/db` in docker-compose |
| **MySQL** | Set `DB_PATH=mysql://user:pass@host:3306/db` in docker-compose |

Data persists across container restarts via **Docker named volumes** (`dev-data`, `test-data`, `prod-data`).

### View stored predictions:
```bash
# From inside container
docker exec -it ai-devops-dev sqlite3 /app/data/dev_sales.db "SELECT * FROM predictions;"
```

---

## 🤖 AI Prediction Features

The `/predict` endpoint accepts **7 parameters**:

| Parameter | Type | Effect |
|---|---|---|
| `marketing` | number | Base marketing spend |
| `visits` | number | Customer visits |
| `price` | number | Product price |
| `season` | Q1/Q2/Q3/Q4 | Seasonal multiplier (Q4 = 1.3×) |
| `region` | North/South/East/West/Central | Regional demand multiplier |
| `ad_channel` | Social/TV/Email/SEO/Influencer/Print | Channel effectiveness multiplier |
| `discount` | 0–50% | Price reduction |

Returns:
- Predicted revenue
- AI-generated improvement recommendations
- 4-scenario what-if analysis (at different marketing budgets)

---

## 📊 Charts & Analytics

### Landing Page (`/`)
- Live stock ticker (company + market indices)
- KPI cards (revenue, growth, market share, peak)
- Revenue trend 2022–2024
- Quarterly doughnut chart
- Share price (30-day simulation)
- Trade volume (30-day)
- Market share vs industry average

### Dashboard (`/dashboard`)
- Year filter (2022 / 2023 / 2024 / All)
- Revenue trend line
- Growth rate bar chart
- Quarterly split doughnut
- Market share vs industry line
- Year-over-year comparison bar
- Prediction form with 7 inputs
- Result: predicted amount + AI insights
- Prediction bar chart
- Marketing scenario comparison
- What-if line chart
- Full prediction history table

---

## 🔧 CI/CD Pipeline

Jenkins stages:
1. `Clone Repo`
2. `Build Docker Image`
3. `Stop Old Containers`
4. `Run All Environments`
5. `Health Check` (curl all 3 ports)

---

## 👩‍🏫 Teacher's Question: Where is data stored?

**All user prediction data is stored in SQLite databases** (one per environment):
- `dev-data` volume → `/app/data/dev_sales.db`
- `test-data` volume → `/app/data/test_sales.db`
- `prod-data` volume → `/app/data/prod_sales.db`

To use **PostgreSQL or MySQL instead**, change one line in `docker-compose.yml`:
```yaml
environment:
  - DB_PATH=postgresql://user:password@your-db-host:5432/nexasales
```
No code changes needed — just the environment variable.
