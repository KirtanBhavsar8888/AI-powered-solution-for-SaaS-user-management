"""
AI Agent for understanding UI elements and extracting structured data
Uses OpenAI GPT-4 for intelligent HTML analysis and data extraction
"""
import json
import os
import re
from typing import Dict, List, Any, Optional
from openai import OpenAI
from config import OPENAI_CONFIG
import logging

class AIAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key="")
        self.logger = logging.getLogger(__name__)

    def extract_users_from_html(self, html_content: str, saas_name: str) -> List[Dict[str, Any]]:
        """
        Extract user data from HTML using AI
        """
        try:
            # Create a function schema for structured output
            function_schema = {
                "name": "extract_user_data",
                "description": "Extract user information from SaaS admin portal HTML",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "users": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "User's full name"},
                                    "email": {"type": "string", "description": "User's email address"},
                                    "role": {"type": "string", "description": "User's role or permission level"},
                                    "last_login": {"type": "string", "description": "Last login date/time"},
                                    "status": {"type": "string", "description": "Account status (active/inactive/pending)"}
                                },
                                "required": ["email"]
                            }
                        }
                    },
                    "required": ["users"]
                }
            }

            # Prepare the prompt
            prompt = f"""
            Analyze the following HTML content from a {saas_name} admin portal and extract user information.
            Look for tables, lists, or other structures containing user data.

            HTML Content (truncated if too long):
            {html_content[:15000]}  # Limit to avoid token limits

            Extract all users you can find with their details. If some information is not available, 
            set it to null or "Unknown". Focus on finding:
            - User names
            - Email addresses  
            - Roles/permissions
            - Last login dates
            - Account status
            """

            response = self.client.chat.completions.create(
                model=OPENAI_CONFIG["model"],
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing HTML and extracting structured user data from SaaS admin portals."},
                    {"role": "user", "content": prompt}
                ],
                functions=[function_schema],
                function_call={"name": "extract_user_data"},
                temperature=OPENAI_CONFIG["temperature"],
                max_tokens=OPENAI_CONFIG["max_tokens"]
            )

            # Parse the function call result
            function_call = response.choices[0].message.function_call
            if function_call and function_call.name == "extract_user_data":
                result = json.loads(function_call.arguments)
                users = result.get("users", [])
                self.logger.info(f"Extracted {len(users)} users from {saas_name}")
                return users
            else:
                self.logger.error("AI failed to extract user data")
                return []

        except Exception as e:
            self.logger.error(f"Error in AI user extraction: {str(e)}")
            return []

    def find_ui_elements(self, html_content: str, task_description: str) -> Dict[str, str]:
        """
        Use AI to find UI elements for specific tasks (like finding add user button)
        """
        try:
            function_schema = {
                "name": "find_ui_elements",
                "description": "Find UI elements for specified task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "elements": {
                            "type": "object",
                            "properties": {
                                "primary_selector": {"type": "string", "description": "Main CSS selector for the element"},
                                "alternative_selectors": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Alternative selectors if primary fails"
                                },
                                "element_type": {"type": "string", "description": "Type of element (button, link, input, etc.)"},
                                "confidence": {"type": "number", "description": "Confidence level 0-1"}
                            }
                        }
                    }
                }
            }

            prompt = f"""
            Analyze this HTML and find the UI element for: {task_description}

            HTML Content:
            {html_content[:10000]}

            Provide the best CSS selector to interact with this element.
            """

            response = self.client.chat.completions.create(
                model=OPENAI_CONFIG["model"],
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing HTML and finding UI elements with CSS selectors."},
                    {"role": "user", "content": prompt}
                ],
                functions=[function_schema],
                function_call={"name": "find_ui_elements"},
                temperature=0.1
            )

            function_call = response.choices[0].message.function_call
            if function_call:
                result = json.loads(function_call.arguments)
                return result.get("elements", {})

            return {}

        except Exception as e:
            self.logger.error(f"Error finding UI elements: {str(e)}")
            return {}

    def generate_user_form_data(self, user_details: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate form data for user provisioning
        """
        try:
            # Simple form data generation based on common patterns
            form_data = {}

            if "email" in user_details:
                form_data["email"] = user_details["email"]
            if "name" in user_details:
                form_data["name"] = user_details["name"]
                # Also try common variations
                form_data["firstName"] = user_details["name"].split()[0] if " " in user_details["name"] else user_details["name"]
                if " " in user_details["name"]:
                    form_data["lastName"] = " ".join(user_details["name"].split()[1:])
            if "role" in user_details:
                form_data["role"] = user_details["role"]

            return form_data

        except Exception as e:
            self.logger.error(f"Error generating form data: {str(e)}")
            return {}

    def analyze_ui_changes(self, old_html: str, new_html: str) -> Dict[str, Any]:
        """
        Analyze changes in UI to adapt selectors
        """
        try:
            prompt = f"""
            Compare these two HTML snippets and identify significant changes in UI structure:

            OLD HTML:
            {old_html[:5000]}

            NEW HTML:
            {new_html[:5000]}

            Identify:
            1. Structural changes
            2. New elements
            3. Removed elements
            4. Changed selectors/IDs/classes
            """

            response = self.client.chat.completions.create(
                model=OPENAI_CONFIG["model"],
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing HTML changes and UI modifications."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )

            changes_analysis = response.choices[0].message.content

            return {
                "has_changes": "changes detected" in changes_analysis.lower(),
                "analysis": changes_analysis,
                "confidence": 0.8  # Basic confidence scoring
            }

        except Exception as e:
            self.logger.error(f"Error analyzing UI changes: {str(e)}")
            return {"has_changes": False, "analysis": "", "confidence": 0.0}

    def validate_action_success(self, before_html: str, after_html: str, action_type: str) -> bool:
        """
        Validate if an action (like adding/removing user) was successful
        """
        try:
            prompt = f"""
            Determine if the following action was successful by comparing before and after HTML:

            Action Type: {action_type}

            BEFORE:
            {before_html[:5000]}

            AFTER:
            {after_html[:5000]}

            Was the action successful? Respond with only "SUCCESS" or "FAILED".
            """

            response = self.client.chat.completions.create(
                model=OPENAI_CONFIG["model"],
                messages=[
                    {"role": "system", "content": "You are an expert at validating UI changes and action results."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )

            result = response.choices[0].message.content.strip().upper()
            return "SUCCESS" in result

        except Exception as e:
            self.logger.error(f"Error validating action: {str(e)}")
            return False
