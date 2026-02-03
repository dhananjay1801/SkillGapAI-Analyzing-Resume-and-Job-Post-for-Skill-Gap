# SkillGapAI - Analyzing Resume and Job Post for Skill Gap

An intelligent AI-powered application that analyzes resumes against job descriptions to identify skill gaps and provide actionable recommendations for career development.

## Features

- **Resume Parsing**: Extract skills from PDF, DOCX, and text-based resumes
- **Job Description Analysis**: Parse and analyze job postings to extract required skills
- **Skill Gap Analysis**: Compare resume skills with job requirements using advanced NLP techniques
- **Smart Recommendations**: Get personalized skill recommendations
- **Visual Analytics**: Interactive charts showing skill match percentages and coverage
- **PDF Report Generation**: Download comprehensive skill gap analysis reports
- **Resume Generator**: Create professional resumes with ATS optimized template

## Tech Stack

- **Frontend**: Streamlit
- **NLP**: spaCy, Transformers (JobBERT), Sentence-Transformers
- **ML Models**: Sentence-Transformer embeddings for semantic similarity
- **Visualization**: Plotly
- **PDF Generation**: WeasyPrint
- **File Processing**: PyPDF2, python-docx, EasyOCR

## Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/SkillGapAI-Analyzing-Resume-and-Job-Post-for-Skill-Gap.git
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install spaCy Language Model

The application requires the English language model for spaCy. It will attempt to download automatically on first use, but you can also install it manually:

```bash
python -m spacy download en_core_web_sm
```

### Step 5: Install WeasyPrint Dependencies

WeasyPrint requires external system dependencies to generate PDFs. Follow the instructions for your operating system:

#### Windows

1. **Download GTK3 Runtime:**
   - Visit: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
   - Download the latest installer
   - Run the installer and install to the default location: `C:\Program Files\GTK3-Runtime Win64\`

2. **Add to System PATH:**
   - Open System Properties → Environment Variables
   - Add `C:\Program Files\GTK3-Runtime Win64\bin` to your System PATH
   - Restart your terminal/IDE after adding to PATH

3. **Alternative: Manual DLL Path (if PATH doesn't work):**
   - The code automatically checks for GTK at `D:\Program Files\GTK3-Runtime Win64\bin`
   - If you installed to a different location, you may need to update the path in:
     - `pages/Resume_Generator.py` (line ~497)
     - `utils/report_generator.py` (line ~447)

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

#### macOS

```bash
brew install cairo pango gdk-pixbuf libffi
```

### Step 6: Verify Installation

Run the application to verify everything is set up correctly:

```bash
streamlit run Home.py
```

The application should open in your default web browser at `http://localhost:8501`

### Run with Docker (prebuilt image)

You can also run SkillGapAI using the prebuilt Docker image:

```bash
docker pull dhananjay1801/skillgap-ai
docker run -p 8501:8501 dhananjay1801/skillgap-ai
```

Then open `http://localhost:8501`.

Note: The first run may take a few minutes because the required ML/NLP models are downloaded on first use.

## Model Locations

The application uses several pre-trained models that are automatically downloaded on first use. Here are their default storage locations:

### Hugging Face Models

**Default Location:** `~/.cache/huggingface/hub/`

**Models Used:**
- **Sentence-Transformer** (`sentence-transformers/all-MiniLM-L6-v2`)
  - Used for: Skill embeddings and semantic similarity (technical + soft skills, gap analysis, recommendations)
  - Size: ~100 MB
  - Path: `~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/`

- **JobBERT Skill Extraction** (`jjzha/jobbert_skill_extraction`)
  - Used for: Named Entity Recognition (NER) to extract skills from text
  - Size: ~440 MB
  - Path: `~/.cache/huggingface/hub/models--jjzha--jobbert_skill_extraction/`

**Windows Example Path:**
```
C:\Users\<YourUsername>\.cache\huggingface\hub\
```

### spaCy Models

**Default Location:** Varies by installation method

**Model Used:**
- **English Core Web SM** (`en_core_web_sm`)
  - Used for: Phrase matching and text processing
  - Size: ~15 MB

**Installation Locations:**
- **Via pip:** `venv/Lib/site-packages/en_core_web_sm/` (if installed in venv)
- **Via spacy CLI:** `~/.local/share/spacy/` (user directory) or system-wide

**Check Installation:**
```bash
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print(nlp.path)"
```

### Clearing Model Cache

If you need to free up space or re-download models:

**Hugging Face Models:**
```bash
# Delete specific model
rm -r ~/.cache/huggingface/hub/models--bert-base-uncased/

# Or delete entire cache
rm -r ~/.cache/huggingface/
```

**spaCy Models:**
```bash
# Re-download model
python -m spacy download en_core_web_sm --force
```

## Usage

### Using Skill Gap Analysis

1. **Upload Resume**: Upload your resume (PDF, DOCX, or paste text)
2. **Enter Job Description**: Paste the job description text
3. **Analyze**: Click "Analyze Skill Gap" to generate the analysis
4. **View Results**: 
   - See overall match percentage
   - Review matched, partial, and missing skills
   - Explore skill recommendations
   - View interactive charts (pie charts, radar chart)
5. **Download Report**: Click "Download PDF Report" to save a comprehensive analysis

### Using Resume Generator

1. Navigate to the Resume Generator page
2. Fill in your information in the sidebar
3. Customize sections as needed
4. Preview your resume
5. Download as PDF

## Troubleshooting

### WeasyPrint Issues

**Error: "Failed to load WeasyPrint"**
- Ensure GTK3 Runtime is installed (Windows)
- Verify GTK bin directory is in PATH
- Restart terminal/IDE after PATH changes

**Error: "Cannot find GTK libraries"**
- Check installation path matches code expectations
- Update paths in `Resume_Generator.py` and `report_generator.py` if needed

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.

