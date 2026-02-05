import pandas as pd

# === Loading the datasets ===
netsuite = pd.read_csv('Original_Datasets/netsuite.csv')
salesforce = pd.read_csv('Original_Datasets/salesforce.csv')
stripe = pd.read_csv('Original_Datasets/stripe.csv')

# === Uniqueness Checks ===

print("=== Uniqueness Checks ===")

#  Salesforce: Checking if Account_ID is unique
is_account_id_unique = salesforce['Account_ID'].is_unique
print(f"Salesforce: Is Account_ID unique? {is_account_id_unique}")

#  NetSuite: Checking if Customer_ID is unique
is_customer_id_unique = netsuite['Customer_ID'].is_unique
print(f"NetSuite: Is Customer_ID unique? {is_customer_id_unique}")

#  Stripe_ID uniqueness in Salesforce
stripe_id_salesforce_duplicates = salesforce['Stripe_ID'].duplicated().sum()
print(f"Salesforce: Duplicate Stripe_IDs? {stripe_id_salesforce_duplicates} found")

#  Stripe_ID uniqueness in NetSuite
stripe_id_netsuite_duplicates = netsuite['Stripe_ID'].duplicated().sum()
print(f"NetSuite: Duplicate Stripe_IDs? {stripe_id_netsuite_duplicates} found")

# === Checking Relationships ===

print("\n=== Relationship Check ===")

# Checking if Stripe_ID matches between Salesforce and NetSuite (1:1 relationship)
netsuite_stripe_id = netsuite.loc[0, 'Stripe_ID']
salesforce_stripe_id = salesforce.loc[0, 'Stripe_ID']
same_stripe_id = netsuite_stripe_id == salesforce_stripe_id
print(f"[Salesforce–NetSuite] Stripe_ID match: {same_stripe_id} ({netsuite_stripe_id})")

# Checking if Stripe_ID appears in Stripe's Customer_IDs
stripe_ids = stripe['Customer_ID'].tolist()
netsuite_in_stripe = netsuite_stripe_id in stripe_ids
salesforce_in_stripe = salesforce_stripe_id in stripe_ids
print(f"[NetSuite → Stripe] Stripe_ID in Stripe: {netsuite_in_stripe}")
print(f"[Salesforce → Stripe] Stripe_ID in Stripe: {salesforce_in_stripe}")