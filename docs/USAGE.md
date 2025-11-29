# LinkedIn Email Generator - Usage Guide

## Quick Start

### Method 1: Using the Batch File (Windows - Easiest)

Simply double-click `run.bat` or run it from command line:

```cmd
run.bat https://www.linkedin.com/in/username/
```

### Method 2: Using Python Script

```cmd
python run.py https://www.linkedin.com/in/username/
```

### Method 3: Using the Main Module Directly

```cmd
python -m src.main
```

Then enter the LinkedIn profile URL when prompted.

---

## Examples

### Example 1: Process a LinkedIn Profile
```cmd
python run.py https://www.linkedin.com/in/yogendra-mishra-/
```

### Example 2: Process Any LinkedIn Profile
```cmd
python run.py https://www.linkedin.com/in/your-target-profile/
```

---

## Output

The application will:

1. **Display results on screen:**
   - Name, Title, Company
   - Full About section (expanded with "see more" button)
   - Generated personalized email (subject + body)

2. **Save to `result.json`:**
   - Complete JSON output with all extracted data

3. **Save debug files:**
   - `extracted_text.txt` - The text sent to LLM (400K chars)
   - `raw_html.html` - Original HTML from LinkedIn (if using debug script)

---

## Configuration

Before running, make sure your `.env` file is configured:

```env
# Choose your AI provider
PROVIDER=azure

# Azure OpenAI credentials
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_DEPLOYMENT_NAME=gpt-4o

# LinkedIn login credentials
LOGIN_METHOD=credentials
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

---

## Step-by-Step for First Time Users

1. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Set up `.env` file:**
   - Copy `.env.example` to `.env`
   - Fill in your Azure OpenAI credentials
   - Fill in your LinkedIn credentials

3. **Run the application:**
   ```cmd
   run.bat https://www.linkedin.com/in/username/
   ```

4. **Check the output:**
   - Results displayed in terminal
   - Full JSON saved to `result.json`

---

## Sample Output

```
================================================================================
LINKEDIN EMAIL GENERATOR
================================================================================
Processing: https://www.linkedin.com/in/yogendra-mishra-/

================================================================================
RESULTS
================================================================================

Name:    Yogendra Mishra
Title:   Software Developer | Full Stack & Backend Engineer
Company: Homenetics Technology PVT. LTD.

About (1044 characters):
--------------------------------------------------------------------------------
I am a Software Developer with hands-on experience in building secure, scalable,
and user-focused applications. My expertise lies in Python (FastAPI), React.js,
TypeScript, and MongoDB, and I enjoy solving complex technical challenges...
--------------------------------------------------------------------------------

GENERATED EMAIL:
--------------------------------------------------------------------------------
Subject: Excited to Connect and Learn from Your Expertise

Body:
Hi Yogendra,

I came across your profile on LinkedIn and was truly impressed by your extensive
expertise in backend and full-stack development...
--------------------------------------------------------------------------------

[OK] Full result saved to: result.json
================================================================================
```

---

## Troubleshooting

### Issue: "No module named 'bs4'"
**Solution:** Install dependencies
```cmd
pip install -r requirements.txt
```

### Issue: "Configuration Error: AZURE_OPENAI_API_KEY not found"
**Solution:** Check your `.env` file and ensure all required fields are filled

### Issue: "Login may have failed"
**Solution:**
- Check your LinkedIn credentials in `.env`
- Try using `LOGIN_METHOD=chrome_profile` instead

### Issue: Profile extraction returns null values
**Solution:**
- Check if LinkedIn profile is public
- Ensure you're logged in (credentials or Chrome profile)
- The "see more" button clicking should handle truncated sections automatically

---

## Advanced Usage

### Debug Mode (See browser in action)
Edit `src/config.py` and set:
```python
HEADLESS_MODE = False
```

### Test Multiple Profiles
Use the test script:
```cmd
python test_both_profiles.py
```

### Check Raw HTML and Extracted Text
Run the debug script:
```cmd
python debug_linkedin.py
```

This creates:
- `raw_html.html` - Original page HTML
- `extracted_text.txt` - Cleaned text sent to LLM
