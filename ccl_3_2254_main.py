### Write a code detect instances of unique keywords
# no of total keywords
# no of each specific keywords
# Print int keyword if present in print function string literal keyword ignore


import re

c_keywords = {'int','float','double','for','do','while','return','case','default','void','if','else','break'}

input_file = r"THIRD_LAB\ccl_3_2254_input.c"
output_file = r"THIRD_LAB\ccl_3_2254_output.c"

with open(input_file, 'r') as f:
    c_code = f.read()

# Remove multi-line comments /* ... */
code_no_multi = re.sub(r'/\*.*?\*/', '', c_code, flags=re.DOTALL)
# clear cmnt
c_code_no_cmnt = re.sub(r'//.*','', code_no_multi)


with open(output_file, 'w') as f:
    f.write(c_code_no_cmnt)
    
## --------------------------------------------------------------------------------
## --------------------------------------------------------------------------------

## remove string literals
code_wo_string = re.sub(r'"(\\.|[^"\\])*"', '',c_code_no_cmnt)

words = re.findall(r'\b[a-zA-Z_]\w*\b', code_wo_string)
keyword_count = {}
for word in words:
    if word in c_keywords:
        keyword_count[word] = keyword_count.get(word, 0)+1


print("Total unique keywords found", len(keyword_count))
print("Total  keywords occurences", sum(keyword_count.values()))
print("\n each keyword count")
for kw, count in sorted(keyword_count.items()):
    print(f"{kw}:{count}")





