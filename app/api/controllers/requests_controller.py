from sqlalchemy.orm import Session

from app.api.crud import requests as requests_crud
from app.schemas import RequestCreate, RequestResponse, RequestStatusUpdate
from app.enums import Roles


def list_requests(db: Session, user_id: int) -> list[RequestResponse]:
    role_id = requests_crud.get_user_role(db=db, user_id=user_id)

    if role_id == Roles.PROVIDER:
        return requests_crud.list_provider_requests(db=db, provider_id=user_id)

    return requests_crud.list_user_requests(db=db, user_id=user_id)


def get_request(db: Session, user_id: int, request_id: int) -> RequestResponse:
    return requests_crud.get_request(db=db, user_id=user_id, request_id=request_id)


def create_request(db: Session, user_id: int, payload: RequestCreate) -> RequestResponse:
    return requests_crud.create_request(db=db, user_id=user_id, payload=payload)


def update_request_status(
    db: Session,
    user_id: int,
    request_id: int,
    payload: RequestStatusUpdate,
) -> RequestResponse:
    return requests_crud.update_request_status(
        db=db,
        user_id=user_id,
        request_id=request_id,
        payload=payload,
    )


def delete_request(db: Session, user_id: int, request_id: int) -> None:
    requests_crud.delete_request(db=db, user_id=user_id, request_id=request_id)
