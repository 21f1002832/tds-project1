#Task A6
def extract_h1_and_create_index(input_dir: str, output_file: str):
    try:
        # Get all .md files in the directory and its subdirectories
        md_files = glob.glob(os.path.join(input_dir, "**", "*.md"), recursive=True)
        
        # Initialize the index dictionary
        index = {}
        
        for md_file in md_files:
            with open(md_file, "r") as file:
                # Read the file line by line
                for line in file:
                    # Check if the line starts with # (H1)
                    if line.startswith("# "):
                        # Extract the title (remove the # and leading/trailing whitespace)
                        title = line.lstrip("# ").strip()
                        # Get the relative path of the file (without the input_dir prefix)
                        relative_path = os.path.relpath(md_file, input_dir)
                        # Add the file and its title to the index
                        index[relative_path] = title
                        # Move to the next file after finding the first H1
                        break
        
        # Sort the index by keys (relative file paths)
        #sorted_index = dict(sorted(index.items()))  # Sort dictionary by keys

        # Sort case-insensitively
        #sorted_index = dict(sorted(index.items(), key=lambda item: item[0].lower())) #The crucial change

        # Write the index to the output file
        with open(output_file, "w", encoding="utf-8") as file:
            #index.sort()
            json.dump(index, file, indent=2)
        
        return {"success": True, "message": f"Created an index file {output_file} that maps each filename to its title"}
    
    except Exception as e:
        return {"success": False, "message": str(e)}


#Task A9
async def similar_comments(input_file: str, output_file: str):
    try:
        with open(input_file, "r") as file:
            comments = file.readlines()

        comments = [comment.strip() for comment in comments]

        batch_size = 20  # Adjust batch size as needed (start with 20, test and increase)
        all_embeddings = []

        for i in range(0, len(comments), batch_size):
            batch = comments[i:i + batch_size]
            embeddings = await get_embeddings(batch) # Await the batch call
            all_embeddings.extend(embeddings)

        embeddings = np.array(all_embeddings)
        
        # Compute pairwise cosine similarity
        similarity_matrix = cosine_similarity(embeddings)
        
        # Find the most similar pair (excluding self-similarity)
        np.fill_diagonal(similarity_matrix, -1)  # Ignore self-similarity
        most_similar_indices = np.unravel_index(np.argmax(similarity_matrix), similarity_matrix.shape)
        
        # Get the most similar pair of comments
        comment1 = comments[most_similar_indices[0]]
        comment2 = comments[most_similar_indices[1]]
        
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


async def get_embeddings(texts: list[str]):  # Accepts a list of texts (batch)
    """Get embeddings for a batch of texts."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(
                "https://aiproxy.sanand.workers.dev/openai/v1/embeddings",
                headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjEwMDI4MzJAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.fVUsbTxVaaoRL7t6712xBmWPDJQ4atPmkd49BfdWVog"},  # Replace with your token
                json={"model": "text-embedding-3-small", "input": texts},  # Send a list of texts (batch)
                timeout=60.0 # Or an appropriate timeout
            )
            response.raise_for_status() # Check for HTTP errors
            return [data["embedding"] for data in response.json()["data"]]  # Extract embeddings
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP Error: {e}")
            raise  # Re-raise the exception to be handled by the caller
        except httpx.TimeoutException as e:
            logging.error(f"Timeout Error: {e}")
            raise
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise