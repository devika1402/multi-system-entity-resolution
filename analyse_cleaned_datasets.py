import pandas as pd

def analyze_datasets(df_netsuite, df_salesforce, df_stripe):
    """
    Analyzes how the three DataFrames (assumed cleaned) are interconnected.
    
    Parameters:
    -----------
    df_netsuite : pd.DataFrame (NetSuite)
       Expected columns: [Customer_ID, Customer_Name, Stripe_ID, Revenue, Date]
    df_salesforce : pd.DataFrame (Salesforce)
       Expected columns: [Account_ID, Account_Name, Stripe_ID, Email, Phone_Number, Closed_Contract_Date]
    df_stripe : pd.DataFrame (Stripe)
       Expected columns: [Customer_ID, Customer_Name, Metadata_SAL_ID, Amount, Currency, Date]
       Note: Stripe's Customer_ID is the Payment Gateway ID.
    
    Returns:
    --------
    A dictionary with the following keys:
       - largest_payment_email: Email of the customer with the single largest payment.
       - crm_details_for_top_transactions: Salesforce (CRM) details for the customer with the highest transaction count.
       - combined_financials: DataFrame with total revenue (from NetSuite) and total cash (from Stripe) per Payment Gateway customer.
       - connection_issues: List of issues noticed about the connection between systems.
    """
    
    results = {}
    
    # --------------------------------------------------------------------------
    # 1) Largest Payment Email
    # --------------------------------------------------------------------------
    df_stripe["Amount"] = pd.to_numeric(df_stripe["Amount"], errors="coerce")
    df_stripe = df_stripe.dropna(subset=["Amount"])
    
    if df_stripe.empty:
        results["largest_payment_email"] = None
    else:
        largest_payment_idx = df_stripe["Amount"].idxmax()
        largest_payment_row = df_stripe.loc[largest_payment_idx]
        payment_gateway_id = largest_payment_row["Customer_ID"]
    
        # Use NetSuite Stripe_ID to match the Payment Gateway ID
        net_row = df_netsuite.loc[df_netsuite["Stripe_ID"] == payment_gateway_id]
        if net_row.empty:
            results["largest_payment_email"] = None
        else:
            sf_row = df_salesforce.loc[df_salesforce["Stripe_ID"] == payment_gateway_id]
            if sf_row.empty:
                results["largest_payment_email"] = None
            else:
                results["largest_payment_email"] = sf_row["Email"].iloc[0]
    
    # --------------------------------------------------------------------------
    # 2) CRM details for highest-transaction customer
    # --------------------------------------------------------------------------
    # Filter Stripe records to only those Payment Gateway IDs that exist in NetSuite.
    valid_pg_ids = set(df_netsuite["Stripe_ID"].dropna())
    filtered_stripe = df_stripe[df_stripe["Customer_ID"].isin(valid_pg_ids)]
    
    if filtered_stripe.empty:
        results["crm_details_for_top_transactions"] = None
    else:
        txn_counts = filtered_stripe.groupby("Customer_ID")["Amount"].count().reset_index(name="txn_count")
        top_txn = txn_counts.loc[txn_counts["txn_count"].idxmax()]
        payment_gateway_id_top = top_txn["Customer_ID"]
    
        net_match = df_netsuite.loc[df_netsuite["Stripe_ID"] == payment_gateway_id_top]
        if net_match.empty:
            results["crm_details_for_top_transactions"] = None
        else:
            sf_match = df_salesforce.loc[df_salesforce["Stripe_ID"] == payment_gateway_id_top]
            if sf_match.empty:
                results["crm_details_for_top_transactions"] = None
            else:
                results["crm_details_for_top_transactions"] = sf_match.to_dict(orient="records")
    
    # --------------------------------------------------------------------------
    # 3) Combined Financials per customer:
    #      Total revenue from NetSuite and total cash from Stripe (grouped by Payment Gateway ID)
    # --------------------------------------------------------------------------
    ns_rev = df_netsuite.groupby("Stripe_ID")["Revenue"].sum().reset_index()
    ns_rev.columns = ["Payment_Gateway_ID", "total_revenue"]
    
    stripe_cash = df_stripe.groupby("Customer_ID")["Amount"].sum().reset_index()
    stripe_cash.columns = ["Payment_Gateway_ID", "total_cash"]
    
    combined_financials = pd.merge(ns_rev, stripe_cash, on="Payment_Gateway_ID", how="outer")
    results["combined_financials"] = combined_financials

    # --------------------------------------------------------------------------
    # 4) Identify Connection Issues
    # --------------------------------------------------------------------------
    issues = []
    missing_ns = df_netsuite["Stripe_ID"].isna().sum()
    missing_sf = df_salesforce["Stripe_ID"].isna().sum()
    if missing_ns > 0:
        issues.append(f"{missing_ns} NetSuite rows have missing Stripe_ID.")
    if missing_sf > 0:
        issues.append(f"{missing_sf} Salesforce rows have missing Stripe_ID.")
    
    unmatched_pg = ~df_stripe["Customer_ID"].isin(df_netsuite["Stripe_ID"])
    unmatched_count = unmatched_pg.sum()
    if unmatched_count > 0:
        issues.append(f"{unmatched_count} Stripe rows (Payment Gateway IDs) cannot be matched to NetSuite via Stripe_ID.")
    if not issues:
        issues.append("No major issues found; all connections appear consistent.")
    
    results["connection_issues"] = issues
    
    return results


if __name__ == "__main__":
    df_netsuite = pd.read_csv("Cleaned_Datasets/netsuite_cleaned.csv")
    df_salesforce = pd.read_csv("Cleaned_Datasets/salesforce_cleaned.csv")
    df_stripe = pd.read_csv("Cleaned_Datasets/stripe_cleaned.csv")
    
    analysis_results = analyze_datasets(df_netsuite, df_salesforce, df_stripe)
    
    print("1) Email of customer with the single largest payment in Stripe:")
    print(analysis_results["largest_payment_email"], "\n")
    
    print("2) CRM details (Salesforce) for the customer with the highest number of transactions:")
    print(analysis_results["crm_details_for_top_transactions"], "\n")
    
    print("3) Combined financials (total revenue and total cash) per customer:")
    print(analysis_results["combined_financials"], "\n")
    
    print("4) Connection issues between systems:")
    for issue in analysis_results["connection_issues"]:
        print("  -", issue)
    
    # --------------------------------------------------------------------------
    # Save the combined financials DataFrame to a separate CSV file:
    analysis_results["combined_financials"].to_csv("Output_Data/combined_financials.csv", index=False)
    print("\nCombined financials saved as 'combined_financials.csv' in Output_Data folder.")