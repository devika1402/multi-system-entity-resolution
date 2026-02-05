# Customer Systems Integration & Analysis



## 📁 Directory Structure
```
├── Original_Datasets/
│   ├── netsuite.csv
│   ├── salesforce.csv
│   └── stripe.csv
│
├── Cleaned_Datasets/
│   ├── netsuite_cleaned.csv
│   ├── salesforce_cleaned.csv
│   └── stripe_cleaned.csv
│
├── Duplicates_and_Profiles/
│   ├── stripeid_salesforce_profiles.csv
│   ├── stripeid_netsuite_profiles.csv
│   ├── duplicate_account_ids.csv
│   ├── duplicate_customer_ids.csv
│   └── netsuite_monthly_revenue_duplicates.csv
│
├── Output_Data/
│   └── combined_financials.csv
│   └── mock_support_tickets.json
│
├── primary_data_inspection.py
├── inspect_duplicates.py
├── clean_datasets.py
├── analyse_cleaned_datasets.py
└── create_mock_data.py

```

---

## 📜 Overview of the Scripts (in the sequence of their creation)

###  `primary_data_inspection.py`

Performs preliminary checks on the original datasets:
- Verifies uniqueness of key identifiers (`Customer_ID`, `Account_ID`, `Stripe_ID`).
- Checks 1:1 relationship between Salesforce and NetSuite based on `Stripe_ID`.
- Confirms if Stripe `Customer_ID`s are found in the other datasets.

---

###  `inspect_duplicates.py`

Analyzes **duplicate records** in the datasets:
- Identifies duplicate `Stripe_ID`s, `Customer_ID`s, and `Account_ID`s.
- Saves grouped profiles for duplicate entries, including associated names and emails.
- Generates reports on **monthly revenue patterns** for repeated entries in NetSuite.

---

###  `clean_datasets.py`

Cleans and standardizes the datasets with the following transformations:
- **Deduplication** and invalid data removal.
- **Email and phone number validation** for Salesforce.
- **Date parsing** for transaction dates.
- **Revenue/Amount outlier filtering** to remove extreme values.
- **Standardization** of customer names and formatting.

Also performs a **cross-system consistency check** to detect mismatched customer names for shared `Stripe_ID`s between NetSuite and Salesforce.

Saves cleaned outputs in `Cleaned_Datasets/`.

---

###  `analyse_cleaned_datasets.py`

Analyzes the relationships between the cleaned datasets and returns:
- The **email** of the customer with the **largest single Stripe payment**.
- The **Salesforce CRM profile** of the customer with the **highest number of Stripe transactions**.
- A **combined financial report** showing:
  - Total revenue (NetSuite)
  - Total cash (Stripe)
  - Per customer, matched by `Stripe_ID`.
- A list of **connection issues** (e.g., missing or unmatched IDs).

Saves the combined financials to `Output_Data/combined_financials.csv`.

---

###  `create_mock_data.py`

Generates **mock support ticket data** for simulation and testing purposes:
- Includes randomized `Ticket_ID`, `Customer_ID`, `Account_ID`, ticket metadata, CSAT scores, and priorities.
- Uses the `Faker` library to simulate agent names and realistic ticket timelines.
- Output: `data/mock_support_tickets.json`

---

## ⚙️ Dependencies

All scripts use standard Python libraries, but you may need to install the following. Additionally, I have included a requirements.txt file:

```bash
pip install pandas numpy faker
```

---

## ✅ Usage (in the order I wrote and ran the files)

### Step 1: Run Initial Inspections
```bash
python primary_data_inspection.py
```

### Step 2: Investigate Duplicates
```bash
python inspect_duplicates.py
```

### Step 3: Clean All Datasets
```bash
python clean_datasets.py
```

### Step 4: Analyze Cleaned Data
```bash
python analyse_cleaned_datasets.py
```

### Step 5:  Generate Mock Support Tickets
```bash
python create_mock_data.py
```

---

## 📈 Sample Outputs

- `Duplicates_and_Profiles/` folder includes summaries like:
  - Duplicate customers/accounts grouped by name or email
  - Revenue inconsistencies over time

- `Output_Data/combined_financials.csv`:
  - Helps compare **invoice revenue** (NetSuite) with **actual payments** (Stripe) per customer.

---