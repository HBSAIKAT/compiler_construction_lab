
from collections import defaultdict

EPSILON = 'ε'  # used for empty remainder if needed

def detect_left_recursion_and_parse(rules_lines):
    print("\n--- Left Recursion Detection Result ---")
    left_recursive_count = 0
    parsed_rules = []

    for rule in rules_lines:
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
    return parsed_rules, left_recursive_count

class _TrieNode:
    def __init__(self):
        self.children = {}
        self.prods = []

def _choose_char_mode(productions):
    for p in productions:
        if ' ' in p:
            return False  # use space-tokenization
    return True  # use char-tokenization

def _tokenize(prod, char_mode):
    pt = prod.strip()
    if pt == '' or pt == EPSILON:
        return []
    return list(pt) if char_mode else pt.split()

def _build_trie(productions, char_mode):
    root = _TrieNode()
    for p in productions:
        tokens = _tokenize(p, char_mode)
        node = root
        node.prods.append(p)
        for t in tokens:
            if t not in node.children:
                node.children[t] = _TrieNode()
            node = node.children[t]
            node.prods.append(p)
    return root

def _collect_maximal_prefixes(root):
    results = []
    def dfs(node, path):
        child_has_group = False
        for tok, child in node.children.items():
            dfs(child, path + [tok])
            if len(child.prods) >= 2:
                child_has_group = True
        if len(node.prods) >= 2 and not child_has_group and path:
            results.append((path, list(node.prods)))
    dfs(root, [])
    return results

def detection_left_factoring(parsed_rules):
    print("\n--- Left Factoring Detection Result ---")
    factoring_map = {}
    total_groups = 0

    for nt, prods in parsed_rules:
        if len(prods) < 2:
            print(f"{nt} has no left factoring.")
            continue
        char_mode = _choose_char_mode(prods)
        root = _build_trie(prods, char_mode)
        groups = _collect_maximal_prefixes(root)
        if groups:
            factoring_map[nt] = (char_mode, groups)
            print(f"{nt} has {len(groups)} left factoring group(s):")
            for idx, (prefix, group_prods) in enumerate(groups, start=1):
                total_groups += 1
                pref_s = ''.join(prefix) if char_mode else ' '.join(prefix)
                print(f"  Group {idx}: common prefix -> '{pref_s}'")
                for gp in group_prods:
                    print(f"    {nt} -> {gp}")
        else:
            print(f"{nt} has no left factoring.")
    print(f"\nTotal left factoring groups in grammar: {total_groups}")
    return factoring_map, total_groups

def _unique_new_nt(base, existing_set):
    cand = base + "'"
    i = 1
    while cand in existing_set:
        cand = f"{base}_f{i}"
        i += 1
    existing_set.add(cand)
    return cand

def _detect_no_print(grammar_items):
    factoring_map = {}
    total_groups = 0
    for nt, prods in grammar_items:
        if len(prods) < 2:
            continue
        char_mode = _choose_char_mode(prods)
        root = _build_trie(prods, char_mode)
        groups = _collect_maximal_prefixes(root)
        if groups:
            factoring_map[nt] = (char_mode, groups)
            total_groups += len(groups)
    return factoring_map, total_groups

def removal_left_factoring(parsed_rules):
    grammar = {nt: list(prods) for nt, prods in parsed_rules}
    existing_nts = set(grammar.keys())

    while True:
        factoring_map, total_groups = _detect_no_print(list(grammar.items()))
        if total_groups == 0:
            break
        for nt in list(grammar.keys()):
            if nt not in factoring_map:
                continue
            char_mode, groups = factoring_map[nt]
            for prefix_tokens, group_prods in groups:
                current_prods = grammar.get(nt, [])
                to_factor = [p for p in current_prods if p in group_prods]
                if len(to_factor) < 2:
                    continue

                new_nt = _unique_new_nt(nt, existing_nts)

                new_nt_prods = []
                for p in to_factor:
                    tokens = _tokenize(p, char_mode)
                    if len(tokens) >= len(prefix_tokens) and tokens[:len(prefix_tokens)] == prefix_tokens:
                        remainder = tokens[len(prefix_tokens):]
                    else:
                        remainder = tokens
                    if remainder:
                        remainder_str = ''.join(remainder) if char_mode else ' '.join(remainder)
                        new_nt_prods.append(remainder_str)
                    else:
                        new_nt_prods.append(EPSILON)

                if char_mode:
                    prefix_str = ''.join(prefix_tokens)
                    new_form = prefix_str + new_nt
                else:
                    prefix_str = ' '.join(prefix_tokens)
                    new_form = (prefix_str + ' ' + new_nt).strip()

                updated = [p for p in current_prods if p not in to_factor]
                if new_form not in updated:
                    updated.append(new_form)
                grammar[nt] = updated

                seen = set()
                deduped = []
                for x in new_nt_prods:
                    if x not in seen:
                        deduped.append(x)
                        seen.add(x)
                grammar[new_nt] = deduped

    print("\n--- Grammar after left factoring removal ---")
    final_rules = []
    for nt, prods in grammar.items():
        print(f"{nt} -> " + " | ".join(prods))
        final_rules.append((nt, prods))
    return final_rules

# --------------------
# INPUT SECTION & main flow
# --------------------
if __name__ == "__main__":
    n = int(input("Enter number of rules: "))
    rules = []
    for _ in range(n):
        rules.append(input())

    parsed_rules, left_recursive_count = detect_left_recursion_and_parse(rules)

    factoring_map, total_fact_groups = detection_left_factoring(parsed_rules)

    if total_fact_groups > 0:
        final_grammar = removal_left_factoring(parsed_rules)
    else:
        print("\nNo left factoring groups found; grammar unchanged after factoring pass.")
        final_grammar = parsed_rules

    print("\n--- All transformations complete ---")
