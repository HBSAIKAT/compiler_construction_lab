# ----------------------------
# Functions (left recursion + left factoring + FIRST only)
# Duplicate outputs removed by quiet detection inside removal loop.
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
    """
    for p in productions:
        if ' ' in p:
            return False
    return True

def _tokenize_char_mode_with_nts(prod, nonterminals):
    pt = prod.strip()
    if pt == '' or pt == EPSILON:
        return []
    tokens = []
    i = 0
    n = len(pt)
    nts_sorted = sorted(nonterminals, key=lambda x: -len(x))
    while i < n:
        matched = False
        for nt in nts_sorted:
            ln = len(nt)
            if ln == 0:
                continue
            if i + ln <= n and pt[i:i+ln] == nt:
                tokens.append(nt)
                i += ln
                matched = True
                break
        if not matched:
            tokens.append(pt[i])
            i += 1
    return tokens

def _tokenize(prod, char_mode, nonterminals=None):
    pt = prod.strip()
    if pt == '' or pt == EPSILON:
        return []
    if char_mode:
        if nonterminals is None:
            return list(pt)
        else:
            return _tokenize_char_mode_with_nts(pt, nonterminals)
    else:
        return pt.split()

def _build_trie_with_mode(productions, char_mode, nonterminals=None):
    root = _TrieNode()
    for p in productions:
        tokens = _tokenize(p, char_mode, nonterminals)
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

def detection_left_factoring(parsed_rules, verbose=True):
    """
    parsed_rules: list of (non_terminal, [productions])
    Returns: factoring_map, total_groups
      factoring_map: {nt: (char_mode, [(prefix_tokens, [productions]), ...])}
    If verbose==True, prints detection output; otherwise returns data quietly.
    """
    factoring_map = {}
    total_groups = 0

    for nt, prods in parsed_rules:
        if len(prods) < 2:
            if verbose:
                print(f"{nt} has no left factoring.")
            continue

        char_mode = _choose_char_mode(prods)
        root = _build_trie_with_mode(prods, char_mode, None)
        groups = _collect_maximal_prefixes(root)
        if groups:
            factoring_map[nt] = (char_mode, groups)
            total_groups += len(groups)
            if verbose:
                print(f"{nt} has {len(groups)} left factoring group(s):")
                for idx, (prefix, group_prods) in enumerate(groups, start=1):
                    if char_mode:
                        pref_s = ''.join(prefix)
                    else:
                        pref_s = ' '.join(prefix)
                    print(f"  Group {idx}: common prefix -> '{pref_s}'")
                    for gp in group_prods:
                        print(f"    {nt} -> {gp}")
        else:
            if verbose:
                print(f"{nt} has no left factoring.")
    if verbose:
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
    Removes left factoring iteratively. Uses quiet detection internally (no repeated detection prints).
    Prints per-change factoring info and final grammar.
    """
    print("\n--- Left Factoring Removal Result ---")
    grammar = {nt: list(prods) for nt, prods in parsed_rules}
    existing_nts = set(grammar.keys())

    iteration = 0
    while True:
        iteration += 1
        # QUIET detection to drive removal (prevents duplicate printed detection headers)
        factoring_map, total_groups = detection_left_factoring(list(grammar.items()), verbose=False)
        if total_groups == 0:
            if iteration == 1:
                print("\nNo left factoring detected; no changes made.")
            else:
                print("\nNo further left factoring to remove.")
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
                nt_set = set(grammar.keys()) | {new_nt}
                for p in to_factor:
                    tokens = _tokenize(p, char_mode, nt_set if char_mode else None)
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

                # dedupe new_nt_prods
                seen = set()
                deduped = []
                for x in new_nt_prods:
                    if x not in seen:
                        deduped.append(x)
                        seen.add(x)
                grammar[new_nt] = deduped

                # print per-change transformation (one-time per change)
                display_prefix = ''.join(prefix_tokens) if char_mode else ' '.join(prefix_tokens)
                print(f"\nFactoring applied on {nt}:")
                print(f"  Common prefix: '{display_prefix}'")
                print(f"  Replaced productions: {', '.join(to_factor)}")
                print(f"  New {nt} productions: {', '.join(grammar[nt])}")
                print(f"  Introduced {new_nt} -> {', '.join(grammar[new_nt])}")

    # final grammar printout (printed once)
    print("\n--- Grammar after left factoring removal ---")
    final_rules = []
    for nt, prods in grammar.items():
        print(f"{nt} -> " + " | ".join(prods))
        final_rules.append((nt, prods))
    return final_rules


# ----------------------------
# FIRST (only) — FOLLOW & table kept but not called in main
# ----------------------------

def build_tokenized_grammar(parsed_rules):
    nonterminals = [nt for nt, _ in parsed_rules]
    char_mode_map = {}
    for nt, prods in parsed_rules:
        char_mode_map[nt] = _choose_char_mode(prods)

    grammar_tokens = {}
    for nt, prods in parsed_rules:
        cm = char_mode_map.get(nt, True)
        tokenized_prods = []
        current_nts = set([x for x, _ in parsed_rules])
        for p in prods:
            if cm:
                tokens = _tokenize(p, True, current_nts)
            else:
                tokens = _tokenize(p, False, None)
            tokenized_prods.append(tokens)
        grammar_tokens[nt] = tokenized_prods

    terminals = set()
    for nt, prods in grammar_tokens.items():
        for prod in prods:
            for tok in prod:
                if tok == EPSILON:
                    continue
                if tok not in grammar_tokens.keys():
                    terminals.add(tok)
    return grammar_tokens, char_mode_map, set(grammar_tokens.keys()), terminals

def compute_first_sets(grammar_tokens):
    FIRST = defaultdict(set)

    nonterminals = set(grammar_tokens.keys())
    symbols = set()
    for nt, prods in grammar_tokens.items():
        for prod in prods:
            for tok in prod:
                symbols.add(tok)

    terminals = set([s for s in symbols if s not in nonterminals and s != EPSILON])
    for t in terminals:
        FIRST[t].add(t)

    for nt in nonterminals:
        FIRST[nt] = set()

    changed = True
    while changed:
        changed = False
        for nt, prods in grammar_tokens.items():
            for prod in prods:
                if not prod:
                    if EPSILON not in FIRST[nt]:
                        FIRST[nt].add(EPSILON)
                        changed = True
                    continue
                add_epsilon = True
                for symbol in prod:
                    to_add = set(FIRST[symbol]) - {EPSILON}
                    if to_add - FIRST[nt]:
                        FIRST[nt].update(to_add)
                        changed = True
                    if EPSILON in FIRST[symbol]:
                        add_epsilon = True
                        continue
                    else:
                        add_epsilon = False
                        break
                if add_epsilon:
                    if EPSILON not in FIRST[nt]:
                        FIRST[nt].add(EPSILON)
                        changed = True
    return FIRST

def pretty_print_first_sets(FIRST):
    print("\n--- FIRST sets ---")
    for sym in sorted(FIRST.keys()):
        if sym.isprintable():
            items = ', '.join(sorted(FIRST[sym]))
            print(f"FIRST({sym}) = {{ {items} }}")

# FOLLOW & table functions remain defined below (not called in main)
def first_of_sequence(seq, FIRST):
    if not seq:
        return {EPSILON}
    result = set()
    for symbol in seq:
        if symbol not in FIRST:
            result.add(symbol)
            return result
        result |= (FIRST[symbol] - {EPSILON})
        if EPSILON in FIRST[symbol]:
            continue
        else:
            return result
    result.add(EPSILON)
    return result

def compute_follow_sets(grammar_tokens, FIRST, start_symbol):
    nonterminals = list(grammar_tokens.keys())
    FOLLOW = {nt: set() for nt in nonterminals}
    FOLLOW[start_symbol].add('$')

    changed = True
    while changed:
        changed = False
        for A, prods in grammar_tokens.items():
            for prod in prods:
                for i, B in enumerate(prod):
                    if B not in grammar_tokens:
                        continue
                    beta = prod[i+1:]
                    first_beta = first_of_sequence(beta, FIRST)
                    to_add = set(first_beta) - {EPSILON}
                    if to_add - FOLLOW[B]:
                        FOLLOW[B].update(to_add)
                        changed = True
                    if EPSILON in first_beta or not beta:
                        if FOLLOW[A] - FOLLOW[B]:
                            FOLLOW[B].update(FOLLOW[A])
                            changed = True
    return FOLLOW

def construct_parsing_table(grammar_tokens, FIRST, FOLLOW):
    table = {}
    conflicts = []
    nonterminals = list(grammar_tokens.keys())
    terminals = set()
    for nt, prods in grammar_tokens.items():
        for prod in prods:
            for tok in prod:
                if tok != EPSILON and tok not in nonterminals:
                    terminals.add(tok)
    terminals_list = sorted(terminals)
    all_terminals = terminals_list + ['$']

    for A in nonterminals:
        for prod in grammar_tokens[A]:
            first_seq = first_of_sequence(prod, FIRST)
            for a in (first_seq - {EPSILON}):
                key = (A, a)
                if key in table and table[key] != prod:
                    conflicts.append((A, a, table[key], prod))
                else:
                    table[key] = prod
            if EPSILON in first_seq:
                for b in FOLLOW[A]:
                    key = (A, b)
                    if key in table and table[key] != prod:
                        conflicts.append((A, b, table[key], prod))
                    else:
                        table[key] = prod
    is_ll1 = len(conflicts) == 0
    return table, is_ll1, conflicts, sorted(all_terminals)

# ----------------------------
# INPUT SECTION (where you enter grammar) and function calls
# ----------------------------
if __name__ == "__main__":
    n = int(input("Enter number of rules: "))
    rules = []
    for _ in range(n):
        rules.append(input().strip())

    # 1) Left recursion detection (parses rules into parsed_rules)
    parsed_rules, left_recursive_count = detect_left_recursion(rules)

    # 2) Left recursion removal (COMMENTED OUT as requested)
    # without_left_recursion = remove_left_recursion(parsed_rules)

    # 3) Left factoring detection (prints once)
    factoring_map, total_fact_groups = detection_left_factoring(parsed_rules, verbose=True)

    # 4) Left factoring removal (if any) - internally uses quiet detection
    if total_fact_groups > 0:
        final_grammar = removal_left_factoring(parsed_rules)
    else:
        print("\nNo left factoring groups found; grammar unchanged after factoring pass.")
        final_grammar = parsed_rules

    # 5) Build tokenized grammar from final_grammar and compute FIRST only
    grammar_tokens, char_mode_map, nonterminals, terminals = build_tokenized_grammar(final_grammar)

    # Choose start symbol as first LHS in final_grammar
    if final_grammar:
        start_symbol = final_grammar[0][0]
    else:
        start_symbol = None

    # Compute FIRST sets (printed once)
    FIRST = compute_first_sets(grammar_tokens)
    pretty_print_first_sets(FIRST)

    # FOLLOW and parsing table computation are still available but not invoked here.
    # To enable follow/table, uncomment the lines below.
    # FOLLOW = compute_follow_sets(grammar_tokens, FIRST, start_symbol)
    # pretty_print_follow_sets(FOLLOW)
    # table, is_ll1, conflicts, terminals_sorted = construct_parsing_table(grammar_tokens, FIRST, FOLLOW)
    # pretty_print_parsing_table(table, list(grammar_tokens.keys()), terminals_sorted, grammar_tokens)

    print("\n--- FIRST sets computed. FOLLOW and parse table computation are commented out. ---")
