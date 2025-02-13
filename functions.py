#functions.py

import os
import subprocess
import json
from datetime import datetime
import logging
import glob
from fastapi import HTTPException
import numpy as np
import requests 
from sklearn.metrics.pairwise import cosine_similarity

from query_gpt import *

def normalize_path(path):
    path = path.lstrip('/') if not os.path.exists(path) else path
    if not path.startswith('data'):
        raise HTTPException(status_code=400, detail="Path must reside within the /data directory.")  # Bad Request
    return path

#Task A1
def run_uv_script(email: str):
    try:
        # Install uv (ignore errors if already installed)
        subprocess.run(["pip", "install", "uv"], check=False)

        # Run the script and capture output
        result = subprocess.run(
            ["uv", "run", "datagen.py", email, "--root", "./data"],
            check=True,
            capture_output=True,  # Capture stdout and stderr
            text=True             # Return output as a string
        )
        return {"success": True, "message": result.stdout or "Script executed successfully."}

    except Exception as e:
        return {"success": False, "message": str(e)}

#Task A2
def format_file(filepath):
        try:
            result = subprocess.run(
                ["npx", "prettier@3.4.2", "--write", filepath],
                check=False,  # Don't raise exception automatically
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"success": False, "message": f"Prettier write failed: {result.stderr}"}
            
            return {"success": True, "message": result.stdout}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
#Task A3
from datetime import datetime
def count_weekdays(file_path: str, weekday: str, output_path: str):
    date_formats = ["%Y/%m/%d %H:%M:%S", "%b %d, %Y", "%Y-%m-%d", "%d-%b-%Y"]
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_index = weekdays.index(weekday)
    count=0

    # Read and process the dates
    with open(file_path, "r") as file:
        for line in file:
            date_str = line.strip()
            for fmt in date_formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    if date_obj.weekday() == weekday_index:
                        count += 1
                except ValueError:
                    # Skip invalid date formats
                    continue

    with open(output_path, 'w') as output_file:
        output_file.write(str(count))

    return {"success": True, "message": f"Counted {count} occurrences of '{weekday.capitalize()}' in {file_path}."}

#Task A4
def sort_contacts(input_file: str, output_file: str, keys: list):
    try:
        with open(input_file, 'r') as f:
            contacts = json.load(f)

        sorted_data = sorted(contacts, key=lambda x: tuple(x[key] for key in keys))

        with open(output_file, 'w') as f:
            json.dump(sorted_data, f, indent=2)

        return {"success": True, "message": f"Sorted contacts from {input_file} and saved to {output_file}"}

    except FileNotFoundError:
        return {"success": False, "message": f"File {input_file} not found."}
    except Exception as e:
        return {"success": False, "message": str(e)}

#Task A5
def write_recent_logs(log_dir, output_file, num_files):
    try:
        # 1. Find all .log files in the directory
        log_files = glob.glob(os.path.join(log_dir, "*.log"))

        # 2. Sort files by modification time (most recent first)
        log_files.sort(key=os.path.getmtime, reverse=True)

        # 3. Take the top 'num_files' most recent files
        recent_log_files = log_files[:num_files]

        # 4. Write the first line of each file to the output file
        with open(output_file, 'w') as outfile:
            for log_file in recent_log_files:
                try:
                    with open(log_file, 'r') as infile:
                        first_line = infile.readline().strip()  # Read and strip leading/trailing whitespace
                        outfile.write(f"{first_line}\n") #Include file name
                except Exception as e:
                    logging.error(f"Error reading file {log_file}: {e}")
                    outfile.write(f"Error reading file {log_file}\n")  # Write an error message

        return {"success": True, "message": f"Wrote first lines of {num_files} recent log files to {output_file}"}

    except Exception as e:
        return {"success": False, "message": str(e)}

#Task A6
import re
def extract_markdown_headers(input_dir: str, output_file: str):
    headers_dict = {}

    try:
        # Recursively find all Markdown files in subdirectories
        md_files = []
        for subdir, dirs, files in os.walk(input_dir):
            for file in files:
                if file.endswith(".md"):
                    md_files.append(os.path.join(subdir, file))

        if not md_files:
            raise HTTPException(status_code=404, detail="No Markdown files found in /data/docs/")

        # Extract the first H1 header from each Markdown file
        for md_file in md_files:
            with open(md_file, "r", encoding="utf-8") as file:
                for line in file:
                    match = re.match(r"^# (.+)", line.strip())  # Find the first H1 header
                    if match:
                        # Remove /data/docs/ prefix and add to the dictionary
                        relative_file_path = os.path.relpath(md_file, input_dir)
                        headers_dict[relative_file_path] = match.group(1)
                        break  # Stop after the first H1

        # Save extracted headers to index.json
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(headers_dict, file, indent=4)
        return {"success": True, "message": "Extracted H1 headers & from Markdown files. Saved to {output_file}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#Task A7
def write_email_eddress(input_file: str, output_file: str):
    try:
        with open(input_file, "r") as email_file:
            email_content = email_file.read()

        gpt_response = query_llm(
            f"""
            Extract the sender's email address from the following email message:

            ```
            {email_content}
            ```

            Write *only* the sender's email address to the output file.  Do not include any other text or explanations.
            """
        )

        if "error" in gpt_response:
            return {"success": False, "message": gpt_response["error"]} #Return error from query_gpt

        extracted_content = gpt_response.get("content").strip() #Handle cases where 'content' is missing

        with open(output_file, "w") as outfile:
            outfile.write(extracted_content)

        return {"success": True, "message": f"Sender's email address is successfully extracted & written to {output_file}."}
    
    except FileNotFoundError:
        return {"success": False, "message": f"Email file not found at {input_file}"}
    except Exception as e:
        return {"success": False, "message": f"An error occurred: {e}"}
    
def query_llm(prompt: str) -> Dict[str, Any]:  # New function for task A7 [extracting & writing email address]
    try:
        request_data = {
            "model": "gpt-4o-mini",  # Or your preferred model
            "messages": [{"role": "user", "content": prompt}],
        }

        print("Request Data:", json.dumps(request_data, indent=2))  # Print the request

        response = httpx.post(
            AI_PROXY_URL,
            headers={
                "Authorization": f"Bearer {AI_PROXY_TOKEN}",
                "Content-Type": "application/json",
            },
            json=request_data,timeout=10.0
        )
        response.raise_for_status() #Raise HTTPError for bad responses (4xx or 5xx)
        response_data = response.json()
        logging.info(f"GPT API Response: {json.dumps(response_data, indent=2)}")

        if "choices" not in response_data or not response_data["choices"]:
            return {"error": "Invalid response from API"}

        return response_data["choices"][0]["message"]

    except Exception as e:
        logging.error(f"Error querying GPT: {str(e)}")
        return {"error": f"An unexpected error occurred: {e}"}
    
#Task A8
import base64
def write_credit_card_no(input_file: str, output_file: str):
    try:
        with open(input_file, "rb") as img_file:
            base64_string = base64.b64encode(img_file.read()).decode('utf-8')
            base64_url = f"data:image/png;base64,{base64_string}"

        request_data = {
            "model": "gpt-4o-mini",  
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract and print only the long series of numbers (16 digits), without any spaces from the image",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": base64_url},
                        },
                    ],
                }
            ],
        }

        response = httpx.post(
            AI_PROXY_URL,
            headers={
                "Authorization": f"Bearer {AI_PROXY_TOKEN}",
                "Content-Type": "application/json",
            },
            json=request_data,
            timeout=60.0  # Set timeout
        )
        response.raise_for_status() #Raise HTTPError for bad responses (4xx or 5xx)
        response_data = response.json()
        logging.info(f"GPT API Response: {json.dumps(response_data, indent=2)}")

        if "choices" not in response_data or not response_data["choices"]:
            return {"error": "Invalid response from API"}

        # Correct extraction from response_data:
        extracted_no = response_data["choices"][0]["message"].get("content", "Credit card number not found").strip()

        with open(output_file, "w") as outfile:
            outfile.write(extracted_no)
        
        return {"success": True, "message": f"Credit card number {extracted_no} is successfully extracted & written to {output_file}."} 
    
    except Exception as e:
        logging.error(f"Error querying GPT: {str(e)}")
        return {"error": f"An unexpected error occurred: {e}"}

#Task A9
async def similar_comments(input_file: str, output_file: str):
    try:
        with open(input_file, "r") as file:
            data = file.readlines()

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://aiproxy.sanand.workers.dev/openai/v1/embeddings",
                headers={"Authorization": f"Bearer {AI_PROXY_TOKEN}"},  # Replace with your token
                json={"model": "text-embedding-3-small", "input": data},  # Send list of comments
            )
            response.raise_for_status() # Check for HTTP errors
            embeddings = np.array([emb["embedding"] for emb in response.json()["data"]])
            
            # Compute pairwise cosine similarity
            similarity_matrix = cosine_similarity(embeddings)
            
            # Find the most similar pair (excluding self-similarity)
            np.fill_diagonal(similarity_matrix, -1)  # Ignore self-similarity
            most_similar_indices = np.unravel_index(np.argmax(similarity_matrix), similarity_matrix.shape)
            
            # Get the most similar pair of comments
            comment1 = data[most_similar_indices[0]]
            comment2 = data[most_similar_indices[1]]
            
            if comment1 and comment2:
                # Write the pair to the output file
                with open(output_file, "w") as file:
                    file.write(f"{comment1}\n{comment2}")
                return {  # Return a dictionary with more information
                    "success": True,
                    "message": f"Most similar comments written to {output_file}",
                    "most_similar_indices": [int(i) for i in most_similar_indices] # Convert to list for JSON serialization
                }

            else:
                return {"success": True, "message": "No similar comments found"}  # Should not happen, but good to have

    except FileNotFoundError:
        return {"success": False, "message": f"File not found: {input_file}"}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"success": False, "message": f"An error occurred: {e}"} 

#Task A10
import sqlite3

def calculate_gold_sales(db_path: str, output_path: str):
    """Calculates total sales for 'Gold' tickets and writes to output file."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
        result = cursor.fetchone()[0]

        total_sales = result if result is not None else 0  # Handle cases where no Gold tickets exist

        with open(output_path, "w") as outfile:
            outfile.write(str(total_sales))

        conn.close()
        return {"success": True, "message": f"Total Gold ticket sales: {total_sales}"}

    except sqlite3.Error as e:
        return {"success": False, "message": f"Database error: {e}"}
    except Exception as e:
        return {"success": False, "message": f"An error occurred: {e}"}