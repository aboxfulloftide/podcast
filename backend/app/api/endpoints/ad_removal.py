from fastapi import APIRouter, Depends, HTTPException, status
from mysql.connector.connection import MySQLConnection
from app.api import deps
from app.crud import crud_ad_removal, crud_subscription
from app.schemas import ad_removal as ad_removal_schema
from app.schemas import user as user_schema

router = APIRouter()

@router.post("/", response_model=ad_removal_schema.AdRemovalRule)
def create_or_update_ad_removal_rule(
    *,
    db: MySQLConnection = Depends(deps.get_db),
    current_user: user_schema.User = Depends(deps.get_current_user),
    rule_in: ad_removal_schema.AdRemovalRuleCreate,
):
    """
    Create or update an ad removal rule for a subscription.
    """
    db_gen = next(db)

    # Verify that the subscription belongs to the current user
    subscription = crud_subscription.get_subscription_by_id(db_gen, rule_in.subscription_id)
    if not subscription or subscription['user_id'] != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to modify this subscription's rules.",
        )
    
    # Check if a rule already exists for this subscription
    existing_rule = crud_ad_removal.get_ad_removal_rule_by_subscription_id(db_gen, rule_in.subscription_id)

    if existing_rule:
        # Update existing rule
        rule = crud_ad_removal.update_ad_removal_rule(db_gen, existing_rule['id'], rule_in)
    else:
        # Create new rule
        rule = crud_ad_removal.create_ad_removal_rule(db_gen, rule_in)
    
    return rule

@router.get("/{subscription_id}", response_model=ad_removal_schema.AdRemovalRule)
def get_ad_removal_rule(
    subscription_id: int,
    db: MySQLConnection = Depends(deps.get_db),
    current_user: user_schema.User = Depends(deps.get_current_user),
):
    """
    Retrieve an ad removal rule for a specific subscription.
    """
    db_gen = next(db)

    # Verify that the subscription belongs to the current user
    subscription = crud_subscription.get_subscription_by_id(db_gen, subscription_id)
    if not subscription or subscription['user_id'] != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this subscription's rules.",
        )
    
    rule = crud_ad_removal.get_ad_removal_rule_by_subscription_id(db_gen, subscription_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad removal rule not found for this subscription.")
    
    return rule
