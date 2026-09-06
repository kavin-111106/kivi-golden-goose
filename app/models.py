from datetime import datetime, UTC

from sqlalchemy import Column, DateTime, Float, Integer, String

from .db import Base


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True)

    canonical = Column(
        String,
        nullable=False
    )

    variants = Column(
        String,
        nullable=False
    )

    memory_type = Column(
        String,
        default="phonetic"
    )

    status = Column(
        String,
        default="candidate"
    )

    confidence = Column(
        Float,
        default=0.0
    )

    evidence_count = Column(
        Integer,
        default=1
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC))

    updated_at = Column(
    DateTime,
    default=lambda: datetime.now(UTC),
    onupdate=lambda: datetime.now(UTC))