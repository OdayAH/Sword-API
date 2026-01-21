from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.address import Address
# from app.models.user import User
from app.schemas import AddressCreate, AddressResponse, AddressUpdate
from app.api.auth import get_current_user

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.get("", response_model=list[AddressResponse])
def get_user_addresses(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    addresses = db.query(Address).filter(Address.user_id == user_id).all()
    return addresses


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(address_id: int, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    return address


@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(address: AddressCreate, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if address.is_default:
            db.query(Address).filter(Address.user_id == user_id).update(
                {Address.is_default: False}
            )

        new_address = Address(
            user_id=user_id,
            **address.model_dump()
        )
        db.add(new_address)
        db.commit()
        db.refresh(new_address)
        
        return new_address
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating address: {str(e)}")


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    address_update: AddressUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    try:
        data = address_update.model_dump(exclude_unset=True)

        if data.get("is_default") is True:
            db.query(Address).filter(
                Address.user_id == user_id,
                Address.id != address_id
            ).update({Address.is_default: False})

        for field, value in data.items():
            setattr(address, field, value)
        
        db.commit()
        db.refresh(address)
        
        return address
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating address: {str(e)}")


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: int, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    try:
        db.delete(address)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting address: {str(e)}")
