"""
Domain Data Models for Lost and Found Management System.
Defines entity representations, validation rules, and serialization.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import json


class ItemType(str, Enum):
    LOST = "LOST"
    FOUND = "FOUND"


class ItemStatus(str, Enum):
    REPORTED = "REPORTED"
    IN_CUSTODY = "IN_CUSTODY"
    CLAIM_PENDING = "CLAIM_PENDING"
    VERIFIED_RETURNED = "VERIFIED_RETURNED"
    DISPOSED = "DISPOSED"


class ClaimStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Category(str, Enum):
    ELECTRONICS = "Electronics"
    DOCUMENTS = "Documents/Cards"
    KEYS_WALLETS = "Keys/Wallets"
    BAGS = "Bags/Backpacks"
    CLOTHING = "Clothing/Apparel"
    OTHERS = "Others"


@dataclass
class ItemRecord:
    item_id: int
    title: str
    category: str
    description: str
    item_type: str  # 'LOST' or 'FOUND'
    location: str
    reporter_name: str
    reporter_contact: str
    status: str = ItemStatus.REPORTED.value
    reward_or_value: float = 0.0
    reported_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def validate(self) -> None:
        """Validate integrity of item attributes."""
        if not self.title or len(self.title.strip()) < 2:
            raise ValueError("Item title must be at least 2 characters long.")
        if not self.location or len(self.location.strip()) == 0:
            raise ValueError("Item location cannot be empty.")
        if not self.reporter_name or len(self.reporter_name.strip()) == 0:
            raise ValueError("Reporter name cannot be empty.")
        if self.reward_or_value < 0:
            raise ValueError("Reward/Value cannot be negative.")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ItemRecord":
        return cls(
            item_id=int(data.get("item_id", 0)),
            title=str(data.get("title", "")),
            category=str(data.get("category", Category.OTHERS.value)),
            description=str(data.get("description", "")),
            item_type=str(data.get("item_type", ItemType.FOUND.value)),
            location=str(data.get("location", "")),
            reporter_name=str(data.get("reporter_name", "")),
            reporter_contact=str(data.get("reporter_contact", "")),
            status=str(data.get("status", ItemStatus.REPORTED.value)),
            reward_or_value=float(data.get("reward_or_value", 0.0)),
            reported_date=str(data.get("reported_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
            updated_at=str(data.get("updated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
        )


@dataclass
class ClaimRecord:
    claim_id: int
    item_id: int
    claimant_name: str
    claimant_contact: str
    proof_description: str
    confidence_score: float = 0.0
    claim_status: str = ClaimStatus.PENDING.value
    submitted_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def validate(self) -> None:
        if not self.claimant_name or len(self.claimant_name.strip()) == 0:
            raise ValueError("Claimant name cannot be empty.")
        if not self.proof_description or len(self.proof_description.strip()) < 3:
            raise ValueError("Proof description must provide meaningful details.")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClaimRecord":
        return cls(
            claim_id=int(data.get("claim_id", 0)),
            item_id=int(data.get("item_id", 0)),
            claimant_name=str(data.get("claimant_name", "")),
            claimant_contact=str(data.get("claimant_contact", "")),
            proof_description=str(data.get("proof_description", "")),
            confidence_score=float(data.get("confidence_score", 0.0)),
            claim_status=str(data.get("claim_status", ClaimStatus.PENDING.value)),
            submitted_at=str(data.get("submitted_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
        )


@dataclass
class AuditAction:
    action_type: str  # 'INSERT', 'UPDATE', 'STATUS_CHANGE', 'DELETE', 'CLAIM_PROCESSED'
    item_id: int
    snapshot_before: Optional[Dict[str, Any]] = None
    snapshot_after: Optional[Dict[str, Any]] = None
    action_id: int = 0
    performed_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditAction":
        sb = data.get("snapshot_before")
        sa = data.get("snapshot_after")
        if isinstance(sb, str):
            sb = json.loads(sb) if sb else None
        if isinstance(sa, str):
            sa = json.loads(sa) if sa else None

        return cls(
            action_type=str(data.get("action_type", "")),
            item_id=int(data.get("item_id", 0)),
            snapshot_before=sb,
            snapshot_after=sa,
            action_id=int(data.get("action_id", 0)),
            performed_at=str(data.get("performed_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
        )
