import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.utils.db import SessionLocal
from app.models.evaluation_result_orm import EvaluationResultORM, EvaluationCandidateORM
from app.models.evaluation_result import (
    EvaluationResult,
    EvaluationResultCreate,
    EvaluationResultSummary,
    EvaluationResultList,
    EvaluationCandidate
)


def _serialize_evaluation_candidate(orm: EvaluationCandidateORM) -> EvaluationCandidate:
    """Convert ORM evaluation candidate to Pydantic model."""
    return EvaluationCandidate(
        id=orm.id,
        evaluation_id=orm.evaluation_id,
        candidate_id=orm.candidate_id,
        candidate_score=orm.candidate_score,
        rank=orm.rank,
        created_at=orm.created_at,
    )


def _serialize_evaluation_result(orm: EvaluationResultORM, include_candidates: bool = True) -> EvaluationResult:
    """Convert ORM evaluation result to Pydantic model."""
    return EvaluationResult(
        id=orm.id,
        rubric_id=orm.rubric_id,
        overall_score=orm.overall_score,
        rubric_name=orm.rubric_name,
        total_candidates=orm.total_candidates,
        is_batch=orm.is_batch == "true",
        individual_results=orm.individual_results or [],
        comparison_summary=orm.comparison_summary,
        evaluation_metadata=orm.evaluation_metadata,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        candidates=[] if not include_candidates else [],  # Will be populated separately if needed
    )


def _serialize_evaluation_summary(orm: EvaluationResultORM) -> EvaluationResultSummary:
    """Convert ORM evaluation result to summary model."""
    return EvaluationResultSummary(
        id=orm.id,
        rubric_id=orm.rubric_id,
        rubric_name=orm.rubric_name,
        overall_score=orm.overall_score,
        total_candidates=orm.total_candidates,
        is_batch=orm.is_batch == "true",
        created_at=orm.created_at,
    )


def create_evaluation_result(data: EvaluationResultCreate) -> EvaluationResult:
    """Create a new evaluation result."""
    db = SessionLocal()
    try:
        new_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # Create main evaluation result
        orm = EvaluationResultORM(
            id=new_id,
            rubric_id=data.rubric_id,
            overall_score=data.overall_score,
            rubric_name=data.rubric_name,
            total_candidates=data.total_candidates,
            is_batch="true" if data.is_batch else "false",
            individual_results=data.individual_results,
            comparison_summary=data.comparison_summary,
            evaluation_metadata=data.evaluation_metadata,
            created_at=now,
            updated_at=now,
        )
        db.add(orm)
        db.flush()  # Get the ID

        # Create candidate associations
        for i, candidate_id in enumerate(data.candidate_ids):
            # Extract score from individual results if available
            candidate_score = data.overall_score  # Default fallback
            rank = None

            # Try to find specific candidate data in individual_results
            for result in data.individual_results:
                if isinstance(result, dict) and result.get("candidate_id") == candidate_id:
                    candidate_score = result.get("overall_score", data.overall_score)
                    break

            # For batch evaluations, try to get rank from comparison_summary
            if data.is_batch and data.comparison_summary:
                rankings = data.comparison_summary.get("rankings", [])
                for ranking in rankings:
                    if isinstance(ranking, dict) and ranking.get("candidate_id") == candidate_id:
                        rank = ranking.get("rank")
                        candidate_score = ranking.get("overall_score", candidate_score)
                        break

            candidate_assoc = EvaluationCandidateORM(
                id=str(uuid.uuid4()),
                evaluation_id=new_id,
                candidate_id=candidate_id,
                candidate_score=candidate_score,
                rank=rank,
                created_at=now,
            )
            db.add(candidate_assoc)

        db.commit()

        # Return the created evaluation result
        result = _serialize_evaluation_result(orm)
        db.close()
        return result

    except Exception as e:
        db.rollback()
        db.close()
        raise e


def get_evaluation_result(evaluation_id: str) -> Optional[EvaluationResult]:
    """Get evaluation result by ID."""
    db = SessionLocal()
    orm = db.query(EvaluationResultORM).filter(EvaluationResultORM.id == evaluation_id).first()
    if not orm:
        db.close()
        return None

    result = _serialize_evaluation_result(orm)

    # Load candidate associations
    candidates_orm = db.query(EvaluationCandidateORM).filter(
        EvaluationCandidateORM.evaluation_id == evaluation_id
    ).order_by(EvaluationCandidateORM.rank.asc().nullslast()).all()

    result.candidates = [_serialize_evaluation_candidate(c) for c in candidates_orm]

    db.close()
    return result


def list_evaluation_results(limit: int = 50, offset: int = 0) -> EvaluationResultList:
    """List evaluation results with pagination."""
    db = SessionLocal()

    total = db.query(EvaluationResultORM).count()
    results_orm = db.query(EvaluationResultORM).order_by(
        EvaluationResultORM.created_at.desc()
    ).offset(offset).limit(limit).all()

    results = [_serialize_evaluation_summary(orm) for orm in results_orm]

    db.close()
    return EvaluationResultList(total=total, results=results)


def get_evaluation_results_by_rubric(rubric_id: str) -> List[EvaluationResultSummary]:
    """Get all evaluation results for a specific rubric."""
    db = SessionLocal()

    results_orm = db.query(EvaluationResultORM).filter(
        EvaluationResultORM.rubric_id == rubric_id
    ).order_by(EvaluationResultORM.created_at.desc()).all()

    results = [_serialize_evaluation_summary(orm) for orm in results_orm]

    db.close()
    return results


def get_evaluation_results_by_candidate(candidate_id: str) -> List[EvaluationResultSummary]:
    """Get all evaluation results that include a specific candidate."""
    db = SessionLocal()

    # Join through the candidate association table
    results_orm = db.query(EvaluationResultORM).join(
        EvaluationCandidateORM,
        EvaluationResultORM.id == EvaluationCandidateORM.evaluation_id
    ).filter(
        EvaluationCandidateORM.candidate_id == candidate_id
    ).order_by(EvaluationResultORM.created_at.desc()).all()

    results = [_serialize_evaluation_summary(orm) for orm in results_orm]

    db.close()
    return results


def delete_evaluation_result(evaluation_id: str) -> bool:
    """Delete an evaluation result and all its associations."""
    db = SessionLocal()
    try:
        orm = db.query(EvaluationResultORM).filter(EvaluationResultORM.id == evaluation_id).first()
        if not orm:
            db.close()
            return False

        db.delete(orm)
        db.commit()
        db.close()
        return True

    except Exception:
        db.rollback()
        db.close()
        return False
