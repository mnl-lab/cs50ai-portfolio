import csv
import itertools
import sys

PROBS = {
    # Unconditional probabilities for having gene
    "gene": {2: 0.01, 1: 0.03, 0: 0.96},
    "trait": {
        # Probability of trait given two copies of gene
        2: {True: 0.65, False: 0.35},
        # Probability of trait given one copy of gene
        1: {True: 0.56, False: 0.44},
        # Probability of trait given no gene
        0: {True: 0.01, False: 0.99},
    },
    # Mutation probability
    "mutation": 0.01,
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {"gene": {2: 0, 1: 0, 0: 0}, "trait": {True: 0, False: 0}}
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (
                people[person]["trait"] is not None
                and people[person]["trait"] != (person in have_trait)
            )
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (
                    True
                    if row["trait"] == "1"
                    else False if row["trait"] == "0" else None
                ),
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s)
        for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # we start by people who don't have parents to get data from
    parentless = []
    for i in people:
        if not people[i]["mother"] and not people[i]["father"]:
            parentless.append(i)

    probas = {
        person: 0 for person in people
    }  # dictionnary to store probabilities for each person
    for (
        person
    ) in (
        parentless
    ):  # computing the probabilities for people with no parents using the PROBS dictionary
        if person in one_gene:
            if person in have_trait:
                probas[person] = PROBS["gene"][1] * PROBS["trait"][1][True]
            else:
                probas[person] = PROBS["gene"][1] * PROBS["trait"][1][False]
        elif person in two_genes:
            if person in have_trait:
                probas[person] = PROBS["gene"][2] * PROBS["trait"][2][True]
            else:
                probas[person] = PROBS["gene"][2] * PROBS["trait"][2][False]
        else:
            if person in have_trait:
                probas[person] = PROBS["gene"][0] * PROBS["trait"][0][True]
            else:
                probas[person] = PROBS["gene"][0] * PROBS["trait"][0][False]

    reception = (
        dict()
    )  # this dictionary collects the probabilities that each one of someone's parents gives them the gene
    for person in people:
        if person in parentless:  # we already calculated probabilities for those
            continue
        reception[person] = {"mother": 0, "father": 0}
        # cases are split and we use the following rule:
        # a parent that has one copy has a probability of 0.5 to pass the gene
        # a parent that has 2 copies has a probability of 1 - PROBS["mutation"]  to pass the gene
        # a parent that has zero copies had a probability of PROBS["mutation"] to pass the gene
        if people[person]["mother"] in one_gene:
            reception[person]["mother"] = 0.5
        elif people[person]["mother"] in two_genes:
            reception[person]["mother"] = 1 - PROBS["mutation"]
        else:
            reception[person]["mother"] = PROBS["mutation"]

        if people[person]["father"] in one_gene:
            reception[person]["father"] = 0.5
        elif people[person]["father"] in two_genes:
            reception[person]["father"] = 1 - PROBS["mutation"]
        else:
            reception[person]["father"] = PROBS["mutation"]

    for person in reception:
        # now the following rule is used to calculate each probability:
        # P(0 copies) = (1-P(mother gives)) * (1-P(father gives)) because none of them gives a copy
        # P(1 copy) = P(mother gives) * (1- P(father gives)) + P(father gives) * (1-P(mother gives))
        # because it's either the father gives a copy and the mother doesnt or the opposite
        # P(2 copies) = P(mother gives) * P(father gives) because both of them should give a copy
        # and after each one is calculated, we multiply it with the trait related probability to complete the calculation
        if person in one_gene:
            probas[person] = reception[person]["mother"] * (
                1 - reception[person]["father"]
            ) + reception[person]["father"] * (1 - reception[person]["mother"])
            if person in have_trait:
                probas[person] *= PROBS["trait"][1][True]
            else:
                probas[person] *= PROBS["trait"][1][False]
        elif person in two_genes:
            probas[person] = reception[person]["mother"] * reception[person]["father"]
            if person in have_trait:
                probas[person] *= PROBS["trait"][2][True]
            else:
                probas[person] *= PROBS["trait"][2][False]
        else:
            probas[person] = (1 - reception[person]["father"]) * (
                1 - reception[person]["mother"]
            )
            if person in have_trait:
                probas[person] *= PROBS["trait"][0][True]
            else:
                probas[person] *= PROBS["trait"][0][False]
    total = 1  # initialising the total
    for person in probas:
        total *= probas[
            person
        ]  # multiplying each probability of each êrson to form a joint probability

    return total


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        # updating based on genes
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p

        # updating based on traits
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # calculating the normalisation constants for genes distribution and trait distribution
        alpha1 = sum(list(probabilities[person]["gene"].values()))
        alpha2 = sum(list(probabilities[person]["trait"].values()))
        # dividing each elment on each distibution by the convenient normalising constant
        for i in probabilities[person]["gene"]:
            probabilities[person]["gene"][i] /= alpha1
        for j in probabilities[person]["trait"]:
            probabilities[person]["trait"][j] /= alpha2


if __name__ == "__main__":
    main()
