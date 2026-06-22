# Multi-System Entity Resolution

Three internal systems, three schemas, no shared key that works cleanly across all of them. This project takes Stripe payment records, Salesforce CRM records, and NetSuite ERP records, finds which rows across the three systems describe the same customer, and merges them into a single view a downstream report can rely on. Across approximately two million rows, 98% of foreign-key mismatches resolved.

## What it does

The pipeline runs in sequence: inspect the raw data, find and characterise duplicates, clean and standardise each system's records, then match across systems and produce a unified financial view per customer.

The hardest part is the cross-system matching. Stripe, Salesforce, and NetSuite use different ID schemes, and a customer who exists in all three is linked by a `Stripe_ID` that the other two systems carry inconsistently. The cleaning step standardises names, validates emails and phone numbers, filters revenue outliers, and parses dates. The matching step checks that the `Stripe_ID` linkage holds and surfaces every customer where it does not.

## Scripts

**`primary_data_inspection.py`** — Verifies uniqueness of key identifiers (`Customer_ID`, `Account_ID`, `Stripe_ID`) and checks whether the expected 1:1 relationship between Salesforce and NetSuite holds.

**`inspect_duplicates.py`** — Identifies duplicate records across all three systems and generates grouped profiles for duplicates, including monthly revenue patterns for repeated NetSuite entries.

**`clean_datasets.py`** — Deduplicates, validates emails and phone numbers, parses transaction dates, filters revenue outliers, and standardises customer names. Runs a cross-system consistency check for mismatched names on shared `Stripe_ID`s. Writes cleaned outputs to `Cleaned_Datasets/`.

**`analyse_cleaned_datasets.py`** — Matches cleaned records across systems and produces a combined financial report: total revenue (NetSuite) and total cash (Stripe) per customer, matched by `Stripe_ID`. Surfaces any customers present in one system but missing from another. Writes to `Output_Data/combined_financials.csv`.

**`create_mock_data.py`** — Generates synthetic support tickets (CSAT scores, priorities, agent names, ticket timelines) for downstream testing. Optional; not required to run the main pipeline.

## How to run

```bash
python primary_data_inspection.py
python inspect_duplicates.py
python clean_datasets.py
python analyse_cleaned_datasets.py
```

## Dependencies

```bash
pip install pandas numpy faker
```
