from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models import Ticket, Project, User
from app.schemas import TicketCreate, TicketRead, TicketUpdate
from app.security import get_current_user

router = APIRouter(tags=["Tickets"])


@router.post(
    "/projects/{project_id}/tickets",
    response_model=TicketRead,
    status_code=201,
    summary="Create a ticket inside a project",
)
def create_ticket(
    project_id: int,
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Check project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Check assignee exists (if provided)
    if ticket_in.assignee_id is not None:
        assignee = db.query(User).filter(User.id == ticket_in.assignee_id).first()
        if assignee is None:
            raise HTTPException(
                status_code=422,
                detail=f"User with id {ticket_in.assignee_id} not found",
            )

    # 3. Create the ticket
    db_ticket = Ticket(
        title=ticket_in.title,
        description=ticket_in.description,
        priority=ticket_in.priority,
        type=ticket_in.type,
        status="TODO",
        project_id=project_id,
        assignee_id=ticket_in.assignee_id,
    )

    # 4. Persist and return
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.get(
    "/projects/{project_id}/tickets",
    response_model=List[TicketRead],
    summary="List all tickets for a project, with optional status filter",
)
def get_tickets(
    project_id: int,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    # 1. Check project exists — 404 if not
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Base query filtered by project
    query = db.query(Ticket).filter(Ticket.project_id == project_id)

    # 3. Optional status filter (case-sensitive: "todo" will NOT match "TODO")
    if status is not None:
        query = query.filter(Ticket.status == status)

    # 4. Return paginated results — empty list [] is valid (not a 404) when no tickets match
    return query.offset(skip).limit(limit).all()


@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketRead,
    summary="Get a single ticket by ID",
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    # 1. Query ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    # 2. 404 if not found
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # 3. Return ticket
    return ticket


@router.patch(
    "/tickets/{ticket_id}",
    response_model=TicketRead,
    summary="Partially update a ticket — only provided fields are changed",
)
def update_ticket(
    ticket_id: int,
    ticket_in: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Fetch ticket — 404 if not found
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # 2. Check assignee exists if a new one is being assigned
    if ticket_in.assignee_id is not None:
        assignee = db.query(User).filter(User.id == ticket_in.assignee_id).first()
        if assignee is None:
            raise HTTPException(
                status_code=422,
                detail=f"User with id {ticket_in.assignee_id} not found",
            )

    # 3. model_dump(exclude_unset=True) is the key — it only returns fields the client
    #    actually sent, so unset fields are never overwritten with None.
    update_data = ticket_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)

    # 4. Refresh the updated_at timestamp manually
    ticket.updated_at = datetime.utcnow().isoformat()

    # 5. Persist and return
    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete(
    "/tickets/{ticket_id}",
    status_code=204,
    summary="Delete a ticket by ID",
)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    # 1. Fetch ticket — 404 if not found
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # 2. Members can only delete their own tickets. Admins can delete any.
    if current_user.role != "admin" and ticket.assignee_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete tickets assigned to you",
        )

    # 3. Delete and commit
    db.delete(ticket)
    db.commit()

    # 4. Return None — FastAPI sends 204 No Content automatically
    return None
