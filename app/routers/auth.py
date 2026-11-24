from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["autenticazione"])


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return request.app.state.templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    email: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or not verify_password(password, user.password_hash):
        return request.app.state.templates.TemplateResponse(
            request, "login.html", {"error": "Email o password non validi"}, status_code=400
        )
    request.session.clear()
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)


@router.get("/registrazione", response_class=HTMLResponse)
def registration_page(request: Request):
    return request.app.state.templates.TemplateResponse(request, "register.html", {"error": None})


@router.post("/registrazione", response_class=HTMLResponse)
def register(
    request: Request,
    display_name: str = Form(min_length=2, max_length=80),
    email: str = Form(max_length=254),
    password: str = Form(min_length=8),
    db: Session = Depends(get_db),
):
    normalized_email = email.strip().lower()
    if db.scalar(select(User).where(User.email == normalized_email)):
        return request.app.state.templates.TemplateResponse(
            request, "register.html", {"error": "Email già registrata"}, status_code=400
        )
    user = User(
        display_name=display_name.strip(),
        email=normalized_email,
        password_hash=hash_password(password),
        role=UserRole.AUTOMOBILISTA,
    )
    db.add(user)
    db.commit()
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
