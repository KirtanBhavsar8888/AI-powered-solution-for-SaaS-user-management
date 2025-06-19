"""
Demo/Test Script for AI-Driven SaaS User Management
This script demonstrates basic functionality without requiring actual SaaS credentials
"""
import asyncio
import json
from datetime import datetime

# Import our modules
from browser_automation import BrowserAutomationHandler
from ai_agent import AIAgent
from data_processor import DataProcessor, UserRecord

async def demo_browser_automation():
    """Demo browser automation without login"""
    print("🔧 Testing Browser Automation...")

    browser = BrowserAutomationHandler()

    # Initialize browser
    success = await browser.initialize_browser()
    if success:
        print("✅ Browser initialized successfully")

        # Navigate to a public page for testing
        await browser.page.goto("https://httpbin.org/html")
        await browser.page.wait_for_load_state('networkidle')

        # Extract content
        content = await browser.extract_page_content()
        print(f"✅ Extracted {len(content)} characters of HTML content")

        # Take screenshot
        screenshot_path = await browser.take_screenshot("demo_test")
        if screenshot_path:
            print(f"✅ Screenshot saved: {screenshot_path}")

    await browser.cleanup()
    print("✅ Browser cleanup completed")

def demo_ai_agent():
    """Demo AI agent with sample HTML (requires OpenAI key)"""
    print("\n🤖 Testing AI Agent...")

    # Sample HTML that mimics a user table
    sample_html = """
    <div class="admin-portal">
        <h1>User Management</h1>
        <table class="user-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Last Login</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>John Doe</td>
                    <td>john.doe@example.com</td>
                    <td>Admin</td>
                    <td>2024-01-15</td>
                    <td>Active</td>
                </tr>
                <tr>
                    <td>Jane Smith</td>
                    <td>jane.smith@example.com</td>
                    <td>User</td>
                    <td>2024-01-14</td>
                    <td>Active</td>
                </tr>
                <tr>
                    <td>Bob Wilson</td>
                    <td>bob.wilson@example.com</td>
                    <td>User</td>
                    <td>2024-01-10</td>
                    <td>Inactive</td>
                </tr>
            </tbody>
        </table>
        <button class="add-user-btn">Add New User</button>
    </div>
    """

    try:
        # This would require an actual OpenAI API key
        # ai_agent = AIAgent(api_key="your_openai_key_here")
        # users = ai_agent.extract_users_from_html(sample_html, "Demo SaaS")
        # print(f"✅ AI extracted {len(users)} users")

        print("⚠️ AI Agent test skipped (requires OpenAI API key)")
        print("💡 To test AI functionality, set your OpenAI API key and uncomment the code above")

        # Instead, let's simulate what the AI would extract
        simulated_extraction = [
            {
                "name": "John Doe",
                "email": "john.doe@example.com", 
                "role": "Admin",
                "last_login": "2024-01-15",
                "status": "Active"
            },
            {
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "role": "User", 
                "last_login": "2024-01-14",
                "status": "Active"
            },
            {
                "name": "Bob Wilson",
                "email": "bob.wilson@example.com",
                "role": "User",
                "last_login": "2024-01-10", 
                "status": "Inactive"
            }
        ]

        print(f"✅ Simulated AI extraction: {len(simulated_extraction)} users")
        return simulated_extraction

    except Exception as e:
        print(f"❌ AI Agent test failed: {str(e)}")
        return []

def demo_data_processor():
    """Demo data processing functionality"""
    print("\n📊 Testing Data Processor...")

    processor = DataProcessor(output_dir="./demo_output/")

    # Sample user data (as if extracted by AI)
    sample_users_data = [
        {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "role": "Admin", 
            "last_login": "2024-01-15",
            "status": "Active"
        },
        {
            "name": "Jane Smith", 
            "email": "jane.smith@example.com",
            "role": "User",
            "last_login": "2024-01-14",
            "status": "Active"
        },
        {
            "name": "Bob Wilson",
            "email": "bob.wilson@example.com",
            "role": "User",
            "last_login": "2024-01-10",
            "status": "Inactive"
        }
    ]

    # Process the data
    processed_users = processor.process_raw_user_data(sample_users_data, "Demo SaaS")
    print(f"✅ Processed {len(processed_users)} user records")

    # Save to files
    json_path = processor.save_to_json(processed_users, "demo_users.json")
    csv_path = processor.save_to_csv(processed_users, "demo_users.csv")

    if json_path:
        print(f"✅ JSON saved: {json_path}")
    if csv_path:
        print(f"✅ CSV saved: {csv_path}")

    # Generate report
    report = processor.generate_report(processed_users)
    print("\n📈 User Data Report:")
    print(json.dumps(report, indent=2))

    return processed_users

async def run_demo():
    """Run all demo functions"""
    print("🚀 Starting AI-Driven SaaS User Management Demo")
    print("=" * 50)

    # Test browser automation
    await demo_browser_automation()

    # Test AI agent (simulated)
    extracted_data = demo_ai_agent()

    # Test data processor
    processed_data = demo_data_processor()

    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("\n💡 Next Steps:")
    print("1. Set your OpenAI API key")
    print("2. Configure SaaS credentials in the main script")
    print("3. Run: python main.py --action scrape --saas dropbox --username admin@example.com --password adminpassword --openai-key your_key")

if __name__ == "__main__":
    asyncio.run(run_demo())