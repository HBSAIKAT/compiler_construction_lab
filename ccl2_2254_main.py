import re

input_file = r"C:\Users\Admin\Documents\ccl_2254\secondLab\ccl_2_2254_input.c"
output_file = r"C:\Users\Admin\Documents\ccl_2254\secondLab\ccl2_2254_output.c"
with open(input_file, 'r') as f:
    code = f.read()

# Count single-line comments (// ...)
single_line_comments = re.findall(r'//.*', code)
single_line_count = len(single_line_comments)

# Count multi-line comments (/* ... */)
multi_line_comments = re.findall(r'/\*.*?\*/', code,flags=re.DOTALL) 
multi_line_count = len(multi_line_comments)

# Remove multi-line comments
code_no_multi = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL) 
# Remove single-line comments
clean_code = re.sub(r'//.*', '', code_no_multi)

with open(output_file, 'w') as f:
    f.write(clean_code)

print(f"Total single-line comments removed: {single_line_count}")
print(f"Total multi-line comments removed: {multi_line_count}")
print(f"Cleaned code saved to '{output_file}'")
