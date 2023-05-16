import random
import time

BOARD_SIZE = 15  # 오목판의 크기
EMPTY = 0  # 빈 칸
BLACK = 1  # 흑돌
WHITE = 2  # 백돌
COMPUTER = 3  # 컴퓨터
HUMAN = 4  # 인간
GOMOKU = 5  # 오목

class OpeningRule:
    def __init__(self, opening_rule):
        self.name = opening_rule
        if opening_rule != 'Pro':
            self.name = 'Standard'

    def possible(self, r=None, c=None, turn=None):
        if self.name == 'Pro':
            return self.Pro().possible(r, c, turn)
        else:
            return self.Standard().possible()

    class Standard:
        def possible(self):
            return True

    class Pro:
        def possible(self, r, c, turn):
            if turn == 1 and not (r == 7 and c == 7):
                return False
            if turn == 3 and 5 <= r < 10 and 5 <= c < 10:
                return False
            return True

class GomokuBoard:
    def __init__(self):
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = BLACK

    def put_stone(self, r, c):
        if self.board[r][c] != EMPTY:
            return False

        self.board[r][c] = self.current_player
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        return True

    def check_winner(self):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    if self.check_gomoku(i, j, dr, dc):
                        return self.board[i][j]
        return None

    def check_gomoku(self, r, c, dr, dc):
        player = self.board[r][c]
        if player == EMPTY:
            return False
        if 0 <= r-dr < BOARD_SIZE and 0 <= c-dc < BOARD_SIZE and player == self.board[r-dr][c-dc]:
            return False

        count = 0
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
            count += 1
            r, c = r + dr, c + dc
        return count == 5

    def print_board(self):
        print('   ', end='')
        for i in range(BOARD_SIZE):
            print(chr(ord('a') + i), end=' ')
        print()
        for i in range(BOARD_SIZE):
            print(f'{i+1:2d}', end=' ')
            for j in range(BOARD_SIZE):
                if self.board[i][j] == EMPTY:
                    print('+', end=' ')
                elif self.board[i][j] == BLACK:
                    print('●', end=' ')
                elif self.board[i][j] == WHITE:
                    print('○', end=' ')
                elif self.board[i][j] == GOMOKU:
                    print('5', end=' ')
            print()

    def not_full(self):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == EMPTY:
                    return True
        return False

class Computer:
    def __init__(self, color, opening_rule='Standard'):
        self.type = 'Computer'
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.color = color
        self.oppo_color = WHITE if color == BLACK else BLACK
        self.opening_rule = opening_rule
        self.last_move = (None, None)
        self.oppo_last_move = (None, None)
        self.used_move = set([self.last_move])

    def update_last_move(self, move):
        self.last_move = move
        self.used_move.add(self.last_move)

    def update_oppo_last_move(self, move):
        self.oppo_last_move = move
        self.used_move.add(self.oppo_last_move)

    def make_move(self, board, turn=None):
        if self.opening_rule == 'Pro':
            if turn == 1:
                move = 7, 7
                self.update_last_move(move)
                return move
            if turn == 3:
                pass

        if self.last_move == (None, None):
            move = self.random_move()
            self.update_last_move(move)
            return move

        move = self.find_four(board, self.color)
        if move is not None:
            self.update_last_move(move)
            return move
        move = self.find_four(board, self.oppo_color)
        if move is not None:
            self.update_last_move(move)
            return move

        # if can_win(): make_move
        move = self.find_open_three(board, self.color)
        if move is not None:
            self.update_last_move(move)
            return move
        move = self.find_open_three(board, self.oppo_color)
        if move is not None:
            self.update_last_move(move)
            return move
        
        move = self.random_move()
        self.update_last_move(move)
        return move

    def find_four(self, board, color):
        last_move = self.last_move if color == self.color else self.oppo_last_move
        for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            ends = [None, None]
            count = 0
            r, c = last_move
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == color:
                count += 1
                r, c = r + dr, c + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                ends[0] = r, c

            r, c = last_move[0] - dr, last_move[1] - dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == color:
                count += 1
                r, c = r - dr, c - dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                ends[1] = r, c

            if count > 4:
                continue

            if ends[0] is not None:
                count_temp = 0
                r, c = ends[0][0] + dr, ends[0][1] + dc
                while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == color:
                    count_temp += 1
                    r, c = r + dr, c + dc
                if count + count_temp == 4 and board[ends[0][0]][ends[0][1]] == EMPTY:
                    return ends[0]

            if ends[1] is not None:
                count_temp = 0
                r, c = ends[1][0] - dr, ends[1][1] - dc
                while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == color:
                    count_temp += 1
                    r, c = r - dr, c - dc
                if count + count_temp == 4 and board[ends[1][0]][ends[1][1]] == EMPTY:
                    return ends[1]
        return None

    def find_open_three(self, board, color):
        last_move = self.last_move if color == self.color else self.oppo_last_move
        for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            ends = [None, None]
            count = 0
            r, c = last_move
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == color:
                count += 1
                r, c = r + dr, c + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                ends[0] = r, c

            r, c = last_move[0] - dr, last_move[1] - dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == color:
                count += 1
                r, c = r - dr, c - dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                ends[1] = r, c

            if count > 3:
                continue

            if ends[0] is not None:
                count_temp = 0
                r, c = ends[0][0] + dr, ends[0][1] + dc
                while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == color:
                    count_temp += 1
                    r, c = r + dr, c + dc
                if count + count_temp == 3 and board[ends[0][0]][ends[0][1]] == EMPTY and ends[1] is not None and board[ends[1][0]][ends[1][1]] == EMPTY:
                    return ends[0]

            if ends[1] is not None:
                count_temp = 0
                r, c = ends[1][0] - dr, ends[1][1] - dc
                while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == color:
                    count_temp += 1
                    r, c = r - dr, c - dc
                if count + count_temp == 3 and board[ends[1][0]][ends[1][1]] == EMPTY and ends[0] is not None and board[ends[0][0]][ends[0][1]] == EMPTY:
                    return ends[1]
        return None

    def random_move(self):
        r, c = None, None
        while (r, c) in self.used_move:
            r, c = random.randrange(BOARD_SIZE), random.randrange(BOARD_SIZE)
        return r, c

class Human:
    def __init__(self, color):
        self.type = 'Human'
        self.color = color

    def make_move(self, board=None, turn=None):
        r, c = None, None
        while True:
            move = input()
            if 2 <= len(move) <= 3 and move[0].isalpha() and move[1:].isdigit():
                r, c = int(move[1:]) - 1, ord(move[0]) - ord('a')
                break
            print("Invalid input. Please enter a letter and a digit (e.g. 'a1').")
        return r, c

def main():
    user_color = 0
    while user_color != BLACK and user_color != WHITE:
        user_color = int(input('Choose your color [1(Black)/2(White)]: '))
    oppo_color = WHITE if user_color == BLACK else BLACK
    opening_rule = input('If you want, write an opening rule where you want to gomoku: ')
    
    user = None
    oppo = None
    mode = input('Choose Mode [1(1 vs 1), 2(1 vs Bot), 3(Bot vs Bot)]: ')
    if mode == '1':  # user vs user
        user = Human(user_color)
        oppo = Human(oppo_color)
    elif mode == '2':  # user vs computer
        user = Human(user_color)
        oppo = Computer(oppo_color, opening_rule)
    elif mode == '3':
        user = Computer(user_color, opening_rule)
        oppo = Computer(oppo_color, opening_rule)

    # user = Human(user_color)
    # user = Computer(user_color, opening_rule)
    # oppo = Computer(WHITE if user_color == BLACK else BLACK, opening_rule)
    # oppo = Human(WHITE if user_color == BLACK else BLACK)
    board = GomokuBoard()
    opening_rule = OpeningRule(opening_rule)
    print('Opening rule:', opening_rule.name)
    turn = 1
    while board.not_full():
        time.sleep(0.5)
        print('Turn', turn)
        board.print_board()
        if board.current_player == BLACK:
            prompt = "Black's turn (e.g. 'a1'):"
        else:
            prompt = "White's turn (e.g. 'b3'):"

        r, c = None, None
        if board.current_player == user_color:
            print(prompt, end=' ')
            r, c = user.make_move(board.board, turn)
            if user.type == 'Computer':
                move = chr(ord('a')+c) + str(r+1)
                print(move)
        else:
            print(prompt, end=' ')
            r, c = oppo.make_move(board.board, turn)
            if oppo.type == 'Computer':
                move = chr(ord('a')+c) + str(r+1)
                print(move)

        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
            print('Invalid position. Please enter a position within the board.')
            continue
        if not opening_rule.possible(r, c, turn):
            print(f'{opening_rule.name} opening rule does not allow the position now.')
            continue
        if not board.put_stone(r, c):
            print('The position is already occupied. Please choose another position.')
            continue

        if board.current_player == user_color:
            if user.type == 'Computer':
                user.update_oppo_last_move((r, c))
        else:
            if oppo.type == 'Computer':
                oppo.update_oppo_last_move((r, c))
        turn += 1

        winner = board.check_winner()
        if winner is not None:
            board.print_board()
            if winner == BLACK:
                print('Black wins!')
            else:
                print('White wins!')
            break
    else:
        board.print_board()
        print('Draw.')
    
    print('Game over.')

if __name__ == '__main__':
    main()
