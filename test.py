import os
import re

# Directory to save client files
output_dir = "data/"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Regular expression to split each client's data
client_separator = r"\n\n"  # Assumes each client's info is separated by a blank line


def parse_client_data(data):
    """Parse the client's data and return it as a dictionary."""
    client_info = {}
    try:
        for line in data.strip().split("\n"):
            key, value = line.split(": ", 1)
            client_info[key.strip()] = value.strip()
    except ValueError:
        print(f"Error parsing data: {data}")
    return client_info


def save_client_file(client_info):
    """Save each client's info into a file named after them in the output directory."""
    client_name = client_info.get("Nom du Client")
    if not client_name:
        print("Client name not found, skipping...")
        return
    filename = os.path.join(output_dir, f"{client_name}.txt")

    # Write client information to the file
    with open(filename, "w", encoding="utf-8") as file:
        for key, value in client_info.items():
            file.write(f"{key}: {value}\n")


def process_file(input_file):
    """Read the input file, process each client's info, and save each one separately."""
    with open(input_file, "r", encoding="utf-8") as file:
        content = file.read()

    # Split content by each client block
    clients_data = re.split(client_separator, content.strip())

    for client_data in clients_data:
        if client_data.strip():  # Only process non-empty blocks
            client_info = parse_client_data(client_data)
            save_client_file(client_info)
            print(f"Saved file for {client_info.get('Nom du Client')}.")


# Run the script on your input file
input_file = "data/clients.txt"  # Replace with your actual file name
process_file(input_file)
