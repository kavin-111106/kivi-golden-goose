import re
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Memory
from .schemas import (ObservationCreate, 
ObservationResponse, 
TransformRequest,
TransformResponse,
MemoryUpdate)

from .utils import normalize_word, similarity


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Kivi Golden Goose",
    description="Personal word memory backend for Kivi",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Kivi Golden Goose backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post(
    "/api/observe",
    response_model=ObservationResponse
)
def observe(
    observation: ObservationCreate,
    db: Session = Depends(get_db)
):
    observed = normalize_word(observation.observed)
    intended = normalize_word(observation.intended)

    memories = db.query(Memory).all()

    memory = None

    for existing_memory in memories:
        variants = existing_memory.variants.split(",")

        observed_match = any(
            similarity(variant, observed) >= 0.85
            for variant in variants
        )

        intended_match = (
    existing_memory.canonical == intended
)

        if observed_match and intended_match:
            memory = existing_memory
            break

    if memory:
        memory.evidence_count += 1

        if observed not in memory.variants.split(","):
            memory.variants += f",{observed}"

        memory.confidence = min(
            0.5 + (memory.evidence_count - 1) * 0.2,
            1.0
        )

        if memory.evidence_count >= 3:
            memory.status = "confirmed"

        db.commit()
        db.refresh(memory)

        message = "Existing memory updated"

    else:
        memory = Memory(
            canonical=intended,
            variants=observed,
            memory_type="phonetic",
            status="candidate",
            confidence=0.5,
            evidence_count=1
        )

        db.add(memory)
        db.commit()
        db.refresh(memory)

        message = "New memory created"

    return {
        "observed": observation.observed,
        "intended": observation.intended,
        "message": message
    }

@app.post(
    "/api/transform",
    response_model=TransformResponse
)
def transform(
    request: TransformRequest,
    db: Session = Depends(get_db)
):
    words = request.text.split()

    memories = db.query(Memory).filter(
        Memory.status == "confirmed"
    ).all()

    transformed_words = []

    for word in words:
        match = re.match(r"^([^\w]*)([\w]+)([^\w]*)$", word)

        if not match:
            transformed_words.append(word)
            continue

        prefix, core_word, suffix = match.groups()

        transformed_word = core_word

        for memory in memories:
            variants = memory.variants.split(",")

            for variant in variants:
                if similarity(variant, core_word) >= 0.85:
                    transformed_word = memory.canonical
                    break

            if transformed_word != core_word:
                break

        transformed_words.append(
            prefix + transformed_word + suffix
        )

    transformed_text = " ".join(transformed_words)

    return {
        "original": request.text,
        "transformed": transformed_text
    }
@app.get("/api/memories")
def get_memories(
    db: Session = Depends(get_db)
):
    memories = db.query(Memory).all()

    return memories

@app.patch("/api/memories/{memory_id}")
def update_memory(
    memory_id: int,
    update: MemoryUpdate,
    db: Session = Depends(get_db)
):
    memory = db.query(Memory).filter(
        Memory.id == memory_id
    ).first()

    if not memory:
        raise HTTPException(
            status_code=404,
            detail="Memory not found"
        )

    if update.canonical is not None:
        memory.canonical = normalize_word(update.canonical)

    if update.variants is not None:
        variants = [
            normalize_word(variant)
            for variant in update.variants.split(",")
            if variant.strip()
        ]

        memory.variants = ",".join(variants)

    if update.status is not None:
        memory.status = update.status

    if update.confidence is not None:
        memory.confidence = update.confidence

    db.commit()
    db.refresh(memory)

    return memory

@app.delete("/api/reset")
def reset_memories(
    db: Session = Depends(get_db)
):
    db.query(Memory).delete()
    db.commit()

    return {
        "message": "All memories have been reset"
    }
@app.delete("/api/memories/{memory_id}")
def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db)
):
    memory = db.query(Memory).filter(
        Memory.id == memory_id
    ).first()

    if not memory:
        raise HTTPException(
            status_code=404,
            detail="Memory not found"
        )

    db.delete(memory)
    db.commit()

    return {
        "message": "Memory deleted successfully"
    }