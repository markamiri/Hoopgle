def remove_rk_rows(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    with open(output_file, 'w') as file:
        for line in lines:
            # Split the line by whitespace and check if the first element is "Rk"
            if line.split()[0] != "Rk":
                file.write(line)

# Example usage
input_file = 'output.txt'
output_file = 'cleaned_output.txt'  # You can overwrite the same file if needed
remove_rk_rows(input_file, output_file)