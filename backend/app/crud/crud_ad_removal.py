from mysql.connector.connection import MySQLConnection
from app.schemas.ad_removal import AdRemovalRuleCreate, AdRemovalMarkerCreate

def create_ad_removal_rule(db: MySQLConnection, rule: AdRemovalRuleCreate):
    """
    Create a new ad removal rule and its associated markers.
    """
    cursor = db.cursor()

    # Insert the rule
    rule_query = "INSERT INTO ad_removal_rules (subscription_id, strategy) VALUES (%s, %s)"
    cursor.execute(rule_query, (rule.subscription_id, rule.strategy))
    rule_id = cursor.lastrowid

    # Insert markers
    if rule.markers:
        marker_query = "INSERT INTO ad_removal_markers (rule_id, marker_time_ms, marker_order) VALUES (%s, %s, %s)"
        marker_data = [
            (rule_id, marker.marker_time_ms, marker.marker_order)
            for marker in rule.markers
        ]
        cursor.executemany(marker_query, marker_data)
    
    db.commit()
    cursor.close()
    return {"id": rule_id, "subscription_id": rule.subscription_id, "strategy": rule.strategy, "markers": rule.markers}

def get_ad_removal_rule_by_subscription_id(db: MySQLConnection, subscription_id: int):
    """
    Get an ad removal rule and its markers by subscription ID.
    """
    cursor = db.cursor(dictionary=True)

    # Get the rule
    rule_query = "SELECT id, subscription_id, strategy FROM ad_removal_rules WHERE subscription_id = %s"
    cursor.execute(rule_query, (subscription_id,))
    rule = cursor.fetchone()

    if rule:
        # Get its markers
        marker_query = "SELECT id, rule_id, marker_time_ms, marker_order FROM ad_removal_markers WHERE rule_id = %s ORDER BY marker_order"
        cursor.execute(marker_query, (rule['id'],))
        markers = cursor.fetchall()
        rule['markers'] = markers
    
    cursor.close()
    return rule

def update_ad_removal_rule(db: MySQLConnection, rule_id: int, rule: AdRemovalRuleCreate):
    """
    Update an existing ad removal rule and its associated markers.
    """
    cursor = db.cursor()

    # Update the rule
    rule_query = "UPDATE ad_removal_rules SET strategy = %s WHERE id = %s"
    cursor.execute(rule_query, (rule.strategy, rule_id))

    # Delete existing markers for this rule
    delete_markers_query = "DELETE FROM ad_removal_markers WHERE rule_id = %s"
    cursor.execute(delete_markers_query, (rule_id,))

    # Insert new markers
    if rule.markers:
        marker_query = "INSERT INTO ad_removal_markers (rule_id, marker_time_ms, marker_order) VALUES (%s, %s, %s)"
        marker_data = [
            (rule_id, marker.marker_time_ms, marker.marker_order)
            for marker in rule.markers
        ]
        cursor.executemany(marker_query, marker_data)
    
    db.commit()
    cursor.close()
    return {"id": rule_id, "subscription_id": rule.subscription_id, "strategy": rule.strategy, "markers": rule.markers}
