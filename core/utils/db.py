from typing import List


def enquote_all(clauses: List[str]):
    for i in (range(len(clauses))):
        clauses[i] = enquote(clauses[i])

    return clauses


def enquote(clause):
    if clause is not None:
        return f"\"{clause}\""
    else:
        return "NULL"
