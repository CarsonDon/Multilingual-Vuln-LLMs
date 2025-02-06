
import pandas as pd
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


client = OpenAI(api_key='')


file_path = '/mnt/sdrive/likai/code/allprompt.csv'
df = pd.read_csv(file_path)

# Define the language columns that need to be processed
language_columns = ['en', 'zh-cn', 'hi', 'ko', 'th', 'bn', 'jw', 'si']

# Process a single prompt and return an answer, updating the file at the same time
def fetch_and_write_answer(row, lang):
    index = row.name
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": row[lang]},
            ],
            max_tokens=200,
            n=1,
            temperature=0.7
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error processing prompt for {lang} at index {index}: {e}")
        answer = "Error"
    
    # Updating a DataFrame
    df.at[index, f'{lang}-answer'] = answer

    # Single row update to CSV file
    df.loc[[index]].to_csv(output_file_path, mode='a', header=not output_file.exists(), index=False)
    print(f"Processed and written prompt for {lang} at index {index} successfully.")

# Set the output file path
output_file_path = '/mnt/sdrive/likai/gpt/all3.5A.csv'
output_file = Path(output_file_path)

# Clear existing files
if output_file.exists():
    output_file.unlink()

# Use thread pool to process requests in parallel
with ThreadPoolExecutor() as executor:
    for lang in language_columns:
        df[f'{lang}-answer'] = ''
        list(executor.map(lambda row: fetch_and_write_answer(row, lang), df.itertuples()))

print("All answers processed and written to the file.")
