import pickle
with open("statements.txt", "r",encoding= "utf-8") as file:
    statements_text = file.read()


# Split the text into lines
lines = statements_text.split("\n")

# Initialize empty dictionaries for Verdadeiro and Falso statements
verdadeiro_statements = {}
falso_statements = {}

# Initialize the current category as None
current_category = None

# Iterate over the lines
for line in lines:
    # If the line is "Verdadeiro" or "Falso", update the current category
    if line == "Verdadeiro":
        current_category = verdadeiro_statements
    elif line == "Falso":
        current_category = falso_statements
    # If the line is not empty and we have a current category, add the line to the category
    elif line and current_category is not None:
        current_category[line] = True if current_category == verdadeiro_statements else False

# Combine the two dictionaries
all_statements = {**verdadeiro_statements, **falso_statements}

print(all_statements)

# Save the dictionary to a file
with open("statements_dict.pkl", "wb") as file:
    pickle.dump(all_statements, file)
