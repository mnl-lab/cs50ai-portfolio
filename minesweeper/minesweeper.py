import itertools
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # this function determines known mines by logical deduction
        if self.count == len(self.cells):
            return self.cells.copy()
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # this function determines known safes by logical deduction
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.discard(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1
        self.moves_made.add(cell)
        # 2
        self.mark_safe(cell)
        # 3
        neigh = set()
        mines_c = count
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                if (
                    i < 0 or j < 0 or i >= self.height or j >= self.width
                ):  # we don't add out-of-bound cells
                    continue
                if (
                    i,
                    j,
                ) in self.mines:  # it's alrady in self.mines so it's already marked as a mine in knowledge
                    mines_c -= 1
                    continue
                if (i, j) in self.safes:  # it's already marked as safe in knowledge
                    continue
                neigh.add((i, j))  # adding only unknown cells
        if neigh:
            if (
                mines_c == 0
            ):  # if the number is of mines is 0 then all the neighboring cells are safe
                for c in neigh:
                    self.mark_safe(c)
            elif (
                len(neigh) == mines_c
            ):  # if the number of unknown cells is exactly the number of remaining mines
                for c in neigh:
                    self.mark_mine(c)  # then all of them are mines
            else:  # else, a sentence is added
                new_sentence = Sentence(neigh, mines_c)
                self.knowledge.append(new_sentence)
        # 4 & 5
        changed = True
        # we need this loop because marking safe and mine creates possibilities for new inferences that we need to keep track of
        # we'll get errors and infinite loops and performance issues otherwise
        # so the loop runs as long as there are made changes
        while changed:
            changed = False
            for sentence in self.knowledge:
                # Check for known safes or mines
                safe_cells = sentence.known_safes()
                for safe_cell in safe_cells:
                    self.mark_safe(safe_cell)
                    changed = True

                mine_cells = sentence.known_mines()
                for mine_cell in mine_cells:
                    self.mark_mine(mine_cell)
                    changed = True

            # 5 inferences
            inferences = []
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2:
                    if sentence1.cells.issubset(sentence2.cells):
                        # using the rule set2 - set1 = count2 - count1
                        new_cells = sentence2.cells - sentence1.cells
                        new_count = sentence2.count - sentence1.count

                        if new_cells and new_count >= 0:
                            new_sentence = Sentence(new_cells, new_count)
                            # check if this sentence is new
                            if new_sentence not in self.knowledge:
                                inferences.append(new_sentence)
                                changed = True

            self.knowledge.extend(inferences)  # adding new sentences
            self.knowledge = [
                s for s in self.knowledge if s.cells
            ]  # removing empty sentences

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:  # cells that are guaranteed to be safe
            if cell not in self.moves_made:  # and not played yet
                return cell  # return the first found one
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possibilities = []
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.mines and (i, j) not in self.moves_made:
                    possibilities.append(
                        (i, j)
                    )  # appending are non forbidden cells into a list
        if not possibilities:
            return None  # if no move is available
        return random.choice(possibilities)  # we randomly select a cell
