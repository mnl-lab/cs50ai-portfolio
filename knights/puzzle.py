from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Not(And(AKnave, AKnight)),  # A can't be both
    Implication(
        And(AKnight, AKnave), AKnight
    ),  # if A is a knight then everything they say is true
    Implication(
        Not(And(AKnave, AKnight)), AKnave
    ),  # if A is a knave then what they said is false
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Not(
        And(AKnave, BKnave)
    ),  # a knight can't say they're a knave so what A said isn't true
    Implication(
        Not(And(AKnave, BKnave)), And(AKnave, BKnight)
    ),  # B said nothing so the falsness of the statement leads to the fact that B is a knight and A is a knave
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Implication(Not(And(AKnave, BKnave)), And(AKnave, BKnight)),
    Implication(Not(And(AKnight, BKnight)), And(AKnave, BKnight)),
    Implication(And(AKnave, BKnight), And(AKnave, BKnight)),
    Not(And(AKnave, BKnave)),
    Not(And(AKnight, BKnight)),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    And(Or(AKnight, AKnave), Not(And(AKnave, AKnight))),  # What A said is true
    Implication(
        And(Or(AKnight, AKnave), Not(And(AKnave, AKnight))), BKnave
    ),  # B said something that A didn't say so B is a knave
    Implication(
        BKnave, CKnight
    ),  # if B is a knave then C is a knight because B said otherwise
    Implication(CKnight, AKnight),  # if C is a knight then it's trus that A is a knight
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3),
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
