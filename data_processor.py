"""
Data Processor for handling extracted user data and managing operations
"""
import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

@dataclass
class UserRecord:
    """Data class for user records"""
    email: str
    name: Optional[str] = None
    role: Optional[str] = None
    last_login: Optional[str] = None
    status: Optional[str] = None
    extracted_at: Optional[str] = None
    source_saas: Optional[str] = None

class DataProcessor:
    def __init__(self, output_dir: str = "./scraped_data/"):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.ensure_output_directory()

    def ensure_output_directory(self):
        """Create output directory if it doesn't exist"""
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info(f"Output directory ensured: {self.output_dir}")

    def process_raw_user_data(self, raw_users: List[Dict[str, Any]], saas_name: str) -> List[UserRecord]:
        """
        Process raw user data from AI extraction into structured records
        """
        processed_users = []
        current_time = datetime.now().isoformat()

        for user_data in raw_users:
            try:
                # Clean and validate email
                email = user_data.get("email", "").strip()
                if not email or "@" not in email:
                    self.logger.warning(f"Invalid email found: {email}")
                    continue

                # Create user record
                user_record = UserRecord(
                    email=email,
                    name=self.clean_text(user_data.get("name")),
                    role=self.clean_text(user_data.get("role")),
                    last_login=self.clean_text(user_data.get("last_login")),
                    status=self.clean_text(user_data.get("status", "Unknown")),
                    extracted_at=current_time,
                    source_saas=saas_name
                )

                processed_users.append(user_record)

            except Exception as e:
                self.logger.error(f"Error processing user data: {user_data}, Error: {str(e)}")
                continue

        self.logger.info(f"Processed {len(processed_users)} valid user records from {saas_name}")
        return processed_users

    def clean_text(self, text: Any) -> Optional[str]:
        """Clean and normalize text data"""
        if text is None or text == "null" or text == "":
            return None

        if isinstance(text, str):
            # Remove extra whitespace and common unwanted characters
            cleaned = text.strip().replace("\n", " ").replace("\t", " ")
            # Remove multiple spaces
            cleaned = " ".join(cleaned.split())
            return cleaned if cleaned else None

        return str(text).strip() if str(text).strip() else None

    def save_to_json(self, users: List[UserRecord], filename: str = None) -> str:
        """Save user data to JSON file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"users_data_{timestamp}.json"

            filepath = os.path.join(self.output_dir, filename)

            # Convert to dictionaries for JSON serialization
            users_dict = [asdict(user) for user in users]

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "total_users": len(users),
                        "extracted_at": datetime.now().isoformat(),
                        "format_version": "1.0"
                    },
                    "users": users_dict
                }, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved {len(users)} users to JSON: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error saving to JSON: {str(e)}")
            return ""

    def save_to_csv(self, users: List[UserRecord], filename: str = None) -> str:
        """Save user data to CSV file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"users_data_{timestamp}.csv"

            filepath = os.path.join(self.output_dir, filename)

            if not users:
                self.logger.warning("No users to save to CSV")
                return ""

            fieldnames = ["email", "name", "role", "last_login", "status", "extracted_at", "source_saas"]

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for user in users:
                    writer.writerow(asdict(user))

            self.logger.info(f"Saved {len(users)} users to CSV: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error saving to CSV: {str(e)}")
            return ""

    def load_existing_data(self, filepath: str) -> List[UserRecord]:
        """Load existing user data from file"""
        try:
            users = []

            if filepath.endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    users_data = data.get('users', [])

                    for user_dict in users_data:
                        users.append(UserRecord(**user_dict))

            elif filepath.endswith('.csv'):
                with open(filepath, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        # Convert None strings back to None
                        for key, value in row.items():
                            if value == '' or value == 'None':
                                row[key] = None
                        users.append(UserRecord(**row))

            self.logger.info(f"Loaded {len(users)} users from {filepath}")
            return users

        except Exception as e:
            self.logger.error(f"Error loading data from {filepath}: {str(e)}")
            return []

    def generate_report(self, users: List[UserRecord]) -> Dict[str, Any]:
        """Generate summary report of user data"""
        try:
            if not users:
                return {"error": "No user data available"}

            # Count by SaaS source
            saas_counts = {}
            role_counts = {}
            status_counts = {}

            for user in users:
                # SaaS source counts
                saas = user.source_saas or "Unknown"
                saas_counts[saas] = saas_counts.get(saas, 0) + 1

                # Role counts
                role = user.role or "Unknown"
                role_counts[role] = role_counts.get(role, 0) + 1

                # Status counts
                status = user.status or "Unknown"
                status_counts[status] = status_counts.get(status, 0) + 1

            report = {
                "summary": {
                    "total_users": len(users),
                    "unique_emails": len(set(user.email for user in users)),
                    "report_generated_at": datetime.now().isoformat()
                },
                "breakdown": {
                    "by_saas": saas_counts,
                    "by_role": role_counts,
                    "by_status": status_counts
                },
                "sample_users": [asdict(user) for user in users[:5]]  # First 5 users as sample
            }

            return report

        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return {"error": f"Report generation failed: {str(e)}"}

    def compare_datasets(self, dataset1: List[UserRecord], dataset2: List[UserRecord]) -> Dict[str, Any]:
        """Compare two datasets and identify differences"""
        try:
            emails1 = set(user.email for user in dataset1)
            emails2 = set(user.email for user in dataset2)

            added_users = emails2 - emails1
            removed_users = emails1 - emails2
            common_users = emails1 & emails2

            comparison = {
                "dataset1_count": len(dataset1),
                "dataset2_count": len(dataset2),
                "added_users": list(added_users),
                "removed_users": list(removed_users),
                "common_users_count": len(common_users),
                "comparison_date": datetime.now().isoformat()
            }

            return comparison

        except Exception as e:
            self.logger.error(f"Error comparing datasets: {str(e)}")
            return {"error": f"Comparison failed: {str(e)}"}
