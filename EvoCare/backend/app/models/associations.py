from sqlalchemy import Column, Integer, ForeignKey, Table
from app.core.database import Base

# Association table for Pattern <-> Evidence
pattern_evidence_association = Table(
    "pattern_evidence",
    Base.metadata,
    Column("pattern_id", Integer, ForeignKey("patterns.id", ondelete="CASCADE"), primary_key=True),
    Column("evidence_id", Integer, ForeignKey("evidences.id", ondelete="RESTRICT"), primary_key=True)
)

# Association table for Conflict <-> Evidence
conflict_evidence_association = Table(
    "conflict_evidence",
    Base.metadata,
    Column("conflict_id", Integer, ForeignKey("conflicts.id", ondelete="CASCADE"), primary_key=True),
    Column("evidence_id", Integer, ForeignKey("evidences.id", ondelete="RESTRICT"), primary_key=True)
)

# Association table for Baseline <-> Evidence
baseline_evidence_association = Table(
    "baseline_evidence",
    Base.metadata,
    Column("baseline_id", Integer, ForeignKey("baselines.id", ondelete="CASCADE"), primary_key=True),
    Column("evidence_id", Integer, ForeignKey("evidences.id", ondelete="RESTRICT"), primary_key=True)
)
