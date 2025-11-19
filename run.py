
import sys
import json

sys.path.insert(0, '.')

from src.linkedin_scraper import scrape_linkedin_profile
from src.email_generator import generate_personalized_email


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://www.linkedin.com/in/yogendra-mishra-/"

   
    profile_data = scrape_linkedin_profile(url)

    
    email_data = generate_personalized_email(profile_data)

 
    result = {
        'name': profile_data.get('name'),
        'title': profile_data.get('title'),
        'company': profile_data.get('company'),
        'about': profile_data.get('about'),
        'email': email_data
    }

   
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"\nName:    {result['name']}")
    print(f"Title:   {result['title']}")
    print(f"Company: {result['company']}")

    if result['about']:
        print(f"\nAbout ({len(result['about'])} characters):")
        print("-"*80)
        print(result['about'])
        print("-"*80)

    print(f"\nEmail Subject: {email_data['subject']}")
    print(f"\nEmail Body:")
    print("-"*80)
    print(email_data['body'])
    print("-"*80)

    
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: result.json")
    print("="*80)


if __name__ == "__main__":
    main()
