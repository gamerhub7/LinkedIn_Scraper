# LinkedIn Profile Email Generator

A Python application that scrapes LinkedIn profiles and generates personalized emails using OpenAI's GPT API or Azure open api key .

## Features

- Scrapes LinkedIn profiles to extract:
  - Name
  - Current job title
  - Company
  - About section
- Generates personalized emails using OpenAI GPT-4
- Returns structured JSON output
- Comprehensive error handling
- Headless browser automation with Playwright

## Prerequisites

- Python 3.8 or higher
- OpenAI API key or azure openapi key
- Internet connection

## Installation

### 1. Clone or Download the Project

```bash
cd TASK
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

After installing the dependencies, you need to install the Playwright browsers:

```bash
playwright install chromium
```

### 5. Set Up Environment Variables

Create a `.env` file in the project root directory:

```
# Copy this file and 
 #Choose your provider: 'azure' or 'openai'
PROVIDER=azure

AZURE_OPENAI_API_KEY=your azure key
AZURE_OPENAI_ENDPOINT=https://adars-mbho2thk-eastus2.openai.azure.com
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# OpenAI API Configuration
OPENAI_API_KEY=your api key
# Optional: OpenAI Model Configuration
OPENAI_MODEL=gpt-5
# Alternative: gpt-3.5-turbo for faster/cheaper responses

LOGIN_METHOD=credentials
#Recommended 
LINKEDIN_EMAIL=ypur linkedin email 
LINKEDIN_PASSWORD=your linkedin password

# Optional: Rate Limiting
MAX_RETRIES=3
RETRY_DELAY=2
```

Edit the `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-4
```

To get an OpenAI API key:
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

## Usage

### Command Line Interface

Run the application from the command line:

```bash
python run.py <linkedin_profile_url>
```

**Example:**

```bash
python run.py https://www.linkedin.com/in/johndoe
```

### Output Format

The application returns a JSON object with the following structure:

```json
{
  "name": "John Doe",
  "title": "Software Engineer at Google",
  "company": "Google",
  "about": "Passionate about AI and cloud computing...",
  "email": {
    "subject": "Loved your work on AI systems at Google!",
    "body": "Hi John,\n\nI came across your profile and was impressed by your focus on AI and cloud technologies..."
  }
}
```

### Error Handling

The application handles various error scenarios:

#### Invalid URL

```json
{
  "error": "Invalid LinkedIn URL format",
  "status": "failed",
  "url": "invalid_url"
}
```

#### Profile Not Accessible

```json
{
  "error": "Profile page timeout - LinkedIn may require login or profile is not public",
  "status": "failed"
}
```

#### Missing About Section

```json
{
  "name": "John Doe",
  "title": "Software Engineer at Google",
  "company": "Google",
  "about": null,
  "email": {
    "subject": "...",
    "body": "..."
  },
  "warning": "About section not found, email generated from available data"
}
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `OPENAI_MODEL` (optional): OpenAI model to use (default: `gpt-4`)
  - Options: `gpt-4`, `gpt-3.5-turbo`
- `MAX_RETRIES` (optional): Maximum retry attempts (default: 3)
- `RETRY_DELAY` (optional): Delay between retries in seconds (default: 2)

### Application Settings

You can modify settings in `src/config.py`:

- `HEADLESS_MODE`: Run browser in headless mode (default: `True`)
- `PAGE_LOAD_TIMEOUT`: Timeout for page loading in seconds (default: 30)
- `IMPLICIT_WAIT`: Implicit wait time for elements (default: 10)


### Customizing Email Generation

Edit `src/email_generator.py` to customize the email generation prompt or style.

## Troubleshooting

### Issue: "OPENAI_API_KEY not found"

**Solution:** Make sure you've created a `.env` file and added your OpenAI API key.

### Issue: "Profile page timeout"

**Possible causes:**
- LinkedIn profile requires login to view
- Profile is private or doesn't exist
- Internet connection issues

**Solution:** Make sure the profile is public and accessible without login.

### Issue: Playwright browser not found

**Solution:** Run `playwright install chromium` to install the required browsers.

### Issue: "Unable to extract profile information"

**Possible causes:**
- LinkedIn's HTML structure has changed
- Profile is not fully public
- Anti-bot measures are blocking access

**Solution:** Check if the profile is accessible in a regular browser without login.



### Version 1.0.0
- Initial release
- LinkedIn profile scraping
- OpenAI email generation
- JSON output format
- Comprehensive error handling
