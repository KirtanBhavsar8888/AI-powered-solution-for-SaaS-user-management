"""
Setup script for AI-Driven SaaS User Management System
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def install_playwright_browsers():
    """Install Playwright browsers"""
    print("🌐 Installing Playwright browsers...")
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install"])
        print("✅ Playwright browsers installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Playwright browsers: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ["logs", "scraped_data", "demo_output"]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🚀 Setting up AI-Driven SaaS User Management System")
    print("=" * 50)

    # Install requirements
    if not install_requirements():
        print("❌ Setup failed at requirements installation")
        return

    # Install Playwright browsers
    if not install_playwright_browsers():
        print("❌ Setup failed at Playwright installation")
        return

    # Create directories
    create_directories()

    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n💡 Next Steps:")
    print("1. Set your OpenAI API key:")
    print("   export OPENAI_API_KEY=your_api_key_here")
    print("2. Run the demo: python demo.py")
    print("3. Or run the main application: python main.py --help")

if __name__ == "__main__":
    main()