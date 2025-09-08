n = int(input("Enter number of rules: "))
rules = []

for _ in range(n):
    rules.append(input())

print("\n--- Left Recursion Detection Result ---")
left_recursive_count = 0
parsed_rules = []

for rule in rules:
    parts = rule.split("->")
    non_terminal = parts[0].strip()
    productions = [p.strip() for p in parts[1].split('|')]
    left_recursive_prods = []

    for prod in productions:
        if prod.startswith(non_terminal):
            left_recursive_prods.append(prod)

    if left_recursive_prods:
        print(f"{non_terminal} has {len(left_recursive_prods)} left recursive production(s):")
        for p in left_recursive_prods:
            print(f"{non_terminal} → {p}")
        left_recursive_count += 1
    else:
        print(f"{non_terminal} has no left recursion.")
    parsed_rules.append((non_terminal, productions))

print(f"\nTotal rules with left recursion: {left_recursive_count}")

print("\n--- Left Recursion Removal Result ---")
for non_terminal, productions in parsed_rules:
    left_rec = []
    non_left_rec = []

    for prod in productions:
        if prod.startswith(non_terminal):
            left_rec.append(prod[len(non_terminal):].strip())
        else:
            non_left_rec.append(prod)

    if left_rec:
        new_non_terminal = non_terminal + "'"
        print(f"{non_terminal} ->", end=' ')
        print(' | '.join([p + ' ' + new_non_terminal for p in non_left_rec]), end=' | ε\n')
        print(f"{new_non_terminal} ->", end=' ')
        print(' | '.join([p + ' ' + new_non_terminal for p in left_rec]), end=' | ε\n')
    else:
        print(f"{non_terminal} -> {' | '.join(productions)}")