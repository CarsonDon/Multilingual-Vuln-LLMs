import os
import pandas as pd
import google.generativeai as genai
import time
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from google.api_core.exceptions import ResourceExhausted


class PreProcessor():

    def __init__(self,api_key, Model):
        self.api_key = api_key
        self.source_prompt_path = './prompts/allprompt.csv'
        self.source_prompt_path_demo = './prompts/demo.csv'
        self.answers_path = './answers/'
        self.languages = ['en', 'zh-cn', 'hi', 'ko', 'th', 'bn', 'jw', 'si']
        self.Model = Model


    def get_results_gemini(self, type):
        genai.configure(api_key=self.api_key)
        model_name = "gemini-1.5-flash"
        model = genai.GenerativeModel(model_name=model_name)
        print("Gemini model configured.")

        if type == 'demo':
            file_path = self.source_prompt_path_demo
        else:
            file_path = self.source_prompt_path
        output_file_path = self.answers_path + f'{self.Model}_allprompt_answers.csv'

        # Reading CSV Files
        df = pd.read_csv(file_path)

        language_columns = self.languages

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

        print("All answers updated and saved to Gemini folder.")
        return

    def fetch_and_write_answer(self, row, lang, df, output_file_path, output_file):
        index = row.Index
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

    def get_results_gpt35(self, type):
        client = OpenAI(api_key=self.api_key)
        
        if type == 'demo':
            file_path = self.source_prompt_path_demo
        else:
            file_path = self.source_prompt_path

        df = pd.read_csv(file_path)

        language_columns = self.languages

        # Set the output file path
        output_file_path = self.answers_path + f'{self.Model}_allprompt_answers.csv'
        output_file = Path(output_file_path)

        # Clear existing files
        if output_file.exists():
            output_file.unlink()

        # Use thread pool to process requests in parallel
        with ThreadPoolExecutor() as executor:
            for lang in language_columns:
                df[f'{lang}-answer'] = ''
                list(executor.map(lambda row: self.fetch_and_write_answer(row, lang, df, output_file_path, output_file), df.itertuples()))

        print("All answers processed and written to the file.")
        return

    def get_results_gpt4(self, type):
        client = OpenAI(api_key=self.api_key)

        if type == 'demo':
            file_path = self.source_prompt_path_demo
        else:
            file_path = self.source_prompt_path

        df = pd.read_csv(file_path)

        # Define the language columns that need to be processed
        language_columns = self.languages

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
        output_file_path = self.answers_path + f'{self.Model}_allprompt_answers.csv'
        df.to_csv(output_file_path, index=False)

        print(f"All answers written to {output_file_path}")