import pandas as pd
import numpy as np
import re

def clean_csv_files(netsuite_path, salesforce_path, stripe_path, 
                    output1_path, output2_path, output3_path):
    """
    Cleans three CSV files (NetSuite, Salesforce, Stripe) with:
    - Deduplication, date parsing, email/phone validation
    - Cleaning of numeric and ID fields
    - Additional checks for conflicting values, outliers, and standardization
    """

    df1 = pd.read_csv(netsuite_path)
    df2 = pd.read_csv(salesforce_path)
    df3 = pd.read_csv(stripe_path)

    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()
    df3.columns = df3.columns.str.strip()

    for col in ["Customer_ID", "Stripe_ID"]:
        if col in df1.columns:
            df1[col] = df1[col].astype(str).str.strip()
    if "Customer_ID" in df3.columns:
        df3["Customer_ID"] = df3["Customer_ID"].astype(str).str.strip()
    if "Stripe_ID" in df2.columns:
        df2["Stripe_ID"] = df2["Stripe_ID"].astype(str).str.strip()
    if "Account_ID" in df2.columns:
        df2["Account_ID"] = df2["Account_ID"].astype(str).str.strip()

    cleaning_report = {
        "netsuite": {"rows_before": len(df1)},
        "salesforce": {"rows_before": len(df2)},
        "stripe": {"rows_before": len(df3)}
    }

    # === Clean NetSuite ===
    df1.drop_duplicates(inplace=True)
    df1["Date"] = pd.to_datetime(df1["Date"], errors="coerce")
    df1.dropna(subset=["Date"], inplace=True)
    df1["Revenue"] = df1["Revenue"].astype(str).str.replace(r"[^\d\.]", "", regex=True)
    df1["Revenue"] = pd.to_numeric(df1["Revenue"], errors="coerce")
    df1.dropna(subset=["Revenue"], inplace=True)
    df1 = df1[df1["Revenue"].between(0, 1_000_000)]  # outlier check

    # Standardize names
    df1["Customer_Name"] = df1["Customer_Name"].str.strip().str.title()

    cleaning_report["netsuite"].update({
        "duplicates_removed": len(df1),
        "invalid_dates": df1["Date"].isna().sum(),
        "invalid_revenue_rows": df1["Revenue"].isna().sum(),
        "missing_stripe_id": df1["Stripe_ID"].isna().sum(),
        "rows_after": len(df1)
    })

    # === Clean Salesforce ===
    df2.drop_duplicates(inplace=True)
    df2["Closed_Contract_Date"] = pd.to_datetime(df2["Closed_Contract_Date"], errors="coerce")
    df2.dropna(subset=["Closed_Contract_Date"], inplace=True)
    df2["Phone_Number"] = df2["Phone_Number"].astype(str).apply(lambda x: re.sub(r"\D+", "", x))

    def is_valid_email(val):
        pattern = r"^[A-Za-z0-9\._%+\-]+@[A-Za-z0-9\.-]+\.[A-Za-z]{2,}$"
        return bool(re.match(pattern, str(val).strip()))

    valid_emails = df2["Email"].apply(is_valid_email)
    df2.loc[~valid_emails, "Email"] = np.nan

    # Standardize names
    df2["Account_Name"] = df2["Account_Name"].str.strip().str.title()

    cleaning_report["salesforce"].update({
        "duplicates_removed": len(df2),
        "invalid_dates": df2["Closed_Contract_Date"].isna().sum(),
        "phone_numbers_fixed": sum(~df2["Phone_Number"].str.match(r"^\d+$")),
        "invalid_emails": (~valid_emails).sum(),
        "rows_after": len(df2)
    })

    # === Clean Stripe ===
    df3.drop_duplicates(inplace=True)
    df3["Date"] = pd.to_datetime(df3["Date"], errors="coerce")
    df3.dropna(subset=["Date"], inplace=True)
    df3["Amount"] = df3["Amount"].astype(str).str.replace(r"[^\d\.]", "", regex=True)
    df3["Amount"] = pd.to_numeric(df3["Amount"], errors="coerce")
    df3.dropna(subset=["Amount"], inplace=True)
    df3 = df3[df3["Amount"].between(0, 1_000_000)]  # outlier check

    # Standardize names
    df3["Customer_Name"] = df3["Customer_Name"].str.strip().str.title()

    cleaning_report["stripe"].update({
        "duplicates_removed": len(df3),
        "invalid_dates": df3["Date"].isna().sum(),
        "invalid_amounts": df3["Amount"].isna().sum(),
        "rows_after": len(df3)
    })

    # === Currency check ===
    print("\n[Stripe] Unique currencies:", df3["Currency"].unique())

    # === Cross-system conflict check for Stripe_ID ===
    merged = df2.merge(df1, on="Stripe_ID", how="inner", suffixes=("_sf", "_ns"))
    name_conflicts = merged[merged["Account_Name"] != merged["Customer_Name"]]
    print(f"\n[Conflict] Stripe_IDs with mismatched names across Salesforce and NetSuite: {len(name_conflicts)}")

    # === Save cleaned files ===
    df1.to_csv(output1_path, index=False)
    df2.to_csv(output2_path, index=False)
    df3.to_csv(output3_path, index=False)

    print("\n======================")
    print("DATA CLEANING REPORT")
    print("======================")
    for section, details in cleaning_report.items():
        print(f"\n--- {section.upper()} ---")
        for k, v in details.items():
            print(f"{k}: {v}")

if __name__ == "__main__":
    clean_csv_files(
        netsuite_path="Original_Datasets/netsuite.csv",
        salesforce_path="Original_Datasets/salesforce.csv",
        stripe_path="Original_Datasets/stripe.csv",
        output1_path="Cleaned_Datasets/netsuite_cleaned.csv",
        output2_path="Cleaned_Datasets/salesforce_cleaned.csv",
        output3_path="Cleaned_Datasets/stripe_cleaned.csv"
    )