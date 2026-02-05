import pandas as pd
import random
from faker import Faker
from datetime import timedelta
import json

# Initialize Faker and seed
fake = Faker()
Faker.seed(42)
random.seed(42)

# Defining choices
statuses = ["Open", "Closed", "Escalated"]
categories = ["Billing", "Technical", "Product", "Shipping", "Account Access"]
priorities = ["Low", "Medium", "High"]

# Generate mock support ticket data
support_data = []
for i in range(100):
    ticket_id = f"TKT{1000 + i}"
    account_id = f"SAL{random.randint(1, 999):04d}"
    customer_id = f"NET{random.randint(1, 999):04d}"
    
    created_date = fake.date_between(start_date='-6M', end_date='today')
    resolved_date = created_date + timedelta(days=random.randint(1, 15)) if random.choice([True, False]) else None
    
    record = {
        "Ticket_ID": ticket_id,
        "Customer_ID": customer_id,
        "Account_ID": account_id,
        "Created_Date": str(created_date),
        "Resolved_Date": str(resolved_date) if resolved_date else None,
        "Status": random.choice(statuses),
        "Category": random.choice(categories),
        "CSAT_Score": random.randint(1, 5),
        "Assigned_Agent": fake.name(),
        "Priority": random.choice(priorities)
    }
    support_data.append(record)

# Save to JSON
json_path = "Output_Data/mock_support_tickets.json"
with open(json_path, "w") as f:
    json.dump(support_data, f, indent=2)