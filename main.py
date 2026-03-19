import pandas as pd
import numpy as np
import difflib

# 1. Define Paths
file_a = r'C:\Users\ASROCK\Desktop\Management\PROJECT\PROJECT 1 - AUTOMATED FINANCIAL PIPELINE\system-reconciliation-pipeline\data\raw\system_a_golden.csv'
file_b = r'C:\Users\ASROCK\Desktop\Management\PROJECT\PROJECT 1 - AUTOMATED FINANCIAL PIPELINE\system-reconciliation-pipeline\data\raw\system_b_messy.csv'
output_final_anomalies = r'C:\Users\ASROCK\Desktop\Management\PROJECT\PROJECT 1 - AUTOMATED FINANCIAL PIPELINE\system-reconciliation-pipeline\data\raw\final_anomalies_for_ML.csv'

print("🚀 INITIALIZING MASTER RECONCILIATION PIPELINE...\n")
df_a = pd.read_csv(file_a)
df_b = pd.read_csv(file_b)

total_records = len(df_a)

# --- TIER 1: EXACT MATCH ---
print("Step 1: Running Tier 1 (Exact Match Engine)...")
merged = pd.merge(df_a, df_b, how='outer', indicator=True)
exact_matches = merged[merged['_merge'] == 'both']
un_a = merged[merged['_merge'] == 'left_only'].drop(columns=['_merge']).copy()
un_b = merged[merged['_merge'] == 'right_only'].drop(columns=['_merge']).copy()

# --- TIER 2: FUZZY TEXT MATCHING ---
print("Step 2: Running Tier 2 (Fuzzy Text Resolution)...")
def get_similarity(str1, str2):
    return difflib.SequenceMatcher(None, str(str1), str(str2)).ratio()

potentials_text = pd.merge(un_a, un_b, on=['step', 'type', 'nameOrig', 'amount'], suffixes=('_A', '_B'))
potentials_text['sim_score'] = potentials_text.apply(lambda row: get_similarity(row['nameDest_A'], row['nameDest_B']), axis=1)
resolved_typos = potentials_text[potentials_text['sim_score'] >= 0.80]

# Filter out the resolved typos from our unmatched buckets
un_a = un_a[~un_a['nameDest'].isin(resolved_typos['nameDest_A'])]
un_b = un_b[~un_b['nameDest'].isin(resolved_typos['nameDest_B'])]

# --- TIER 3: NUMERIC TOLERANCE ---
print("Step 3: Running Tier 3 (Numeric Variance Engine)...")
potentials_num = pd.merge(un_a, un_b, on=['step', 'type', 'nameOrig', 'nameDest'], suffixes=('_A', '_B'))
potentials_num['variance'] = abs(potentials_num['amount_A'] - potentials_num['amount_B'])
resolved_amounts = potentials_num[(potentials_num['variance'] > 0) & (potentials_num['variance'] <= 0.50)]

# Filter out the resolved amounts from our unmatched buckets
un_a = un_a[~un_a['amount'].isin(resolved_amounts['amount_A'])]

# --- FINAL REPORT ---
print("\n=============================================")
print(" 📊 PIPELINE PERFORMANCE REPORT ")
print("=============================================")
print(f"Total Processed Records: {total_records:,}")
print(f"✅ Tier 1 (Exact):       {len(exact_matches):,}")
print(f"✅ Tier 2 (Typos):       {len(resolved_typos):,}")
print(f"✅ Tier 3 (Variances):   {len(resolved_amounts):,}")

total_reconciled = len(exact_matches) + len(resolved_typos) + len(resolved_amounts)
success_rate = (total_reconciled / total_records) * 100

print(f"\n🌟 OVERALL AUTOMATION SUCCESS RATE: {success_rate:.2f}%")
print(f"❌ True Anomalies Remaining: {len(un_a):,}")

# Save the true anomalies for Machine Learning (Phase 3)
un_a.to_csv(output_final_anomalies, index=False)
print(f"\nSaved true anomalies to: {output_final_anomalies}")

from datetime import datetime

# ... (keep all your existing matching logic here) ...

# --- NEW: THE AUTO-LOGGING SYSTEM ---
log_file_path = r'C:\Users\ASROCK\Desktop\Management\PROJECT\PROJECT 1 - AUTOMATED FINANCIAL PIPELINE\system-reconciliation-pipeline\data\raw\reconciliation_history.log'

# Create the log entry
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log_entry = f"""
--------------------------------------------------
SCAN COMPLETED AT: {timestamp}
Total Records:     {total_records:,}
Success Rate:      {success_rate:.2f}%
Exact Matches:     {len(exact_matches):,}
Fuzzy Matches:     {len(resolved_typos):,}
Numeric Matches:   {len(resolved_amounts):,}
TRUE ANOMALIES:    {len(un_a):,}
--------------------------------------------------
"""

# Write to the file ( 'a' means append, so it adds to the bottom of the list)
with open(log_file_path, "a") as f:
    f.write(log_entry)

print(f"📊 Audit log updated at: {log_file_path}")