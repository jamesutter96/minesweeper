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
        # go through all cells in a sentence 
        if len(self.cells) == self.count:
            return set(self.cells)

        return set()


        #raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)

        return set()

        #raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            # remove the mine from the sentence 
            self.cells.remove(cell)
            # reduce teh counting amount by 1
            self.count -= 1

            return None 

        #raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            # remove the safe cells from the sentence 
            self.cells.remove(cell)
            # the count does not need to be reduced becausde there are no miones in the safe cells 
            return None 

        #raise NotImplementedError


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


    def neighbors_to_cell(self, cell):
        """
        this function finds all the neighbors to any cell on the board 
        """
        # counting the known mines found
        mines = 0 
        i, j = cell
        neighbors = set()
        for row in range(i-1, i+2):
            # checks to see if the row is even on the board (edge case)
            for col in range(j-1, j+2):
                # same check but for the fopr the columms 
                if ((col >= 0 and col < self.width) 
                    and ((row, col) != cell) 
                    and (row >= 0 and row < self.height) 
                    and ((row,col) is not self.moves_made)):

                    # if (row,col) is on the board then add it to the neighbors list 
                    if (row, col) in self.mines:
                        mines += 1

                    elif (row, col) in self.safes:
                        continue

                    else :
                        neighbors.add((row, col))

        # this will return a set of the neighboring cells and the mines 
        return neighbors, mines



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
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        #2) mark the cell as safe
        self.safes.add(cell)

        # 3) add a new sentence to the AI's knowledge base
        #    based on the value of `cell` and `count`
        neighbors   = self.neighbors_to_cell(cell)[0]
        found_mines = self.neighbors_to_cell(cell)[1]
        # adjust the counter
        count -= found_mines

        # create a new sentence
        new_sen = Sentence(neighbors, count)

        # add the newly formulated sentence to the knowldge base 
        if new_sen not in self.knowledge:
            self.knowledge.append(new_sen)

        # 4) mark any additional cells as safe or as mines
        #    if it can be concluded based on the AI's knowledge base
        
        # going over all the sentences in the knowledge base 
        for sen in self.knowledge:
            safes = sen.known_safes()
            mines = sen.known_mines()
            #adding newly found safe areas to the known_safes in the knowledge base 
            for known_safe in safes:
                self.mark_safe(known_safe)

            for known_mine in mines:
                self.mark_mine(known_mine)

        
        #5) add any new sentences to the AI's knowledge base
        #   if they can be inferred from existing knowledge

        known_sentences = copy.deepcopy(self.knowledge)

        for sen1 in known_sentences:
            # to make sure that the loop does not go an infinate amount of times we will remove the sentence being looked at 
            known_sentences.remove(sen1)

            # iterate over the remaing sentences 
            for sen2 in known_sentences:
                # find which one of the sentences has the larger length and assigne that as a "bigger set" of knowldge
                # case for sen1 > sen2
                if ((len(sen1.cells) > len(sen2.cells)) and len(sen1.cells) != 0 and len(sen2.cells) != 0):
                    small_set  = sen2.cells
                    big_set    = sen1.cells
                    diff_count = sen1.count - sen2.count

                elif ((len(sen2.cells) > len(sen1.cells)) and len(sen1.cells) != 0 and len(sen2.cells) != 0):
                    small_set  = sen1.cells
                    big_set    = sen2.cells
                    diff_count = sen2.count - sen1.count

                # if they are the same length        
                elif (len(sen1.cells) == len(sen2.cells)):

                    continue

                # again insuring that an infinate loop is not in place         
                else:
                    continue


                # looking to see if the small_set is a subset of big_set 
                if small_set <= big_set:
                    diff_set = big_set - small_set

                    # looking to see how much of a difference there is 
                    # seeing if there is only one extra field in knowledge base
                    if len(diff_set) == 1:

                        # checks if the cell is a mine or a safe 
                        if diff_count == 0:
                            new_safe = diff_set.pop()
                            self.mark_safe(new_safe)

                        if diff_count == 1:
                            new_mine = diff_set.pop()
                            self.mark_mine(new_mine)

                    else:
                        # adding small_set into knowledge base 
                        self.knowledge.append(Sentence(diff_set, diff_count))




        #raise NotImplementedError

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # printing the first safe move that will be made 
        print(f'{len(self.safes - self.moves_made)} known unsued safe moves')
        print(f'{len(self.mines)} known mines: \n{list(self.mines)}')

        for i in self.safes:
            # seeing if the move has been made yet
            if i in self.moves_made:
                continue

            else:
                safe_move = i 
                # add the new move to the made moves list 
                self.moves_made.add(safe_move)
                print(f'Made Move: {safe_move}')
                # if the move os safe and it has not bewen found in the past then break out of the loop 
                return safe_move

            return None  
        #raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        
        # list of potential moves 
        future_moves = []
        # go through all the cells on the board 
        board = []
        for row in range(self.height):
            for col in range(self.width):
                board.append((row, col))


        for future_cell in board:
            if (future_cell not in self.mines) and (future_cell not in self.moves_made):
                future_moves.append(future_cell)

        if len(future_moves) == 0:
            print("The Game Is Finished!")

        else:
            # picking a random move from all the potential moves that can be made 
            random_move = random.choice(future_moves)
            self.moves_made.add(random_move)
            print(f'Move Made {random_move}')

            return random_move

        # raise NotImplementedError


















