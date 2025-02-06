import os
import pandas as pd
import google.generativeai as genai
import time
from google.api_core.exceptions import ResourceExhausted


api_key = ''
genai.configure(api_key=api_key)

model_name = "gemini-1.5-flash"
model = genai.GenerativeModel(model_name=model_name)
print("Gemini model configured.")

file_path = '/mnt/sdrive/likai/code/allprompt.csv'
output_file_path = '/mnt/sdrive/likai/Gemini/1.5_allprompt_answers.csv'

# Reading CSV Files
df = pd.read_csv(file_path)

language_columns = ['en', 'zh-cn', 'hi', 'ko', 'th', 'bn', 'jw', 'si']

max_retries = 3  
retry_delay = 30  

# Writing to CSV file in real time
for lang in language_columns:
    if f'{lang}-answer' not in df.columns:
        df[f'{lang}-answer'] = ""
    for i in range(len(df)):
        prompt = df[lang][i]
        retries = 0
        success = False
        while retries < max_retries:
            try:
                response = model.generate_content(prompt)
                # Extract text content
                text_content = response.result.candidates[0].content.parts[0].text
                df.at[i, f'{lang}-answer'] = text_content
                print(f"Processed {lang} prompt for row {i}")
                success = True
                break  
            except Exception as e:  
                retries += 1
                if retries >= max_retries:
                    print(f"Skipping row {i} for {lang} after {max_retries} retries due to error: {e}")
                    df.at[i, f'{lang}-answer'] = f"Error: Failed after multiple retries due to {e}"
                else:
                    print(f"Error encountered: {e}. Retrying {retries}/{max_retries}...")
                    time.sleep(retry_delay)  

        if not success and retries >= max_retries:
            df.at[i, f'{lang}-answer'] = "Error: Failed after multiple retries"
            print(f"Failed to generate response for row {i} after {max_retries} retries.")
        elif not success:
            df.at[i, f'{lang}-answer'] = "No response generated"

        # Write to CSV file
        df.to_csv(output_file_path, index=False)
        print(f"Saved progress to {output_file_path} after processing row {i} for {lang}")

print("All answers updated and saved to file.")

