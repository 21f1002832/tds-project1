#tools.py

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_uv_script",
            "description": "Install uv (if required) and run datagen.py with email as the only argument",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "Email address to pass as an argument to the script."}
                },
                "required": ["email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "format_file",
            "description": "Format a markdown file using Prettier",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the markdown file to be formatted using Prettier."}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "count_weekdays",
            "description": "Count the number of specific weekdays in a file and write the count to an output file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file containing dates."},
                    "weekday": {"type": "string", "description": "The weekday to count (e.g., Monday, Tuesday, etc.)."},
                    "output_path": {"type": "string", "description": "Path to the output file where the count will be written."}
                },
                "required": ["file_path", "weekday", "output_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sort_contacts",
            "description": "Sort JSON data by specified keys in specified order and write the result to an output file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Path to the file containing unsorted contacts."},
                    "output_file": {"type": "string", "description": "Path to the output file where the sorted result will be written."},
                    "keys": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of keys to sort by in specified order"
                    }
                },
                "required": ["input_file", "output_file", "keys"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_recent_logs",
            "description": "Write the first line of the required number of most recent .log file in given input file to specified output file, most recent first",
            "parameters": {
                "type": "object",
                "properties": {
                    "log_dir": {"type": "string", "description": "Input directory containing all .log files."},
                    "num_files": {"type": "integer", "description": "Count of most recent .log files"},
                    "output_file": {"type": "string", "description": "Output file where the result will be written."}
                },
                "required": ["input_file","num_files", "output_file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_markdown_headers",
            "description": "Find all Markdown (.md) files in given input directory. For each file, extract the first occurrance of each H1 (i.e. a line starting with # ). Create an index file from specified output file path that maps each filename (without the input directory prefix) to its title",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_dir": {"type": "string", "description": "Input directory containing all .md files."},
                    "output_file": {"type": "string", "description": "Output file where the result will be written."}
                },
                "required": ["input_dir", "output_file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_email_eddress",
            "description": "Given input file contains an email message. Parse it's content and extract the sender's email address, and write it to specified output file",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Input file containing the email message."},
                    "output_file": {"type": "string", "description": "Output file where the result(sender’s email address) will be written."}
                },
                "required": ["input_file", "output_file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_credit_card_no",
            "description": "Given input file contains a long series of numbers. Parse the image and extract those long series of numbers, and write it without spaces to specified output file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Input image containing useful text data"},
                    "output_file": {"type": "string", "description": "Output file where the result will be written."}
                },
                "required": ["input_file", "output_file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "similar_comments",
            "description": "Given input file contains a list of comments, one per line. Using embeddings, find the most similar pair of comments and write them to specified output file, one per line",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Input file containing a list of comments, one per line"},
                    "output_file": {"type": "string", "description": "Output file where the result will be written."}
                },
                "required": ["input_file", "output_file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_gold_sales",
            "description": "Given SQLite database file has a tickets with columns type, units, and price. Each row is a customer bid for a concert ticket. What is the total sales of all the items in the “Gold” ticket type? Write the number in output file",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Input SQLite database file"},
                    "output_file": {"type": "string", "description": "Output file where the result will be written."}
                },
                "required": ["input_file", "output_file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "never_delete",
            "description": "Look for keywords like delete/Delete and a given file which is specified for deletion",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "File requested for deletion"}
                },
                "required": ["file"]
            }
        }
    }          
]