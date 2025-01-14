import pandas as pd
from collections import Counter
import spacy
import matplotlib.pyplot as plt
import string

nlp = spacy.load("en_core_web_md")
df = pd.read_csv("AI_TRAINING/tokenized_data.csv")
df['Original Text'] = df['Original Text'].fillna("").astype(str)

stopwords = nlp.Defaults.stop_words

# Function to tokenize text and extract keywords
@staticmethod
def tokenize_and_extract_keywords(text, stopwords, min_freq=1):
    if not isinstance(text, str):  # Check if text is not a string
        print(f"Non-string value encountered: {type(text)}")
        return {}  # Return an empty dictionary if the text is invalid
    
    doc = nlp(text)
    tokens = [token.text.lower() for token in doc if token.text.lower() not in stopwords and token.text not in string.punctuation and token.is_alpha]
    token_freq = Counter(tokens)
    keywords = {token: freq for token, freq in token_freq.items() if freq >= min_freq}
    
    return keywords

# Apply the tokenization to the 'Original Text' column and extract keywords
df['Keywords'] = df['Original Text'].apply(lambda x: tokenize_and_extract_keywords(x, stopwords))

# Display the keywords for the first few rows
print("Keywords extracted for each row:")
print(df[['Text ID', 'Keywords']].head())

# Clean up the "Tokens" column (if it exists, for additional processing)
if "Tokens" in df.columns:
    df["Tokens"] = df["Tokens"].apply(lambda x: x.strip(',').replace(' ,', ',').replace(', ', ',') if isinstance(x, str) else "")

    # Flatten all tokens into a single list
    all_tokens = [token.strip() for tokens in df["Tokens"] for token in tokens.split(",") if token.strip() != ""]
    
    print(f"Total number of tokens: {len(all_tokens)}")
    print(f"First few tokens: {all_tokens[:10]}")

    token_frequency = Counter(all_tokens)
    print(f"Total unique tokens: {len(token_frequency)}")
    print(f"Most common tokens: {token_frequency.most_common(5)}")

    # Convert to a DataFrame for easier visualization
    token_freq_df = pd.DataFrame(token_frequency.items(), columns=["Token", "Frequency"])

    # Remove punctuation using SpaCy tokenizer
    punctuation_tokens = {token.text for token in nlp(".".join(all_tokens)) if token.is_punct}
    token_freq_df = token_freq_df[~token_freq_df["Token"].isin(punctuation_tokens)]

    token_freq_df["Frequency"] = pd.to_numeric(token_freq_df["Frequency"], errors="coerce")
    token_freq_df = token_freq_df.sort_values(by="Frequency", ascending=False)

    print(f"Token Frequency DataFrame shape: {token_freq_df.shape}")
    print(token_freq_df.head())

    # Plot the top 20 most frequent tokens
    if not token_freq_df.empty:
        token_freq_df.head(20).plot(kind="bar", x="Token", y="Frequency", figsize=(10, 6))
        plt.title("Top 20 Most Frequent Tokens")
        plt.xlabel("Token")
        plt.ylabel("Frequency")
        plt.show()
    else:
        print("Token Frequency DataFrame is empty. Cannot plot.")
else:
    print("No 'Tokens' column found. Please check the CSV file.")

# Check for missing values in 'Original Text' column and print out its values
print("Checking 'Original Text' column:")
print(df['Original Text'].head())

# Ensure the 'Keywords' column is converted to a string before exporting
df['Keywords'] = df['Keywords'].apply(lambda x: str(x))

# Export the DataFrame to a CSV file
output_file = "AI_TRAINING/keywords_extracted.csv"
df.to_csv(output_file, index=False)

print(f"Data exported successfully to {output_file}")