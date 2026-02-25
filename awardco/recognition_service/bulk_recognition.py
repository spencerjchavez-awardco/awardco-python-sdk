from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class BulkRecognition:
    recognition_date: datetime
    from_user: str  # Employee id or email (required)
    to_user: str  # Employee id or email (required)
    note: str
    is_private: bool
    amount: int = 0
    budget_name: str = ""  # Required if amount > 0
    program_name: str = ""
    tags: list[str] = field(default_factory=list)
    year: int | None = None
    email_template: str = ""
    notify_manager: str = ""
    notify_date: datetime | None = None
    notify_email_template: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "Recognition Date (ISO 8601)": self.recognition_date.replace(microsecond=0).isoformat(),
            "From User (Employee Id/Email)": self.from_user,
            "To User (Employee Id/Email)": self.to_user,
            "Note": self.note,
            "Tags": ";".join(self.tags),
            "Year": str(self.year) if self.year else "",
            "Amount (Currency)": self.amount,
            "Budget Name": self.budget_name,
            "Public/Private": "Private" if self.is_private else "Public",
            "Email Template": self.email_template,
            "Program Name": self.program_name,
            "Notify Manager (Employee Id/Email)": self.notify_manager,
            "Notify Date (ISO 8601)": self.notify_date.replace(microsecond=0).isoformat() if self.notify_date else '',
            "Notify Email Template": self.notify_email_template,
        }