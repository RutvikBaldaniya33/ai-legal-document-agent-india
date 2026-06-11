# 🎯 QUICK REFERENCE CARD

## Launch Your Hackathon App in 5 Minutes

### Step 1️⃣ — Setup Environment (1 minute)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2️⃣ — Configure Secrets (2 minutes)

Copy and configure `.env`:
```bash
cp env.example .env
```

Edit `.env` and add:
```
GEMINI_API_KEY=your_key_here
MONGODB_URI=your_connection_string_here
DB_NAME=legal_agent
```

### Step 3️⃣ — Verify Setup (1 minute)

```bash
python verify_setup.py
```

Should show all ✓ checks passed.

### Step 4️⃣ — Launch App (30 seconds)

```bash
streamlit run app.py
```

Opens automatically at: **http://localhost:8501**

---

## 📋 What You Get

### 5 Core Features

| # | Feature | Input | Output |
|---|---------|-------|--------|
| 1 | Classifier | Dispute text | Type + State |
| 2 | Law Retriever | Type + State | Relevant laws |
| 3 | Evidence | PDF/Images | Names, dates, amounts |
| 4 | Case Strength | All above | Score 0-100 |
| 5 | Notice | Full case | Legal document |

### UI Layout

```
┌─────────────────────────────────────────────┐
│  ⚖️  AI LEGAL DOCUMENT AGENT - India       │
├──────────────┬──────────────────────────────┤
│  SIDEBAR     │  MAIN AREA                   │
│              │                              │
│ 📄 Documents │ 📋 Describe Your Dispute    │
│ 📤 Upload    │                              │
│              │ [Text input area]            │
│ 👤 Parties   │                              │
│ [Names]      │ 👥 Claimant: John Doe      │
│              │ 👥 Respondent: Owner       │
│              │                              │
│              │ 🚀 PROCESS BUTTON           │
│              ├──────────────────────────────┤
│              │ 📊 RESULTS (5 Tabs)         │
│              │                              │
│              │ [Classification]            │
│              │ [Laws]                      │
│              │ [Facts]                     │
│              │ [Case Strength: 72/100]     │
│              │ [Legal Notice - Download]   │
│              │                              │
└──────────────┴──────────────────────────────┘
```

---

## 🧪 Demo Dispute (Copy-Paste)

**Claimant:** Rajesh Kumar
**Respondent:** Property Owner
**Dispute:**
```
Landlord not returning ₹50,000 security deposit after 3 months.
I rented a 2-bedroom flat in Surat, Gujarat for ₹15,000/month.
Lease agreement signed on January 1, 2023. I vacated on December 31, 2023.
Owner says he's keeping deposit for "maintenance costs" but provided no invoice.
I have emails requesting the deposit back and WhatsApp messages.
His number is 98765-43210. I'm losing patience.
```

---

## ⚙️ API Keys (2 minutes to get)

### Gemini API Key
1. Go to https://ai.google.dev
2. Click "Get API Key"
3. Sign in with Google
4. Create key → Copy → Paste in `.env`

### MongoDB Connection
1. Go to https://www.mongodb.com/cloud/atlas
2. Create account (free M0 cluster)
3. Click "Connect" → "Drivers"
4. Copy connection string
5. Edit: `<username>`, `<password>`, `<cluster>`
6. Paste in `.env`

---

## 📊 Expected Results

When you process a dispute, you'll see:

### Tab 1: Classification ✅
```
Dispute Type: TENANT
State: Gujarat
```

### Tab 2: Laws ✅
```
• Gujarat Rent Control Act, 1961
• Indian Penal Code Section 406
• Consumer Protection Act 2019
```

### Tab 3: Facts ✅
```
Names: Rajesh Kumar, Property Owner
Dates: Jan 1 2023 - Dec 31 2023
Amounts: ₹50,000 deposit
Addresses: Surat, Gujarat
Facts: Breach of agreement, no explanation for retention
```

### Tab 4: Case Strength ✅
```
Score: 72/100 - STRONG

Breakdown:
• Agreement: 20/25 ✓
• Payment: 18/20 ✓
• Communication: 12/15 ✓
• Law Match: 9/10 ✓
• Timeline: 7/8 ✓
• Witnesses: 4/7
• Documentation: 10/15

Strengths:
✓ Clear written agreement
✓ Communication trail via email/WhatsApp
✓ Good law support

Risks:
⚠ Missing photos of property condition
⚠ No independent witness
```

### Tab 5: Legal Notice ✅
```
[Full formal legal notice generated]
[Consumer complaint if applicable]
[Executive summary]

📥 Download as TXT file
```

---

## 🚨 If Something Goes Wrong

| Problem | Solution |
|---------|----------|
| "ModuleNotFoundError" | Run `pip install -r requirements.txt` again |
| "GEMINI_API_KEY not found" | Check `.env` file has correct key |
| "Streamlit not opening" | Check http://localhost:8501 manually |
| "MongoDB connection error" | Verify connection string in `.env` |
| "Slow responses" | Normal on first run; wait 30 seconds |
| Port 8501 already in use | Kill other Streamlit instances or restart |

**Quick fix for any issue:**
```bash
python verify_setup.py
```

---

## ✨ Key Features

✅ **One-click processing** - Enter dispute → Get results
✅ **Professional UI** - Clean, minimal black & white
✅ **All results on one screen** - No navigation needed
✅ **Document support** - Upload PDF/images for fact extraction
✅ **Explainable AI** - See why case scores 72/100
✅ **Ready-to-send notices** - Download and send to court
✅ **Real Indian laws** - Actual applicable statutes
✅ **Fast processing** - ~30 seconds total

---

## 📊 Tech Stack

```
Frontend:  Streamlit (Python)
Backend:   Python (Flask-less, async)
AI:        Google Gemini 2.5 Flash
Database:  MongoDB Atlas
Hosting:   Streamlit Cloud / Docker / Local
```

---

## 🎬 Full Demo (5 minutes)

1. **Open app** → `streamlit run app.py`
2. **Fill sidebar** → Names + optionally upload document
3. **Enter dispute** → Copy the demo dispute above
4. **Click button** → "PROCESS & GENERATE LEGAL NOTICE"
5. **Review results** → Click through 5 tabs
6. **Download** → Get legal notice as TXT file
7. **Done!** 🎉

---

## 📁 File Reference

**Main Files:**
- `app.py` - Start here! Main UI
- `.env` - Your secrets go here
- `requirements.txt` - Dependencies

**Core Modules:**
- `classifier.py` - Categorizes disputes
- `law_retriever.py` - Finds relevant laws
- `evidence_extractor.py` - Analyzes documents
- `case_strength.py` - Scores likelihood of success
- `legal_notice.py` - Generates formal notices

**Utilities:**
- `verify_setup.py` - Check everything works
- `README.md` - Full documentation
- `LAUNCH.md` - Deployment guide

---

## 🎯 Pro Tips

1. **First run:** Application compiles Gemini models - give it 30 seconds
2. **Rate limits:** Free Gemini API limited to ~60 req/minute
3. **MongoDB:** Free tier allows 512MB storage - plenty for this
4. **Documents:** Upload 1-2 documents for better fact extraction
5. **Save notice:** Download and have lawyer review before sending

---

## 🏆 You're Ready!

Everything is configured and ready to go.

**Run:**
```bash
streamlit run app.py
```

**Explore:** 5 tabs with complete legal analysis
**Demo:** Copy-paste the dispute above
**Export:** Download professional legal notices

**Good luck with your hackathon! 🚀**

---

*AI Legal Document Agent — India*
*Hackathon Submission 2026*
