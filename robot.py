# najzanimivejsi del projektne naloge

def update(state, y, x, points, directions, n, change=True):
    # to je treba še narediti
    stone = {1:-1, 2:0}.get(n, 0 if (n + 1) % 2 == 0 else 1 - (n % 4))
    color = 1 - 2 * ((n % 4) // 2) if n != 1 else -1
    for i in range(4):
        update_one_board(state[i], y, x, points, directions[i], color, stone, change=change)


def update_one_board(board, y, x, points_diff, directions, color, stone, change=True):
    dy0, dx0 = directions[0]
    dy1, dx1 = directions[1]

    a0 = board[y + dy0][x + dx0]
    a1 = board[y + dy1][x + dx1]

    k0 = 0 if  a0 is None else a0 * stone
    k1 = 0 if  a1 is None else a1 * stone

    stones_in_seq = 1
    if k0 > 0:
        stones_in_seq += k0
    if k1 > 0:
        stones_in_seq += k1

    ak0, ak1 = abs(k0), abs(k1)

    if k0 > 0 or k1 > 0:

        b0 = board[y + (k0 + 1) * dy0][x + (k0 + 1) * dx0]
        b1 = board[y + (k1 + 1) * dy1][x + (k1 + 1) * dx1]

        if  k0 > 0 and k1 > 0:

            points_diff[color] -= ak0 + ak1
            points_diff[1 - color] += (stones_in_seq * (stones_in_seq - 1) - ak0 * (ak0 - 1) - ak1 * (ak1 - 1)) // 2
            if b0 is None:
                points_diff[color] += stones_in_seq - ak0

            if b1 is None:
                points_diff[color] += stones_in_seq - ak1
    
        else:
            if a0 is None:
                points_diff[color] += 1
                points_diff[1 - color] += ak1
                if b1 is None:
                    points_diff[color] += 1

            elif a1 is None:
                points_diff[color] += 1
                points_diff[1 - color] += ak0
                if b0 is None:
                    points_diff[color] += 1
            
            else:
                if k0 > 0:
                    points_diff[color] -= ak0
                    points_diff[1 - color] += ak0
                    if b0 is None:
                        points_diff[color] += 1
                    if k1 < 0:
                        points_diff[2 + color] -= ak1
                else:  # k1 > 0
                    points_diff[color] -= ak1
                    points_diff[1 - color] += ak1
                    if b1 is None:
                        points_diff[color] += 1
                    if k0 < 0:
                        points_diff[2 + color] -= ak0

    else:
        if stone:
            points_diff[color] += (a0 is None) + (a1 is None)

        if not a0 is None:
            if a0 < 0:
                points_diff[3] += a0
            elif a0 > 0:
                points_diff[1] -= a0

        if not a1 is None:
            if a1 < 0:
                points_diff[3] += a1
            elif a1 > 0:
                points_diff[1] -= a1
        

    if change:
        if k0 > 0 and k1 > 0:
            board[y][x] = (k0 * stone, k1 * stone)
        else:
            board[y][x] = stones_in_seq * stone

        if k0 > 0:
            board[y + k0 * dy0][x + k0 * dx0] = stones_in_seq * stone
        if k1 > 0:
            board[y + k1 * dy1][x + k1 * dx1] = stones_in_seq * stone

def undo(state, y, x, directions):
    for i, j in enumerate(directions):
        dy0, dx0 = j[0]
        dy1, dx1 = j[1]
        board = state[i]
        if type(board[y][x]) == type((0,)):
            k0, k1 = board[y][x]
            board[y + abs(k0) * dy0][x + abs(k0) * dx0] = k0
            board[y + abs(k1) * dy1][x + abs(k1) * dx1] = k1
        else:
            k = board[y][x]
            if abs(k) == 1:
                pass
            elif (0 if board[y + dy0][x + dx0] is None else board[y + dy0][x + dx0]) * k > 0:
                board[y + (abs(k) - 1) * dy0][x + (abs(k) - 1) * dx0] = (k - 1 if k > 0 else k + 1)
            else:
                board[y + (abs(k) - 1) * dy1][x + (abs(k) - 1) * dx1] = (k - 1 if k > 0 else k + 1)
            
        board[y][x] = None





    


def ai(move_sequence, y, x):
    directions = (((1, 0), (-1, 0)), ((1, 1), (-1, -1)), ((0, 1), (0, -1)), ((-1, 1), (1, -1)))
    state = [[[None if not (i == 0 or j == 0 or i == x + 1 or j == x + 1) else 0
    for i in range(x + 2)] for j in range(y + 2)] for k in range(4)]
    points = [0 for i in range(4)]

    
    for i, j in enumerate(move_sequence):
        y, x, z = j
        update(state, y + 1, x + 1, points, directions, i)

    for i in state:
        print(i)
    print(points)

        


ai([], 6, 6)
for n in range(10):
    print()

a = [[None for i in range(7)]]
points_diff = [0, 0, 0, 0]
update_one_board(a, 0, 2, points_diff, ((0, 1), (0, -1)), -1, -1, change=True)
update_one_board(a, 0, 1, points_diff, ((0, 1), (0, -1)), 1, 1, change=True)
update_one_board(a, 0, 3, points_diff, ((0, 1), (0, -1)), -1, -1, change=True)
update_one_board(a, 0, 5, points_diff, ((0, 1), (0, -1)), -1, -1, change=True)
print(a)
update_one_board(a, 0, 4, points_diff, ((0, 1), (0, -1)), -1, -1, change=True)


print(a, points_diff, )
undo([a,], 0, 4, (((0, 1), (0, -1)),))
print(a)
undo([a,], 0, 1, (((0, 1), (0, -1)),))
print(a)

# ai([(0, 0, 0), (1, 1, 0), (0, 1, 0), (1, 2, 0), (2, 0, 0), (5, 5, 0), (4, 4, 0), (3, 3, 0), (1, 0, 0)], 6, 6)
