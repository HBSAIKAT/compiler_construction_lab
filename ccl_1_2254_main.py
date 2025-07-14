# Open and read the input file
with open('ccl_1_2254_input.c', 'r') as input_file:
    content = input_file.read()

# Write the content to the output file
with open('ccl_1_2254_output.c', 'w') as output_file:
    output_file.write(content)

print("File copied successfully from input.c to output.c.")
