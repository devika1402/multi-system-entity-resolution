import pandas as pd
import os

# Ensure output directory exists
os.makedirs("Duplicates_and_Profiles", exist_ok=True)

# Load datasets
netsuite = pd.read_csv('Original_Datasets/netsuite.csv')
salesforce = pd.read_csv('Original_Datasets/salesforce.csv')
stripe = pd.read_csv('Original_Datasets/stripe.csv')

print("=== DUPLICATE INVESTIGATION ===")

# === Stripe_ID Duplicates ===
print("\n[Salesforce] Stripe_ID Duplicates:")
sf_stripe_dupes = salesforce[salesforce.duplicated('Stripe_ID', keep=False)]
print(f"Count: {sf_stripe_dupes['Stripe_ID'].nunique()}")
print(sf_stripe_dupes.groupby('Stripe_ID').size().sort_values(ascending=False).head())

# Save associated names/emails
sf_stripe_grouped = sf_stripe_dupes.groupby('Stripe_ID')[['Account_Name', 'Email']].agg(lambda x: list(set(x)))
sf_stripe_grouped.to_csv('Duplicates_and_Profiles/stripeid_salesforce_profiles.csv')

print("\n[NetSuite] Stripe_ID Duplicates:")
ns_stripe_dupes = netsuite[netsuite.duplicated('Stripe_ID', keep=False)]
print(f"Count: {ns_stripe_dupes['Stripe_ID'].nunique()}")
print(ns_stripe_dupes.groupby('Stripe_ID').size().sort_values(ascending=False).head())

# Save associated names
ns_stripe_grouped = ns_stripe_dupes.groupby('Stripe_ID')[['Customer_Name']].agg(lambda x: list(set(x)))
ns_stripe_grouped.to_csv('Duplicates_and_Profiles/stripeid_netsuite_profiles.csv')

# === Account_ID Duplicates in Salesforce ===
print("\n[Salesforce] Account_ID Duplicates:")
sf_acc_dupes = salesforce[salesforce.duplicated('Account_ID', keep=False)]
print(f"Count: {sf_acc_dupes['Account_ID'].nunique()}")
print(sf_acc_dupes.groupby('Account_ID').size().sort_values(ascending=False).head())

sf_acc_grouped = sf_acc_dupes.groupby('Account_ID')[['Account_Name', 'Email']].agg(lambda x: list(set(x)))
sf_acc_grouped.to_csv('Duplicates_and_Profiles/duplicate_account_ids.csv')

# === Customer_ID Duplicates in NetSuite ===
print("\n[NetSuite] Customer_ID Duplicates:")
ns_cust_dupes = netsuite[netsuite.duplicated('Customer_ID', keep=False)]
print(f"Count: {ns_cust_dupes['Customer_ID'].nunique()}")
print(ns_cust_dupes.groupby('Customer_ID').size().sort_values(ascending=False).head())

ns_cust_grouped = ns_cust_dupes.groupby('Customer_ID')[['Customer_Name']].agg(lambda x: list(set(x)))
ns_cust_grouped.to_csv('Duplicates_and_Profiles/duplicate_customer_ids.csv')

# === Revenue Pattern Profiling ===
print("\n[NetSuite] Monthly Revenue Patterns:")

netsuite['Date'] = pd.to_datetime(netsuite['Date'], dayfirst=True, errors='coerce')
netsuite['YearMonth'] = netsuite['Date'].dt.to_period('M')

revenue_profile = netsuite.groupby(['Customer_ID', 'YearMonth'])['Revenue'].agg(['count', 'sum']).reset_index()
revenue_profile = revenue_profile[revenue_profile['count'] > 1]

revenue_profile.to_csv('Duplicates_and_Profiles/netsuite_monthly_revenue_duplicates.csv', index=False)

print("\n✔ Grouped profiles and revenue patterns saved to 'Duplicates_and_Profiles/' folder.")