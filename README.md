# AI Legal Document Agent — India

A hackathon-winning submission that provides end-to-end legal document analysis and notice generation for Indian legal disputes.

## 🎯 Project Overview

This AI Legal Document Agent helps users with tenant and consumer disputes by:

1. **Classifying** the dispute type and jurisdiction
2. **Retrieving** relevant Indian laws and acts
3. **Extracting** facts from uploaded documents (PDF, images, screenshots)
4. **Calculating** case strength with explainable scoring
5. **Generating** professional legal notices ready for filing

**Tech Stack:**
- Python 3.9+
- FastAPI (backend framework)
- MongoDB Atlas (law database)
- Google Gemini 2.5 Flash (AI analysis & vision)
- Streamlit (frontend UI)
- Pydantic (data validation)

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google Gemini API key (free tier available)
- MongoDB Atlas account (free tier)
- pip package manager

### Installation

1. **Clone/Extract the project:**
```bash
cd agent
```

2. **Create virtual environment:**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=legal_agent
```

**Getting API Keys:**

- **Gemini API Key:** 
  - Visit https://ai.google.dev
  - Sign in with Google account
  - Create API key (free tier available)
  - Copy and paste in `.env`

- **MongoDB URI:**
  - Visit https://www.mongodb.com/cloud/atlas
  - Create free account
  - Create new cluster
  - Click "Connect" → "Drivers"
  - Copy connection string
  - Replace `<username>`, `<password>`, and `<cluster>` with your credentials

5. **Populate laws database (optional):**

If you have a CSV or JSON file with Indian laws, you can seed the MongoDB database. Otherwise, the app uses Gemini's knowledge base.

### Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📋 Features

### 1. Dispute Classification
- Classifies disputes into: **Tenant** or **Consumer**
- Detects Indian state/jurisdiction
- Uses Gemini with zero-shot classification

### 2. Law Retrieval
- Retrieves relevant laws from MongoDB
- Fallback to general/central acts
- Supports state-specific legislation

### 3. Evidence Extraction
- Supports: PDF, PNG, JPEG, GIF, WebP
- Extracts:
  - Names of parties
  - Important dates
  - Monetary amounts
  - Addresses
  - Key facts and timeline
- Uses Gemini Vision for accurate OCR and understanding

### 4. Case Strength Calculation
- Scores 0-100 based on evidence quality
- Breakdown by category:
  - Agreement Present (25 pts)
  - Payment Proof (20 pts)
  - Communication Evidence (15 pts)
  - Law Match (10 pts)
  - Timeline Consistency (8 pts)
  - Witnesses (7 pts)
  - Documentation Completeness (15 pts)
- Identifies strengths and risk factors
- Provides explainable reasoning

### 5. Legal Notice Generation
- Generates formal legal notices
- Consumer complaint documents
- Professional formatting suitable for filing
- Includes applicable law sections
- Different formats for tenant vs. consumer disputes

## 🏗️ Project Structure

```
agent/
├── app.py                          # Main Streamlit UI
├── classifier.py                   # Dispute classification
├── law_retriever.py               # Law retrieval from MongoDB
├── evidence_extractor.py          # Document analysis & fact extraction
├── case_strength.py               # Case strength calculation
├── legal_notice.py                # Legal notice generation
├── mongodb.py                     # MongoDB connection & operations
├── utils.py                       # Utility functions
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── prompts/
│   ├── classifier.txt             # Classification prompt
│   ├── evidence_extractor.txt     # Evidence extraction prompt
│   ├── case_strength.txt          # Case strength prompt
│   └── legal_notice.txt           # Legal notice prompt
└── README.md                      # This file
```

## 💻 Usage Examples

### Example 1: Tenant Dispute

**Input:**
```
Landlord not returning my ₹50,000 security deposit after 3 months in Surat, Gujarat.
I have a signed agreement and WhatsApp messages asking for the deposit back.
The owner keeps giving excuses.
```

**Output:**
- Classification: Tenant dispute in Gujarat
- Relevant laws: Gujarat Rent Act, IPC sections
- Extracted facts: Deposit amount, dates, communication
- Case strength: 72/100 (Strong)
- Generated legal notice ready to send

### Example 2: Consumer Dispute

**Input:**
```
Amazon delivered a damaged laptop. I ordered a MacBook Pro for ₹1,29,999 but it arrived with a broken screen.
They refused to replace it. I have photos of the damage and my order receipt.
```

**Output:**
- Classification: Consumer dispute
- Relevant laws: Consumer Protection Act 2019, IPC
- Extracted facts: Item, amount, damage photos analyzed
- Case strength: 85/100 (Very Strong)
- Generated consumer complaint

## 🎨 UI Design

The Streamlit interface follows a clean, professional design:

- **Black & White theme** - Professional appearance
- **Minimal design** - No distracting effects
- **Single screen** - All results visible without scrolling
- **Sidebar** - Document uploads and party information
- **Tabbed results** - Classification, Laws, Facts, Strength, Notice
- **Download feature** - Export legal notices as TXT

## 🔧 Troubleshooting

### "GEMINI_API_KEY not found"
- Check `.env` file exists in project root
- Verify API key is correct
- Make sure there are no extra spaces

### "MONGODB_URI connection failed"
- Check MongoDB connection string in `.env`
- Verify username and password
- Ensure IP is whitelisted in MongoDB Atlas
- Test connection: `python test_mongodb.py`

### "Module not found" errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Try `pip install --upgrade pip`

### Streamlit not starting
- Check all dependencies: `pip list`
- Try `streamlit hello` to verify Streamlit works
- Check port 8501 is not in use

### Gemini API rate limits
- Free tier has limits (~60 requests/minute)
- Wait a few minutes before retrying
- For production, consider paid Gemini tier

## 📊 Case Strength Scoring

### Score Ranges:
- **80-100:** Very Strong case, likely to succeed in court
- **60-79:** Strong case, good chance of success
- **40-59:** Moderate case, outcome uncertain
- **20-39:** Weak case, significant challenges
- **0-19:** Very weak case, unlikely to succeed

### Factors Considered:
1. **Agreement Quality** - Is there a valid written agreement?
2. **Payment Evidence** - Bank statements, receipts, proof of payment
3. **Communication Trail** - Emails, messages, chat history
4. **Law Application** - How well do applicable laws support your case
5. **Timeline** - Clear chronology without suspicious gaps
6. **Witnesses** - Independent corroboration of facts
7. **Documentation** - Completeness of supporting evidence

## 🚀 Deployment

### For Local Development:
```bash
streamlit run app.py
```

### For Heroku/Cloud Deployment:

1. Create `Procfile`:
```
web: streamlit run app.py
```

2. Create `.streamlit/config.toml`:
```toml
[server]
headless = true
port = $PORT

[browser]
serverAddress = "0.0.0.0"
```

3. Deploy:
```bash
git push heroku main
```

### For Docker:

1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

2. Build and run:
```bash
docker build -t legal-agent .
docker run -p 8501:8501 legal-agent
```

## 📝 Legal Notice

**Disclaimer:**
- This tool provides AI-generated legal documents for educational purposes
- The generated notices should be reviewed by a qualified lawyer before sending
- The tool does NOT provide legal advice or guarantee case success
- Always verify with a legal professional before filing

## 🎓 How It Works

### Processing Pipeline:

```
User Dispute Text
        ↓
    Classifier (Gemini)
   Determines type & state
        ↓
    Law Retriever
  Fetches relevant laws
        ↓
Document Upload (Optional)
    Evidence Extractor (Gemini Vision)
   Extracts facts from docs
        ↓
    Case Strength Calculator
   Scores likelihood of success
        ↓
  Legal Notice Generator
 Creates professional notice
        ↓
    User Reviews & Downloads
```

## 🧪 Testing

Test individual modules:

```bash
# Test Gemini connection
python test_gemini.py

# Test classifier
python classifier.py

# Test law retriever
python law_retriever.py

# Test evidence extractor
python evidence_extractor.py
```

## 📚 Dependencies

See `requirements.txt` for complete list. Key packages:
- `streamlit` - Web UI framework
- `google-generativeai` - Gemini API access
- `pymongo` - MongoDB driver
- `pydantic` - Data validation
- `PyMuPDF` - PDF processing
- `pillow` - Image processing

## 🤝 Contributing

To extend this project:

1. Add new dispute types in `classifier.py`
2. Add state-specific laws in MongoDB
3. Extend prompts for better results
4. Add new document types in `evidence_extractor.py`

## 📧 Support

For issues or questions:
1. Check the README
2. Review error messages in console
3. Check environment variables
4. Verify API keys and credentials

## 📄 License

This project is provided as-is for hackathon evaluation.

## 🎯 Future Enhancements

- [ ] Vector search with embeddings for better law retrieval
- [ ] Multi-language support
- [ ] Case history database
- [ ] Lawyer referral system
- [ ] Case tracking dashboard
- [ ] Auto-fill from document extraction
- [ ] Mobile app version
- [ ] Integration with legal filing systems

---

**Built with ❤️ for hackathon submission**

Last updated: 2026-06-11
