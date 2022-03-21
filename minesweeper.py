import itertools
import random
import copy


class Minesweeper():
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


class Sentence():
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
        # TODO
        mines = set()
        if len(self.cells) == self.count != 0:
            mines = self.cells  # creates same pointer in memory?
            # for cell in self.cells:  # Hopefully this creates separate object
            #     mines.add(cell)
        return mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # TODO
        safes = set()
        if self.cells != set() and self.count == 0:
            safes = self.cells  # creates same pointer in memory causing  RuntimeError('Set changed size during
            # iteration')?
            # for cell in self.cells:  # After this change, the program freezes and I don't know what is causing it
            #     safes.add(cell)
        return safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # TODO
        if cell in self.cells:  # No need to loop since set ensures unique value
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # TODO
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
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
        #  TODO
        #  1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        #  2) mark the cell as safe
        self.mark_safe(cell)  # adds to self.safes & runs sentence.mark_safe on all sentences in knowledge

        #  Identify neighbors
        neighbors = set()
        for d_row in range(-1, 2):
            for d_col in range(-1, 2):
                if d_row != 0 and d_col != 0:
                    n_row = cell[0] + d_row
                    n_col = cell[1] + d_col
                    if n_row in range(self.height) and n_col in range(self.width):
                        neighbors.add((n_row, n_col))

        # Process neighboring mines
        neighboring_mines = neighbors.intersection(self.mines)
        for c in neighboring_mines:
            self.mark_mine(c)
            if count > 0:
                count -= 1
            else:
                break

        neighbors.difference_update(self.mines)  # exclude identified mines from neighbors

        # Process neighboring safes
        neighboring_safes = neighbors.intersection(self.safes)
        [self.mark_safe(c) for c in neighboring_safes]  # mark_safe all neighboring safes
        neighbors.difference_update(self.safes)  # exclude identified safes from remaining neighbors

        #  Case when remaining neighboring cells are mine
        if len(neighbors) == count != 0:
            for c in neighbors:
                if c not in self.mines:
                    self.mark_mine(c)  # adds to self.mines & runs sentence.mark_mine on all sentences in knowledge
        #  Case when all cells are safe
        elif neighbors != set() and count == 0:
            for c in neighbors:
                if c not in self.safes:
                    self.mark_safe(c)  # adds to self.safes & runs sentence.mark_safe on all sentences in knowledge
        #  Surviving neighboring cells are undertermined
        else:
            #  3) add a new sentence to the AI's knowledge base
            #                based on the value of `cell` and `count`
            new_sentence = Sentence(list(neighbors), count)
            if new_sentence not in self.knowledge and new_sentence.cells != set():
                self.knowledge.append(new_sentence)

        #  4) mark any additional cells as safe or as mines
        #                if it can be concluded based on the AI's knowledge base


        # curr_knowledge = copy.deepcopy(self.knowledge)  # is this allowed? this seems to fix the problem of size change
        # # curr_knowledge = self.knowledge
        #
        # for s in curr_knowledge:
        #     if s.cells != set():
        #         safes = s.known_safes()
        #         mines = s.known_mines()
        #         [self.mark_safe(safe) for safe in safes if safes != set()]
        #         [self.mark_mine(mine) for mine in mines if mines != set()]
        #     else:
        #         self.knowledge.remove(s)  # remove s from the real self.knowledge
        #  Try to conclude safe and mines from existing knowledge
        # for s in self.knowledge:
        #     if s.known_safes() != set():
        #         self.safes.union(s.known_safes())  # merge to master safes
        #     if s.known_mines() != set():
        #         self.mines.union(s.known_mines())  # merge to master mines
        #
        # safes = self.safes
        # mines = self.mines
        # #  Actually mark cells as safe or mines
        # [self.mark_safe(c) for c in safes]
        # [self.mark_mine(c) for c in mines]
        #
        # #  Delete empty sets
        # [x for x in self.knowledge if x.cells != set()]


        #  5) add any new sentences to the AI's knowledge base
        #                if they can be inferred from existing knowledge
        #  Infer new knowledge based on subsets on existing sentences
        # temp_knowledge = []
        # a_cnt = 0
        # for a in self.knowledge:
        #     a_cnt += 1
        #     b_cnt = 0
        #     for b in self.knowledge:
        #         b_cnt += 1
        #         if a != b:
        #             if a.cells.issubset(b.cells):
        #                 temp_knowledge.append(Sentence(b.cells - a.cells, b.count - a.count))
        #             if b.cells.issubset(a.cells):
        #                 temp_knowledge.append(Sentence(a.cells - b.cells, a.count - b.count))
        #
        # [self.knowledge.append(s) for s in temp_knowledge if s not in self.knowledge]  # merge with real knowledge

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # TODO
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # TODO
        moves_remain = set()
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    moves_remain.add((i, j))
        if moves_remain != set():
            return random.choice(tuple(moves_remain))
        else:
            return None

