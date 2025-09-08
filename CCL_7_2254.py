# ----------------------------
# Functions (left recursion + left factoring)
# ----------------------------
from collections import defaultdict

# ---------- Left recursion functions ----------
def detect_left_recursion(rules_lines):
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


def remove_left_recursion(parsed_rules):
    print("\n--- Left Recursion Removal Result ---")
    result_rules = []

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

            main_prods = [ (p + ' ' + new_non_terminal).strip() for p in non_left_rec ] + ['ε']
            new_prods = [ (p + ' ' + new_non_terminal).strip() for p in left_rec ] + ['ε']
            result_rules.append((non_terminal, main_prods))
            result_rules.append((new_non_terminal, new_prods))
        else:
            print(f"{non_terminal} -> {' | '.join(productions)}")
            result_rules.append((non_terminal, productions))

    return result_rules

# ---------- Left factoring functions ----------
EPSILON = 'ε'

class _TrieNode:
    def __init__(self):
        self.children = {}
        self.prods = []

def _choose_char_mode(productions):
    """
    Heuristic:
      - If any production contains a space -> use space-tokenization (return False)
      - Else use character-tokenization (return True)
    This handles mixed styles conservatively (prefers space tokens if present).
    """
    for p in productions:
        if ' ' in p:
            return False
    return True

def _tokenize(prod, char_mode):
    pt = prod.strip()
    if pt == '' or pt == EPSILON:
        return []
    if char_mode:
        # treat each character as a token (good for inputs like iEtS)
        return list(pt)
    else:
        # treat space-separated symbols as tokens (default when user used spaces)
        return pt.split()

def _build_trie_with_mode(productions, char_mode):
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
    """
    Return list of (prefix_tokens_list, [productions...]) for deepest nodes with >=2 prods.
    """
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
    """
    parsed_rules: list of (non_terminal, [productions])
    Returns: factoring_map, total_groups
      factoring_map: {nt: (char_mode, [(prefix_tokens, [productions]), ...])}
    Also prints detection output.
    """
    print("\n--- Left Factoring Detection Result ---")
    factoring_map = {}
    total_groups = 0

    for nt, prods in parsed_rules:
        if len(prods) < 2:
            print(f"{nt} has no left factoring.")
            continue

        char_mode = _choose_char_mode(prods)
        root = _build_trie_with_mode(prods, char_mode)
        groups = _collect_maximal_prefixes(root)
        if groups:
            factoring_map[nt] = (char_mode, groups)
            print(f"{nt} has {len(groups)} left factoring group(s):")
            for idx, (prefix, group_prods) in enumerate(groups, start=1):
                total_groups += 1
                if char_mode:
                    pref_s = ''.join(prefix)
                else:
                    pref_s = ' '.join(prefix)
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

def removal_left_factoring(parsed_rules):
    """
    Removes left factoring iteratively. Uses same tokenization heuristic per nonterminal.
    Prints each transformation and returns the new grammar list [(nt, [prods])].
    """
    print("\n--- Left Factoring Removal Result ---")
    grammar = {nt: list(prods) for nt, prods in parsed_rules}
    existing_nts = set(grammar.keys())

    iteration = 0
    while True:
        iteration += 1
        factoring_map, total_groups = detection_left_factoring(list(grammar.items()))
        if total_groups == 0:
            if iteration == 1:
                print("\nNo left factoring detected; no changes made.")
            else:
                print("\nNo further left factoring to remove.")
            break

        # Process nonterminals deterministically (by current insertion order)
        for nt in list(grammar.keys()):
            if nt not in factoring_map:
                continue
            char_mode, groups = factoring_map[nt]
            # Apply groups sequentially (changes can affect later groups)
            for prefix_tokens, group_prods in groups:
                current_prods = grammar.get(nt, [])
                to_factor = [p for p in current_prods if p in group_prods]
                if len(to_factor) < 2:
                    continue

                new_nt = _unique_new_nt(nt, existing_nts)

                # compute remainders for new nonterminal
                new_nt_prods = []
                for p in to_factor:
                    tokens = _tokenize(p, char_mode)
                    if len(tokens) >= len(prefix_tokens) and tokens[:len(prefix_tokens)] == prefix_tokens:
                        remainder = tokens[len(prefix_tokens):]
                    else:
                        remainder = tokens  # fallback
                    if remainder:
                        remainder_str = ''.join(remainder) if char_mode else ' '.join(remainder)
                        new_nt_prods.append(remainder_str)
                    else:
                        new_nt_prods.append(EPSILON)

                # replace grouped productions with one prefixed production
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

                # dedupe new_nt_prods
                seen = set()
                deduped = []
                for x in new_nt_prods:
                    if x not in seen:
                        deduped.append(x)
                        seen.add(x)
                grammar[new_nt] = deduped

                # print transformation
                display_prefix = ''.join(prefix_tokens) if char_mode else ' '.join(prefix_tokens)
                print(f"\nFactoring applied on {nt}:")
                print(f"  Common prefix: '{display_prefix}'")
                print(f"  Replaced productions: {', '.join(to_factor)}")
                print(f"  New {nt} productions: {', '.join(grammar[nt])}")
                print(f"  Introduced {new_nt} -> {', '.join(grammar[new_nt])}")

    # final grammar printout
    print("\n--- Grammar after left factoring removal ---")
    final_rules = []
    for nt, prods in grammar.items():
        print(f"{nt} -> " + " | ".join(prods))
        final_rules.append((nt, prods))
    return final_rules


# ----------------------------
# INPUT SECTION (where you enter grammar) and function calls
# ----------------------------
if __name__ == "__main__":
    # --- INPUT SECTION ---
    n = int(input("Enter number of rules: "))
    rules = []
    for _ in range(n):
        rules.append(input())

    # 1) Left recursion detection (parses rules into parsed_rules)
    parsed_rules, left_recursive_count = detect_left_recursion(rules)

    # 2) Left recursion removal (COMMENTED OUT as requested)
    # without_left_recursion = remove_left_recursion(parsed_rules)
    # (left recursion removal is disabled; parsed_rules remains unchanged)

    # 3) Left factoring detection (operate on original parsed_rules)
    factoring_map, total_fact_groups = detection_left_factoring(parsed_rules)

    # 4) Left factoring removal (if any)
    if total_fact_groups > 0:
        final_grammar = removal_left_factoring(parsed_rules)
    else:
        print("\nNo left factoring groups found; grammar unchanged after factoring pass.")
        final_grammar = parsed_rules

    print("\n--- All transformations complete ---")
