"""
Example usage of LinkedIn Email Generator
Demonstrates how to use the application programmatically
"""

import sys
import os

# Add parent directory to path to import src module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import process_linkedin_profile
from src.utils import format_json_output
import json


def example_basic_usage():
    """Basic usage example"""
    print("=" * 70)
    print("Example 1: Basic Usage")
    print("=" * 70)

    url = "https://www.linkedin.com/in/example-profile"

    print(f"\nProcessing profile: {url}")
    result = process_linkedin_profile(url)

    print("\nResult:")
    print(format_json_output(result))


def example_multiple_profiles():
    """Process multiple profiles"""
    print("\n" + "=" * 70)
    print("Example 2: Processing Multiple Profiles")
    print("=" * 70)

    urls = [
        "https://www.linkedin.com/in/profile1",
        "https://www.linkedin.com/in/profile2",
        "https://www.linkedin.com/in/profile3"
    ]

    results = []

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")

        try:
            result = process_linkedin_profile(url)
            results.append(result)

            if 'error' in result:
                print(f"  ✗ Error: {result['error']}")
            else:
                print(f"  ✓ Success: Generated email for {result.get('name', 'Unknown')}")

        except Exception as e:
            print(f"  ✗ Exception: {str(e)}")
            results.append({'url': url, 'error': str(e)})

    print(f"\n\nProcessed {len(results)} profiles")
    print(f"Successful: {sum(1 for r in results if 'error' not in r)}")
    print(f"Failed: {sum(1 for r in results if 'error' in r)}")


def example_error_handling():
    """Demonstrate error handling"""
    print("\n" + "=" * 70)
    print("Example 3: Error Handling")
    print("=" * 70)

    # Test with invalid URL
    print("\nTest 1: Invalid URL")
    invalid_url = "https://invalid-url.com/profile"
    result = process_linkedin_profile(invalid_url)

    if 'error' in result:
        print(f"Error caught: {result['error']}")
    else:
        print("Unexpected success")


def example_custom_processing():
    """Example with custom processing of results"""
    print("\n" + "=" * 70)
    print("Example 4: Custom Processing")
    print("=" * 70)

    url = "https://www.linkedin.com/in/example-profile"

    result = process_linkedin_profile(url)

    # Custom processing
    if 'error' not in result:
        print(f"\nProfile Summary:")
        print(f"  Name: {result.get('name', 'N/A')}")
        print(f"  Position: {result.get('title', 'N/A')}")
        print(f"  Company: {result.get('company', 'N/A')}")

        if result.get('email'):
            print(f"\nGenerated Email:")
            print(f"  Subject: {result['email'].get('subject', 'N/A')}")
            print(f"  Body Preview: {result['email'].get('body', '')[:100]}...")

        # Save to file
        output_file = f"output_{result.get('name', 'unknown').replace(' ', '_')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nSaved to: {output_file}")


def example_batch_processing_with_file():
    """Batch process profiles from a file"""
    print("\n" + "=" * 70)
    print("Example 5: Batch Processing from File")
    print("=" * 70)

    # Create a sample input file
    urls_file = "linkedin_urls.txt"

    print(f"\nReading URLs from: {urls_file}")

    # Example: Read URLs from file (create this file first)
    try:
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

        print(f"Found {len(urls)} URLs to process\n")

        all_results = []

        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Processing: {url}")
            result = process_linkedin_profile(url)
            all_results.append(result)

        # Save all results to a single JSON file
        output_file = "batch_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        print(f"\nAll results saved to: {output_file}")

    except FileNotFoundError:
        print(f"File {urls_file} not found. Create this file with one LinkedIn URL per line.")


if __name__ == '__main__':
    print("\nLinkedIn Email Generator - Usage Examples\n")

    # Run examples
    # Uncomment the examples you want to run

    # example_basic_usage()
    # example_multiple_profiles()
    # example_error_handling()
    # example_custom_processing()
    # example_batch_processing_with_file()

    print("\n" + "=" * 70)
    print("To run these examples, uncomment the desired function calls above")
    print("=" * 70)
