import pandas as pd
import numpy as np
import re


def normalize_id(series):
    """Trim identifier values without converting missing values to the string 'nan'."""
    return series.astype("string").str.strip()


def parse_mixed_amount(value):
    """Parse currency strings that use either comma or point decimal separators."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.number)):
        return float(value)

    cleaned = re.sub(r"[^0-9,.-]", "", str(value).strip())
    if not cleaned:
        return np.nan

    comma = cleaned.rfind(",")
    point = cleaned.rfind(".")

    if comma >= 0 and point >= 0:
        decimal_separator = "," if comma > point else "."
        thousands_separator = "." if decimal_separator == "," else ","
        cleaned = cleaned.replace(thousands_separator, "")
        if decimal_separator == ",":
            cleaned = cleaned.replace(",", ".")
    elif comma >= 0:
        decimals = len(cleaned) - comma - 1
        cleaned = cleaned.replace(",", "." if decimals == 2 else "")
    elif point >= 0:
        decimals = len(cleaned) - point - 1
        if decimals != 2:
            cleaned = cleaned.replace(".", "")

    return pd.to_numeric(cleaned, errors="coerce")


def parse_dates(series, *, dayfirst=False):
    """Parse a column that may contain ISO, written-month, or numeric dates."""
    return pd.to_datetime(series, format="mixed", dayfirst=dayfirst, errors="coerce")

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
            df1[col] = normalize_id(df1[col])
    if "Customer_ID" in df3.columns:
        df3["Customer_ID"] = normalize_id(df3["Customer_ID"])
    if "Stripe_ID" in df2.columns:
        df2["Stripe_ID"] = normalize_id(df2["Stripe_ID"])
    if "Account_ID" in df2.columns:
        df2["Account_ID"] = normalize_id(df2["Account_ID"])

    cleaning_report = {
        "netsuite": {"rows_before": len(df1)},
        "salesforce": {"rows_before": len(df2)},
        "stripe": {"rows_before": len(df3)}
    }

    # === Clean NetSuite ===
    before_dedup = len(df1)
    df1.drop_duplicates(inplace=True)
    duplicates_removed = before_dedup - len(df1)
    df1["Date"] = parse_dates(df1["Date"], dayfirst=True)
    invalid_dates = int(df1["Date"].isna().sum())
    df1.dropna(subset=["Date"], inplace=True)
    df1["Revenue"] = df1["Revenue"].apply(parse_mixed_amount)
    invalid_revenue_rows = int(df1["Revenue"].isna().sum())
    df1.dropna(subset=["Revenue"], inplace=True)
    in_range = df1["Revenue"].between(0, 1_000_000)
    revenue_outliers = int((~in_range).sum())
    df1 = df1[in_range]

    # Standardize names
    df1["Customer_Name"] = df1["Customer_Name"].str.strip().str.title()

    cleaning_report["netsuite"].update({
        "duplicates_removed": duplicates_removed,
        "invalid_dates_removed": invalid_dates,
        "invalid_revenue_rows_removed": invalid_revenue_rows,
        "revenue_outliers_removed": revenue_outliers,
        "missing_stripe_id": int(df1["Stripe_ID"].isna().sum()),
        "rows_after": len(df1)
    })

    # === Clean Salesforce ===
    before_dedup = len(df2)
    df2.drop_duplicates(inplace=True)
    duplicates_removed = before_dedup - len(df2)
    df2["Closed_Contract_Date"] = parse_dates(df2["Closed_Contract_Date"])
    invalid_dates = int(df2["Closed_Contract_Date"].isna().sum())
    df2.dropna(subset=["Closed_Contract_Date"], inplace=True)
    original_phone = df2["Phone_Number"].astype("string")
    df2["Phone_Number"] = original_phone.apply(
        lambda x: re.sub(r"\D+", "", x) if pd.notna(x) else pd.NA
    )
    phone_numbers_changed = int((original_phone != df2["Phone_Number"]).fillna(False).sum())

    def is_valid_email(val):
        pattern = r"^[A-Za-z0-9\._%+\-]+@[A-Za-z0-9\.-]+\.[A-Za-z]{2,}$"
        return bool(re.match(pattern, str(val).strip()))

    valid_emails = df2["Email"].apply(is_valid_email)
    df2.loc[~valid_emails, "Email"] = np.nan

    # Standardize names
    df2["Account_Name"] = df2["Account_Name"].str.strip().str.title()

    cleaning_report["salesforce"].update({
        "duplicates_removed": duplicates_removed,
        "invalid_dates_removed": invalid_dates,
        "phone_numbers_standardized": phone_numbers_changed,
        "invalid_emails": int((~valid_emails).sum()),
        "rows_after": len(df2)
    })

    # === Clean Stripe ===
    before_dedup = len(df3)
    df3.drop_duplicates(inplace=True)
    duplicates_removed = before_dedup - len(df3)
    df3["Date"] = parse_dates(df3["Date"], dayfirst=True)
    invalid_dates = int(df3["Date"].isna().sum())
    df3.dropna(subset=["Date"], inplace=True)
    df3["Amount"] = df3["Amount"].apply(parse_mixed_amount)
    invalid_amounts = int(df3["Amount"].isna().sum())
    df3.dropna(subset=["Amount"], inplace=True)
    in_range = df3["Amount"].between(0, 1_000_000)
    amount_outliers = int((~in_range).sum())
    df3 = df3[in_range]

    # Standardize names
    df3["Customer_Name"] = df3["Customer_Name"].str.strip().str.title()

    cleaning_report["stripe"].update({
        "duplicates_removed": duplicates_removed,
        "invalid_dates_removed": invalid_dates,
        "invalid_amounts_removed": invalid_amounts,
        "amount_outliers_removed": amount_outliers,
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
