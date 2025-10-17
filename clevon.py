import pandas as pd
import re

# === User Settings ===

# Path to input Excel file
input_file = "scopus_results.xlsx"

# Sheet name or use default first sheet
sheet_name = 0  # or 'Sheet1'

# Column names for title and abstract
title_col = "Title"
abstract_col = "Abstract"

# Keywords with wildcard support
keywords = [
    "flood*", "risk*", "uncertaint*", "climate change", "hazard*", "resilien*", "vulnerab*"
]

# Convert wildcard terms to regex patterns
def wildcard_to_regex(pattern):
    # Escape other regex chars, then replace * with .*
    return re.compile(r"\b" + re.escape(pattern).replace(r"\*", ".*") + r"\b", re.IGNORECASE)

# Create list of regex patterns
regex_patterns = [wildcard_to_regex(k) for k in keywords]

# === Load Excel file ===
df = pd.read_excel(input_file, sheet_name=sheet_name)

# Fill NaNs in case of missing abstracts or titles
df[title_col] = df[title_col].fillna("")
df[abstract_col] = df[abstract_col].fillna("")

# Function to scan text for any pattern match
def match_patterns(text):
    return any(p.search(text) for p in regex_patterns)

# Apply to each row
df['Match_Title'] = df[title_col].apply(match_patterns)
df['Match_Abstract'] = df[abstract_col].apply(match_patterns)
df['Match_Either'] = df['Match_Title'] | df['Match_Abstract']

# Optionally filter to only matched rows
matched_df = df[df['Match_Either']]

# === Save output ===
output_file = "scopus_matches.xlsx"
matched_df.to_excel(output_file, index=False)

print(f"Matched rows saved to: {output_file}")