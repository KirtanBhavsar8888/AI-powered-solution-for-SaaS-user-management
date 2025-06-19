"""
Main Orchestrator for AI-Driven SaaS User Management
This is the main entry point for the application.
"""
import os
import asyncio
import json
import argparse
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import from our modules
from config import SAAS_CONFIGS, SETTINGS
from browser_automation import BrowserAutomationHandler
from ai_agent import AIAgent
from data_processor import DataProcessor, UserRecord

class SaaSAutomationOrchestrator:
    def __init__(self, openai_api_key: str):
        """Initialize the orchestrator with required components"""
        self.browser_handler = BrowserAutomationHandler()
        self.ai_agent = AIAgent(api_key=openai_api_key)
        self.data_processor = DataProcessor(output_dir=SETTINGS["data_output_dir"])

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs(SETTINGS["logs_dir"], exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{SETTINGS['logs_dir']}/orchestrator.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """Initialize components"""
        return await self.browser_handler.initialize_browser()

    async def cleanup(self):
        """Clean up resources"""
        await self.browser_handler.cleanup()

    async def scrape_users(self, saas_id: str, credentials: Dict[str, str]) -> List[UserRecord]:
        """
        Main workflow for scraping users from a SaaS portal
        """
        try:
            # Get SaaS configuration
            if saas_id not in SAAS_CONFIGS:
                self.logger.error(f"Unknown SaaS ID: {saas_id}")
                return []

            saas_config = SAAS_CONFIGS[saas_id]
            self.logger.info(f"Starting user scraping workflow for {saas_config.name}")

            # Login to SaaS portal
            login_success = await self.browser_handler.login_to_saas(
                saas_config, 
                credentials.get("username", ""),
                credentials.get("password", "")
            )

            if not login_success:
                self.logger.error(f"Login failed for {saas_config.name}")
                return []

            # Navigate to users page
            nav_success = await self.browser_handler.navigate_to_users_page(saas_config)
            if not nav_success:
                self.logger.error(f"Failed to navigate to users page for {saas_config.name}")
                return []

            # Extract page content
            html_content = await self.browser_handler.extract_page_content()
            if not html_content:
                self.logger.error("Failed to extract page content")
                return []

            # Take screenshot for debugging
            await self.browser_handler.take_screenshot(f"{saas_id}_users_page")

            # Use AI to extract user data
            raw_users = self.ai_agent.extract_users_from_html(html_content, saas_config.name)
            if not raw_users:
                self.logger.error("AI failed to extract user data")
                return []

            # Process extracted data
            processed_users = self.data_processor.process_raw_user_data(raw_users, saas_config.name)

            # Save data
            self.data_processor.save_to_json(processed_users, f"{saas_id}_users.json")
            self.data_processor.save_to_csv(processed_users, f"{saas_id}_users.csv")

            return processed_users

        except Exception as e:
            self.logger.error(f"Error in scrape_users workflow: {str(e)}")
            return []

    async def provision_user(
        self, saas_id: str, credentials: Dict[str, str], user_details: Dict[str, Any]
    ) -> bool:
        """
        Workflow for provisioning a new user
        """
        try:
            if saas_id not in SAAS_CONFIGS:
                self.logger.error(f"Unknown SaaS ID: {saas_id}")
                return False

            saas_config = SAAS_CONFIGS[saas_id]
            self.logger.info(f"Starting user provisioning for {saas_config.name}")

            # Login to SaaS portal
            login_success = await self.browser_handler.login_to_saas(
                saas_config, 
                credentials.get("username", ""),
                credentials.get("password", "")
            )

            if not login_success:
                self.logger.error(f"Login failed for {saas_config.name}")
                return False

            # Navigate to users page
            nav_success = await self.browser_handler.navigate_to_users_page(saas_config)
            if not nav_success:
                self.logger.error(f"Failed to navigate to users page for {saas_config.name}")
                return False

            # Get page state before action for later comparison
            before_html = await self.browser_handler.extract_page_content()

            # Find and click "Add User" button
            # We first try the predefined selector, but if it fails, we use AI to find it
            add_user_success = await self.browser_handler.click_element(saas_config.add_user_button)

            if not add_user_success:
                self.logger.warning("Failed to find add user button with predefined selector, using AI")
                page_content = await self.browser_handler.extract_page_content()
                ui_elements = self.ai_agent.find_ui_elements(
                    page_content, 
                    f"Find the button to add a new user in the {saas_config.name} admin portal"
                )

                if ui_elements and "primary_selector" in ui_elements:
                    add_user_success = await self.browser_handler.click_element(
                        ui_elements["primary_selector"]
                    )

                if not add_user_success:
                    self.logger.error("Failed to find and click add user button")
                    return False

            # Wait for the form to appear
            await asyncio.sleep(2)  # Simple wait to ensure form is loaded

            # Generate form data
            form_data = {}
            for field, selector in saas_config.user_form_selectors.items():
                if field in user_details:
                    form_data[selector] = user_details[field]

            # Fill the form
            form_fill_success = await self.browser_handler.fill_form(form_data)
            if not form_fill_success:
                self.logger.error("Failed to fill user form")
                return False

            # Submit the form (find and click submit button)
            # Using AI to find submit button
            page_content = await self.browser_handler.extract_page_content()
            submit_ui = self.ai_agent.find_ui_elements(
                page_content, 
                "Find the submit or save button for the user form"
            )

            if submit_ui and "primary_selector" in submit_ui:
                submit_success = await self.browser_handler.click_element(
                    submit_ui["primary_selector"]
                )

                if not submit_success:
                    self.logger.error("Failed to click submit button")
                    return False
            else:
                self.logger.error("Could not find submit button")
                return False

            # Wait for the action to complete
            await asyncio.sleep(3)

            # Get page state after action
            after_html = await self.browser_handler.extract_page_content()

            # Validate if user was added successfully
            success = self.ai_agent.validate_action_success(
                before_html, 
                after_html, 
                f"Adding user {user_details.get('email', 'unknown')}"
            )

            if success:
                self.logger.info(f"Successfully provisioned user: {user_details.get('email')}")
            else:
                self.logger.error(f"Failed to provision user: {user_details.get('email')}")

            return success

        except Exception as e:
            self.logger.error(f"Error in provision_user workflow: {str(e)}")
            return False

    async def deprovision_user(
        self, saas_id: str, credentials: Dict[str, str], user_email: str
    ) -> bool:
        """
        Workflow for deprovisioning/removing a user
        """
        try:
            if saas_id not in SAAS_CONFIGS:
                self.logger.error(f"Unknown SaaS ID: {saas_id}")
                return False

            saas_config = SAAS_CONFIGS[saas_id]
            self.logger.info(f"Starting user deprovisioning for {user_email} in {saas_config.name}")

            # Login to SaaS portal
            login_success = await self.browser_handler.login_to_saas(
                saas_config, 
                credentials.get("username", ""),
                credentials.get("password", "")
            )

            if not login_success:
                self.logger.error(f"Login failed for {saas_config.name}")
                return False

            # Navigate to users page
            nav_success = await self.browser_handler.navigate_to_users_page(saas_config)
            if not nav_success:
                self.logger.error(f"Failed to navigate to users page for {saas_config.name}")
                return False

            # Get page state before action for later comparison
            before_html = await self.browser_handler.extract_page_content()

            # Use AI to find the user row and delete button
            user_row_info = self.ai_agent.find_ui_elements(
                before_html,
                f"Find the row or entry for user with email {user_email}"
            )

            if not user_row_info or "primary_selector" not in user_row_info:
                self.logger.error(f"Could not find user row for {user_email}")
                return False

            # Click on the user row (if needed)
            await self.browser_handler.click_element(user_row_info["primary_selector"])

            # Now find the delete/remove button for this user
            updated_html = await self.browser_handler.extract_page_content()
            delete_button_info = self.ai_agent.find_ui_elements(
                updated_html,
                f"Find the delete, remove, or deactivate button for user {user_email}"
            )

            if not delete_button_info or "primary_selector" not in delete_button_info:
                self.logger.error(f"Could not find delete button for {user_email}")
                return False

            # Click the delete button
            delete_click_success = await self.browser_handler.click_element(
                delete_button_info["primary_selector"]
            )

            if not delete_click_success:
                self.logger.error(f"Failed to click delete button for {user_email}")
                return False

            # Handle confirmation dialog if present
            await asyncio.sleep(1)
            dialog_html = await self.browser_handler.extract_page_content()
            confirm_button_info = self.ai_agent.find_ui_elements(
                dialog_html,
                "Find the confirm, yes, or ok button in the confirmation dialog"
            )

            if confirm_button_info and "primary_selector" in confirm_button_info:
                await self.browser_handler.click_element(confirm_button_info["primary_selector"])

            # Wait for the action to complete
            await asyncio.sleep(3)

            # Get page state after action
            after_html = await self.browser_handler.extract_page_content()

            # Validate if user was removed successfully
            success = self.ai_agent.validate_action_success(
                before_html, 
                after_html, 
                f"Removing user {user_email}"
            )

            if success:
                self.logger.info(f"Successfully deprovisioned user: {user_email}")
            else:
                self.logger.error(f"Failed to deprovision user: {user_email}")

            return success

        except Exception as e:
            self.logger.error(f"Error in deprovision_user workflow: {str(e)}")
            return False

async def main():
    """Main function to run the orchestrator"""
    parser = argparse.ArgumentParser(description="AI-Driven SaaS User Management")
    parser.add_argument("--action", choices=["scrape", "provision", "deprovision"], 
                      required=True, help="Action to perform")
    parser.add_argument("--saas", required=True, help="SaaS ID (e.g., 'dropbox', 'notion')")
    parser.add_argument("--username", required=True, help="Admin username/email")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--user-email", help="User email for provision/deprovision actions")
    parser.add_argument("--user-name", help="User name for provisioning")
    parser.add_argument("--user-role", help="User role for provisioning")
    parser.add_argument("--openai-key", required=True, help="OpenAI API Key")

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = SaaSAutomationOrchestrator(openai_api_key=args.openai_key)

    try:
        # Initialize browser
        init_success = await orchestrator.initialize()
        if not init_success:
            print("Failed to initialize browser. Exiting.")
            return

        credentials = {
            "username": args.username,
            "password": args.password
        }

        if args.action == "scrape":
            # Scrape users
            users = await orchestrator.scrape_users(args.saas, credentials)
            if users:
                print(f"Successfully scraped {len(users)} users")
                # Generate and print report
                report = orchestrator.data_processor.generate_report(users)
                print("User Data Report:")
                print(json.dumps(report, indent=2))
            else:
                print("Failed to scrape users or no users found")

        elif args.action == "provision":
            # Check required args
            if not args.user_email:
                print("Error: --user-email is required for provisioning")
                return

            # Prepare user details
            user_details = {
                "email": args.user_email,
                "name": args.user_name,
                "role": args.user_role
            }

            # Provision user
            success = await orchestrator.provision_user(args.saas, credentials, user_details)
            if success:
                print(f"Successfully provisioned user: {args.user_email}")
            else:
                print(f"Failed to provision user: {args.user_email}")

        elif args.action == "deprovision":
            # Check required args
            if not args.user_email:
                print("Error: --user-email is required for deprovisioning")
                return

            # Deprovision user
            success = await orchestrator.deprovision_user(args.saas, credentials, args.user_email)
            if success:
                print(f"Successfully deprovisioned user: {args.user_email}")
            else:
                print(f"Failed to deprovision user: {args.user_email}")

    finally:
        # Clean up
        await orchestrator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
