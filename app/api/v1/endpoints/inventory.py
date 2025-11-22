from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.inventory import Inventory
from app.models.user import User
from app.schemas.inventory import InventoryCreate, InventoryResponse, InventoryUpdate
from app.api.deps import get_current_admin

router = APIRouter()


@router.get("/", response_model=List[InventoryResponse])
def list_inventory(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all inventory records"""
    inventory = db.query(Inventory).offset(skip).limit(limit).all()
    return inventory


@router.get("/product/{product_id}", response_model=InventoryResponse)
def get_inventory_by_product(product_id: UUID, db: Session = Depends(get_db)):
    """Get inventory by product ID"""
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


@router.get("/{inventory_id}", response_model=InventoryResponse)
def get_inventory(inventory_id: UUID, db: Session = Depends(get_db)):
    """Get inventory by ID"""
    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


@router.post("/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def create_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Create new inventory record (Admin only)"""
    db_inventory = Inventory(**inventory.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


@router.patch("/{inventory_id}", response_model=InventoryResponse)
def update_inventory(
    inventory_id: UUID,
    inventory_update: InventoryUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Update inventory (Admin only)"""
    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")

    update_data = inventory_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(inventory, field, value)

    db.commit()
    db.refresh(inventory)
    return inventory


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory(
    inventory_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Delete inventory (Admin only)"""
    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")

    db.delete(inventory)
    db.commit()
    return None
