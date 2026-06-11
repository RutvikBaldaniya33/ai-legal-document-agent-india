# 🚀 DEPLOYMENT & LAUNCH GUIDE

## Quick Start (30 seconds)

```bash
# 1. Setup environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure secrets (.env file)
cp env.example .env
# Edit .env and add:
#   - GEMINI_API_KEY
#   - MONGODB_URI

# 4. Verify setup
python verify_setup.py

# 5. Launch
streamlit run app.py
```

App opens at: **http://localhost:8501**

---

## ✅ Pre-Launch Checklist

- [ ] Python 3.9+ installed (`python --version`)
- [ ] Virtual environment created and activated
- [ ] `pip install -r requirements.txt` completed
- [ ] `.env` file created with GEMINI_API_KEY
- [ ] `.env` file created with MONGODB_URI
- [ ] `python verify_setup.py` shows all green
- [ ] `streamlit run app.py` launches without errors

---

## 🧪 Testing the Application

### Test Case 1: Tenant Dispute
1. Open app at http://localhost:8501
2. In sidebar, enter:
   - Claimant Name: "John Doe"
   - Respondent Name: "Property Owner"
3. In main area, enter dispute:
   ```
   Landlord not returning ₹50,000 security deposit after 3 months 
   in Surat, Gujarat. I have a signed lease agreement and email 
   requesting the deposit back dated March 15, 2024.
   ```
4. Click "PROCESS & GENERATE LEGAL NOTICE"
5. Verify results appear in tabs

### Test Case 2: Consumer Dispute
1. Enter:
   - Claimant Name: "Priya Kumar"
   - Respondent Name: "Amazon India"
2. Dispute:
   ```
   Amazon delivered a MacBook for ₹89,999 with a broken screen.
   They refused replacement. Order number ORD-2024-001234.
   I have photos of the damage and order receipt.
   ```
3. Process and verify results

### Test Case 3: Document Upload
1. Upload a PDF or image with legal documents
2. Check "Auto-extract facts from documents"
3. Enter dispute and process
4. Verify extracted facts appear in "Extracted Facts" tab

---

## 📊 Expected Output

When case is processed successfully, you should see:

**Tab 1: Classification**
- Dispute Type: Tenant or Consumer
- State: Indian state identified

**Tab 2: Relevant Laws**
- List of applicable Indian laws/acts
- Each expandable to see details

**Tab 3: Extracted Facts**
- Names, dates, amounts, addresses extracted
- Important facts summarized

**Tab 4: Case Strength**
- Score out of 100 (e.g., 72/100)
- Breakdown by category
- Analysis and risk factors

**Tab 5: Legal Notice**
- Full formal legal notice text
- Consumer complaint (if applicable)
- Executive summary
- Download button

---

## ⚙️ Environment Setup Details

### Gemini API Key
1. Go to https://ai.google.dev
2. Click "Get API Key"
3. Sign in with Google
4. Create new API key
5. Copy key to `.env`: `GEMINI_API_KEY=your_key`

### MongoDB URI
1. Go to https://www.mongodb.com/cloud/atlas
2. Create account or sign in
3. Create new cluster (M0 free tier)
4. Click "Connect"
5. Choose "Drivers" connection
6. Copy connection string
7. Replace `<username>`, `<password>`, `<cluster>`
8. Add to `.env`: `MONGODB_URI=your_uri`

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError" | Run `pip install -r requirements.txt` |
| "GEMINI_API_KEY not found" | Check `.env` file exists and has correct key |
| "MongoDB connection failed" | Verify MONGODB_URI, check IP whitelist |
| "Streamlit not starting" | Check port 8501 is free or restart PC |
| "Slow responses" | First run is slow; Gemini API may have limits |

---

## 📁 Project File Structure

```
agent/
├── app.py                      # Main Streamlit application ⭐
├── classifier.py               # Dispute classification module
├── law_retriever.py           # Law retrieval from MongoDB
├── evidence_extractor.py      # Document analysis module
├── case_strength.py           # Case strength calculator
├── legal_notice.py            # Notice generator
├── mongodb.py                 # MongoDB operations
├── utils.py                   # Utility functions
├── verify_setup.py            # System verification script ✓
├── requirements.txt           # Python dependencies
├── README.md                  # Full documentation
├── LAUNCH.md                  # This file
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── .streamlit/
│   └── config.toml            # Streamlit configuration
└── prompts/
    ├── classifier.txt         # Classification prompt
    ├── evidence_extractor.txt # Evidence extraction prompt
    ├── case_strength.txt      # Case strength prompt
    └── legal_notice.txt       # Notice generation prompt
```

---

## 🎯 Key Features Working

✅ **Dispute Classification** - Identifies tenant vs consumer + state
✅ **Law Retrieval** - Fetches relevant Indian laws
✅ **Evidence Extraction** - Analyzes PDF/images with Gemini Vision
✅ **Case Strength** - Calculates 0-100 score with breakdown
✅ **Legal Notice** - Generates professional notices
✅ **Clean UI** - Minimal, professional black & white design
✅ **Document Download** - Export notices as TXT files
✅ **Multi-Tab Results** - All information organized clearly

---

## 🎓 Architecture

```
User Input (Streamlit UI)
        ↓
Classifier (Gemini)
   ↓         ↓
Type      State
   ↓         ↓
Law Retriever (MongoDB)
   ↓
Evidence Extractor (Gemini Vision) [Optional]
   ↓
Case Strength Calculator (Gemini)
   ↓
Legal Notice Generator (Gemini)
   ↓
Display in Tabs + Download
```

---

## 📞 Support

If you encounter issues:

1. **First check**: Run `python verify_setup.py`
2. **Check logs**: Look at console output for error messages
3. **Verify config**: Ensure `.env` has correct keys
4. **Check internet**: All APIs require internet connection
5. **API limits**: Gemini free tier has rate limits (~60 req/min)

---

## 🚀 Deployment Options

### Option 1: Local Development
```bash
streamlit run app.py
```

### Option 2: Docker
```bash
docker build -t legal-agent .
docker run -p 8501:8501 legal-agent
```

### Option 3: Cloud (Heroku)
```bash
git push heroku main
```

---

## ✨ Demo Mode

To test without Gemini/MongoDB:

1. The app validates credentials on startup
2. If missing, it shows helpful error messages
3. Check LAUNCH.md → Environment Setup for details

---

**Last Updated:** 2026-06-11  
**Status:** Ready for Hackathon Submission ✓
