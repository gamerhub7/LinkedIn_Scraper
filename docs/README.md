# LinkedIn Email Generator

A powerful LinkedIn profile scraper and personalized email generator that uses AI to extract profile information and create professional, personalized outreach emails.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Expected Output](#expected-output)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This application automates the process of:
1. **Scraping LinkedIn profiles** - Extracts name, title, company, and full About section
2. **Expanding "see more" sections** - Automatically clicks "see more" buttons to get complete profile data
3. **Generating personalized emails** - Uses AI to create professional outreach emails based on profile details

### Key Features

✅ **LLM-Based Extraction** - Uses GPT-4 for robust data extraction instead of fragile CSS selectors
✅ **"See More" Auto-Expansion** - Automatically expands truncated sections for complete data
✅ **Dual AI Provider Support** - Works with both Azure OpenAI and regular OpenAI
✅ **LinkedIn Login** - Supports both credential-based and Chrome profile login
✅ **Comprehensive Logging** - Detailed logs for debugging and monitoring
✅ **Error Handling** - Robust error handling with retry logic
✅ **Pydantic Validation** - Ensures data integrity with schema validation

---

## 🛠 Tech Stack

### Core Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Programming language | 3.8+ |
| **Playwright** | Browser automation for LinkedIn scraping | ≥1.40.0 |
| **OpenAI API** | LLM for data extraction and email generation | ≥1.0.0 |
| **Azure OpenAI** | Alternative LLM provider | ≥1.0.0 |
| **BeautifulSoup4** | HTML parsing and text extraction | ≥4.12.0 |
| **Pydantic** | Data validation and schema enforcement | ≥2.0.0 |

### Key Libraries

- **python-dotenv** - Environment variable management
- **lxml** - XML/HTML processing
- **requests** - HTTP requests
- **colorlog** - Colored logging output

---

## 🔧 How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User Input (LinkedIn URL)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              LinkedIn Scraper V2 (Playwright)               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Login to LinkedIn (credentials/Chrome profile)    │   │
│  │ 2. Navigate to profile page                          │   │
│  │ 3. Click "see more" buttons to expand sections       │   │
│  │ 4. Extract HTML content                              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  HTML Cleaning & Processing                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Remove script/style tags                          │   │
│  │ 2. Extract text content (400K chars max)             │   │
│  │ 3. Clean excessive newlines                          │   │
│  │ 4. Save to extracted_text.txt for debugging          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│          LLM-Based Data Extraction (GPT-4)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Send text to OpenAI/Azure OpenAI                  │   │
│  │ 2. Extract structured JSON (name, title, company,    │   │
│  │    about)                                             │   │
│  │ 3. Validate with Pydantic schema                     │   │
│  │ 4. Retry up to 3 times on failure                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│             Email Generation (GPT-4)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Create personalized prompt with profile data      │   │
│  │ 2. Generate subject line and email body              │   │
│  │ 3. Validate with Pydantic schema                     │   │
│  │ 4. Return structured JSON                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Output (JSON + Console)                  │
│  • Profile data (name, title, company, about)              │
│  • Personalized email (subject + body)                     │
│  • Saved to result.json                                    │
└─────────────────────────────────────────────────────────────┘
```

### Workflow Steps

1. **Profile Fetching**
   - Uses Playwright to launch a Chromium browser
   - Logs into LinkedIn using credentials or Chrome profile
   - Navigates to the target profile page
   - Waits for content to load

2. **"See More" Expansion**
   - Detects buttons with `aria-expanded="false"` and text "see more"
   - Clicks all matching buttons to expand truncated sections
   - Ensures complete About section is visible

3. **HTML Extraction & Cleaning**
   - Extracts page HTML content
   - Uses BeautifulSoup to parse HTML
   - Removes script/style tags
   - Extracts plain text (up to 400K characters)
   - Saves to `extracted_text.txt` for debugging

4. **LLM-Based Data Extraction**
   - Sends cleaned text to OpenAI/Azure OpenAI
   - Uses structured prompts for JSON extraction
   - Validates response with Pydantic models
   - Retries up to 3 times on parsing errors

5. **Email Generation**
   - Creates personalized prompt using profile data
   - Generates subject line (max 60 chars) and email body
   - Ensures professional, genuine, non-salesy tone
   - Validates output format

6. **Output**
   - Displays results in console
   - Saves complete output to `result.json`
   - Includes all extracted data and generated email

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- LinkedIn account credentials
- Azure OpenAI API key OR OpenAI API key

### Step 1: Clone/Download the Project

```bash
# Navigate to project directory
cd F:\Yogi
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Playwright Browsers

```bash
playwright install chromium
```

---

## ⚙️ Configuration

### Step 1: Create .env File

Copy the example environment file:

```bash
copy .env.example .env
```

### Step 2: Configure Environment Variables

Edit `.env` file with your credentials:

```env
# =============================================================================
# AI PROVIDER CONFIGURATION
# =============================================================================

PROVIDER=azure

# =============================================================================
# AZURE OPENAI CONFIGURATION
# =============================================================================

AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_API_VERSION=2025-01-01-preview

# =============================================================================
# LINKEDIN LOGIN CONFIGURATION
# =============================================================================

LOGIN_METHOD=credentials
LINKEDIN_EMAIL=your_linkedin_email@example.com
LINKEDIN_PASSWORD=your_linkedin_password
```

### Configuration Options

#### AI Provider Options

| Option | Description |
|--------|-------------|
| `PROVIDER=azure` | Use Azure OpenAI (requires Azure credentials) |
| `PROVIDER=openai` | Use regular OpenAI (requires OpenAI API key) |
| `PROVIDER=auto` | Auto-detect based on available credentials |

#### Login Method Options

| Option | Description |
|--------|-------------|
| `LOGIN_METHOD=credentials` | Use LinkedIn email/password (automated login) |
| `LOGIN_METHOD=chrome_profile` | Use existing Chrome profile (stays logged in) |
| `LOGIN_METHOD=none` | No login (may fail for private profiles) |

---

## 🚀 Running the Application

### Quick Start

```bash
python run.py https://www.linkedin.com/in/yogendra-mishra-/
```

### Command Options

#### 1. Run with Specific Profile

```bash
python run.py https://www.linkedin.com/in/username/
```

#### 2. Run with Default Profile

```bash
python run.py
```

Uses the default test profile (yogendra-mishra)

#### 3. Run Using Batch File (Windows)

```bash
run.bat https://www.linkedin.com/in/username/
```

#### 4. Test Multiple Profiles

```bash
python test_both_profiles.py
```

Tests with both yogendra-mishra and sanheensethi profiles

#### 5. Debug Mode

```bash
python debug_linkedin.py
```

Runs in non-headless mode with detailed HTML output

---

## 📊 Expected Output

### Console Output

```
[OK] Using Azure OpenAI: https://adars-mbho2thk-eastus2.openai.azure.com
================================================================================
RESULTS
================================================================================

Name:    Yogendra Mishra
Title:   Software Developer | Full Stack & Backend Engineer | FastAPI , Python Backend , MERN Stack | Building Secure & Scalable Applications
Company: Homenetics Technology PVT. LTD.

About (1044 characters):
--------------------------------------------------------------------------------
I am a Software Developer with hands-on experience in building secure, scalable,
and user-focused applications. My expertise lies in Python (FastAPI), React.js,
TypeScript, and MongoDB, and I enjoy solving complex technical challenges that
improve system performance and user experience. At Homenetics Technology Pvt Ltd,
I built real-time monitoring tools like the Eagle Eye Dashboard, developed RESTful
APIs, integrated Google APIs, and secured infrastructure with WireGuard VPN...
--------------------------------------------------------------------------------

Email Subject: Connecting with a Skilled Full Stack Developer

Email Body:
--------------------------------------------------------------------------------
Hi Yogendra,

I came across your profile and was thoroughly impressed by your expertise in
building secure and scalable applications, particularly your work with Python
(FastAPI), React.js, and MongoDB. Your contributions at Homenetics Technology,
like the Eagle Eye Dashboard and securing infrastructure with WireGuard VPN,
highlight your ability to deliver impactful solutions.

I'd love to connect and explore opportunities to collaborate or exchange ideas
around building reliable and innovative systems. Let me know if you'd be open
to a quick chat.

Looking forward to connecting!

Best regards,
[Your Name]
--------------------------------------------------------------------------------

Saved to: result.json
================================================================================
```

### Log Output

```
INFO:src.linkedin_scraper_v2:Fetching LinkedIn profile: https://www.linkedin.com/in/yogendra-mishra-/
INFO:src.linkedin_scraper_v2:Login method: credentials
INFO:src.linkedin_scraper_v2:Logging in to LinkedIn...
INFO:src.linkedin_scraper_v2:Entering credentials...
INFO:src.linkedin_scraper_v2:Clicked sign in button, waiting for login...
INFO:src.linkedin_scraper_v2:[OK] Successfully logged in to LinkedIn
INFO:src.linkedin_scraper_v2:Navigating to profile: https://www.linkedin.com/in/yogendra-mishra-/
INFO:src.linkedin_scraper_v2:Looking for 'see more' buttons to expand sections...
INFO:src.linkedin_scraper_v2:Clicking 'see more' button...
INFO:src.linkedin_scraper_v2:[OK] Clicked 1 'see more' button(s)
INFO:src.linkedin_scraper_v2:Cleaning HTML content...
INFO:src.linkedin_scraper_v2:Extracted text content (397437 characters)
INFO:src.linkedin_scraper_v2:Saved extracted text to: extracted_text.txt
INFO:src.linkedin_scraper_v2:Extracting profile information using LLM...
INFO:src.linkedin_scraper_v2:✓ Successfully extracted profile data for: Yogendra Mishra
INFO:src.email_generator:Generating email for Yogendra Mishra... (attempt 1)
INFO:src.email_generator:✓ Email generated successfully
```

### Generated Files

| File | Description |
|------|-------------|
| `result.json` | Complete output with profile data and email |
| `extracted_text.txt` | Cleaned text sent to LLM (400K chars) |

### result.json Format

```json
{
  "name": "Yogendra Mishra",
  "title": "Software Developer | Full Stack & Backend Engineer",
  "company": "Homenetics Technology PVT. LTD.",
  "about": "I am a Software Developer with hands-on experience...",
  "email": {
    "subject": "Connecting with a Skilled Full Stack Developer",
    "body": "Hi Yogendra,\n\nI came across your profile..."
  }
}
```

---

## 📁 Project Structure

```
F:\Yogi\
│
├── src/                           # Source code
│   ├── __init__.py               # Package initialization
│   ├── config.py                 # Configuration and environment setup
│   ├── linkedin_scraper_v2.py    # LinkedIn scraper with LLM extraction
│   ├── email_generator.py        # Personalized email generation
│   ├── main.py                   # Main orchestration module
│   └── utils.py                  # Utility functions
│
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md           # System architecture documentation
│   └── README.md                 # This file
│
├── run.py                         # Simple runner script
├── run.bat                        # Windows batch file runner
├── test_both_profiles.py         # Test script for multiple profiles
├── debug_linkedin.py             # Debug script with HTML output
│
├── .env                           # Environment variables (not in repo)
├── .env.example                  # Example environment file
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
│
└── result.json                   # Output file (generated)
```

---

## 🚀 Future Enhancements

### Planned Features

#### 1. **Batch Processing**
- Process multiple LinkedIn URLs from a CSV file
- Export results to Excel/CSV format
- Progress tracking with status dashboard

#### 2. **Enhanced Data Extraction**
- Extract work experience history
- Extract education details
- Extract skills and endorsements
- Extract recommendations

#### 3. **Email Customization**
- Multiple email templates (networking, job inquiry, collaboration)
- Tone customization (formal, casual, friendly)
- Length preferences (short, medium, long)
- Custom call-to-action options

#### 4. **CRM Integration**
- Export to Salesforce, HubSpot, or other CRMs
- Automated follow-up scheduling
- Contact tracking and management

#### 5. **Advanced Features**
- LinkedIn connection request automation
- Profile similarity matching
- Company research integration
- Email A/B testing suggestions

#### 6. **Performance Improvements**
- Parallel processing for batch operations
- Caching mechanism for LinkedIn sessions
- Rate limiting and throttling controls
- Resume capability for interrupted scraping

#### 7. **User Interface**
- Web-based dashboard (Flask/FastAPI)
- Chrome extension for one-click scraping
- Mobile app support

#### 8. **Analytics & Reporting**
- Success rate tracking
- Response rate analytics
- Email effectiveness scoring
- Export to visualization tools

#### 9. **Security Enhancements**
- Encrypted credential storage
- OAuth integration for LinkedIn
- IP rotation and proxy support
- CAPTCHA handling

#### 10. **Multi-Platform Support**
- Twitter/X profile scraping
- GitHub profile integration
- Company website data extraction
- Multiple social media aggregation

---

## 🔍 Troubleshooting

### Common Issues

#### 1. `ModuleNotFoundError: No module named 'bs4'`

**Solution:**
```bash
pip install -r requirements.txt
```

#### 2. `Configuration Error: AZURE_OPENAI_API_KEY not found`

**Solution:**
- Check your `.env` file exists
- Ensure all required fields are filled
- Verify no extra spaces in variable names

#### 3. `Login may have failed - unexpected URL`

**Solution:**
- Verify LinkedIn credentials in `.env`
- Try using `LOGIN_METHOD=chrome_profile` instead
- Check if LinkedIn requires verification

#### 4. `Timeout while loading profile`

**Solution:**
- Increase `PAGE_LOAD_TIMEOUT` in `src/config.py`
- Check your internet connection
- Ensure LinkedIn is accessible

#### 5. Profile extraction returns null values

**Solution:**
- Ensure LinkedIn profile is public or you're logged in
- Check logs for "see more" button clicks
- Verify profile URL is correct

#### 6. `Error code: 429 - Rate limit exceeded`

**Solution:**
- Wait before making more requests
- Check your OpenAI/Azure quota
- Consider upgrading your API plan

### Debug Mode

For detailed debugging, set in `src/config.py`:

```python
HEADLESS_MODE = False
```

This will show the browser window during scraping.

---

## 📝 License

This project is for educational and personal use only. Please respect LinkedIn's Terms of Service and use responsibly.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

## 📧 Support

For questions or issues, please check the documentation or create an issue in the repository.

---

**Built with ❤️ using Python, Playwright, and OpenAI**
