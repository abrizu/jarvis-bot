import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from config import *

def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f"CSV file loaded successfully. Number of rows: {len(df)}")
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        sys.exit(1)

# Function to configure GenAI and process text
def configure_and_generate_text(df):
    try:
        # Configure GenAI with API Key
        genai.configure(api_key="GENAI_TOKEN_ID")  # Replace with your actual token ID

        # Initialize the model
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Prepare the data for inference (using 'Original Text' column)
        texts = df['Original Text'].tolist()
        generated_texts = []

        for text in texts:
            # Run inference for each text entry
            response = model.generate(prompt=text, max_tokens=100)  # Adjust parameters as needed
            generated_texts.append(response['text'])  # assuming 'text' is the key for the generated response

        # Add the generated texts to the DataFrame
        df['Generated Text'] = generated_texts
        print("Generated text has been added to the DataFrame.")

        return df
    except Exception as e:
        print(f"Error configuring GenAI or generating text: {e}")
        sys.exit(1)

# Function to save the results to a new CSV file
def save_to_csv(df, output_file):
    try:
        df.to_csv(output_file, index=False)
        print(f"Output saved to {output_file}")
    except Exception as e:
        print(f"Error saving CSV: {e}")
        sys.exit(1)

# Main function to run the script
def main():
    # Path to your input CSV file
    input_csv = "AI_TRAINING/keywords_extracted.csv"  # Replace with your actual file path

    # Load the CSV
    df = load_csv(input_csv)

    # Generate new text using GenAI
    df_with_generated_text = configure_and_generate_text(df)

    # Save the updated CSV
    save_to_csv(df_with_generated_text, "generated_output.csv")  # Output CSV name

if __name__ == "__main__":
    main()