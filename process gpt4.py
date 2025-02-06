import os
import pandas as pd
from openai import OpenAI


client = OpenAI(api_key='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')


file_path = '/mnt/sdrive/likai/code/allprompt.csv'
df = pd.read_csv(file_path)

# Define the language columns that need to be processed
language_columns = ['en', 'zh-cn', 'hi', 'ko', 'th', 'bn', 'jw', 'si']

# Generate answers for each language and store in new columns
for lang in language_columns:
    answer_column = f'{lang}-answer'
    df[answer_column] = ""
    for index, row in df.iterrows():
        prompt = row[lang]
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                n=1,
                temperature=0.7
            )
            answer = response.choices[0].message.content.strip()
            df.at[index, answer_column] = answer
            
            # Output processing progress
            print(f"Processed prompt for {lang} at index {index} successfully.")

        except Exception as e:
            print(f"Error processing prompt for {lang} at index {index}: {e}")
            df.at[index, answer_column] = "Error"

    # Output progress per language
    print(f"Finished processing all prompts for language: {lang}")

# Write the results back to a CSV file
output_file_path = '/mnt/sdrive/likai/gpt/all_4A.csv'
df.to_csv(output_file_path, index=False)

print(f"All answers written to {output_file_path}")

