from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
import json
import uvicorn

from tools import tools  # Import tools list
from functions import *  # Import all the functions
from query_gpt import query_gpt # Import query_gpt function

# Set up logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/read")
async def read_file(path: str):
    path = normalize_path(path)
    if os.path.exists(path):
        try:
            with open(path, 'r') as file:
                content = file.read()
            return PlainTextResponse(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail="File not found.")

@app.post("/run", response_model=dict)
async def run_task(task: str = Query(..., description="User query to be processed by OpenAI")):
    gpt_response = query_gpt(task, tools)
    if "tool_calls" in gpt_response:
        tool_call = gpt_response["tool_calls"][0]
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])

        #Task: A1
        if function_name == "run_uv_script":
            email = arguments.get("email")
            return run_uv_script(email)
        
        #Task: A2
        elif function_name == "format_file":
            filepath = normalize_path(arguments.get("filepath"))

            if filepath and os.path.exists(filepath):
                return format_file(filepath)
            else:
                return {"success": False, "message": f"File {filepath} does not exist."}

        #Task: A3
        elif function_name == "count_weekdays":
            file_path = normalize_path(arguments.get("file_path"))
            weekday = arguments.get("weekday")
            output_path = normalize_path(arguments.get("output_path"))

            if file_path and weekday or output_path:
                return count_weekdays(file_path, weekday, output_path)
            else:
                return {"success": False, "message": "Missing required parameters."}
        
        #Task: A4
        elif function_name == "sort_contacts":
            input_file = normalize_path(arguments.get("input_file"))
            output_file = normalize_path(arguments.get("output_file"))
            keys = arguments.get("keys")

            if input_file and output_file and keys:
                return sort_contacts(input_file, output_file, keys)
            else:
                return {"success": False, "message": "Missing required parameters."}
            
        #Task: A5
        elif function_name == "write_recent_logs":
            log_dir = normalize_path(arguments.get("log_dir"))
            num_files = arguments.get("num_files")
            output_file = normalize_path(arguments.get("output_file"))

            if log_dir and output_file and num_files:
                return write_recent_logs(log_dir, output_file, num_files)
            else:
                return {"success": False, "message": "Missing required parameters."}
        
        #Task: A6
        elif function_name == "extract_markdown_headers":
            input_dir = normalize_path(arguments.get("input_dir"))
            output_file = normalize_path(arguments.get("output_file"))

            if input_dir and output_file:
                return extract_markdown_headers(input_dir, output_file)
            else:
                return {"success": False, "message": "Missing required parameters."}
            
        #Task: A7
        elif function_name == "write_email_eddress":
            input_file = normalize_path(arguments.get("input_file"))
            output_file = normalize_path(arguments.get("output_file"))

            if input_file and output_file:
                return write_email_eddress(input_file, output_file)
            else:
                return {"success": False, "message": "Missing required parameters."}
            
        #Task: A8
        elif function_name == "write_credit_card_no":
            input_file = normalize_path(arguments.get("input_file"))
            output_file = normalize_path(arguments.get("output_file"))

            if input_file and output_file:
                return write_credit_card_no(input_file, output_file)
            else:
                return {"success": False, "message": "Missing required parameters."}
            
        #Task: A9
        elif function_name == "similar_comments":
            input_file = normalize_path(arguments.get("input_file"))
            output_file = normalize_path(arguments.get("output_file"))

            if input_file and output_file:
                result = await similar_comments(input_file, output_file) # Await here!
                return result # Return the awaited result
            else:
                return {"success": False, "message": "Missing required parameters."}
        
        #Task: A10
        elif function_name == "calculate_gold_sales":
            input_file = normalize_path(arguments.get("input_file"))
            output_file = normalize_path(arguments.get("output_file"))

            if input_file and output_file:
                return calculate_gold_sales(input_file, output_file)
            else:
                return {"success": False, "message": "Missing required parameters."}
            
        #Task: B2    
        elif function_name == "never_delete":
            #file = normalize_path(arguments.get("file"))
            raise HTTPException(status_code=400, detail="Deletion of data is not permitted anywhere on the file system")

    return {"error": "Could not determine the appropriate function"}


if __name__ == '__main__':
    uvicorn.run(app,reload=True)