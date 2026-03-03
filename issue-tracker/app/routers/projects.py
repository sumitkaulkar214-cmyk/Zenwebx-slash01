from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectRead

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectRead, status_code=201, summary="Create a new project")
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    # Check for duplicate project name
    existing = db.query(Project).filter(Project.name == project_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project name already exists")

    db_project = Project(name=project_in.name, description=project_in.description)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("", response_model=List[ProjectRead], summary="List all projects")
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@router.get("/{project_id}", response_model=ProjectRead, summary="Get a single project by ID")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
