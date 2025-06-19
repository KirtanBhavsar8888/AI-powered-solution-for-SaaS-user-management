"""
Configuration file for AI-driven SaaS User Management System
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class SaaSConfig:
    """Configuration for specific SaaS applications"""
    name: str
    login_url: str
    username_selector: str
    password_selector: str
    login_button_selector: str
    users_page_url: str
    user_table_selector: str
    add_user_button: str
    user_form_selectors: Dict[str, str]

# Predefined SaaS configurations
SAAS_CONFIGS = {
    "dropbox": SaaSConfig(
        name="Dropbox Business",
        login_url="https://www.dropbox.com/login",
        username_selector="input[name='login_email']",
        password_selector="input[name='login_password']",
        login_button_selector="button[type='submit']",
        users_page_url="https://www.dropbox.com/manage/admin/members",
        user_table_selector="table.member-list",
        add_user_button="button[data-testid='add-member']",
        user_form_selectors={
            "email": "input[name='memberEmail']",
            "name": "input[name='memberName']",
            "role": "select[name='memberRole']"
        }
    ),
    "notion": SaaSConfig(
        name="Notion Workspace",
        login_url="https://www.notion.so/login",
        username_selector="input[type='email']",
        password_selector="input[type='password']",
        login_button_selector="div[role='button']:has-text('Continue with password')",
        users_page_url="https://www.notion.so/my-integrations",
        user_table_selector="div[data-testid='members-table']",
        add_user_button="button:has-text('Invite')",
        user_form_selectors={
            "email": "input[placeholder='Enter email address']",
            "role": "select[data-testid='permission-select']"
        }
    )
}

# General settings
SETTINGS = {
    "browser_headless": True,
    "page_timeout": 30000,
    "max_retries": 3,
    "screenshot_on_error": True,
    "data_output_dir": "./scraped_data/",
    "logs_dir": "./logs/"
}

# OpenAI Configuration
OPENAI_CONFIG = {
    "model": "gpt-4",
    "temperature": 0.1,
    "max_tokens": 2000
}
