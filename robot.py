# najzanimivejsi del projektne naloge

def update(state, y, x, points, directions, n, change=True):
    # to je treba še narediti
    points_diff = [0 for i in range(4)]
    stone = {1:-1, 2:0}.get(n, 0 if (n + 1) % 2 == 0 else 1 - (n % 4))
    color = 1 - 2 * ((n % 4) // 2) if n != 1 else -1
    for i in range(4):
        pass


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
            board[y][x] = stones_in_seq * stone
            if k0 > 0:
                board[y + k0 * dy0][x + k0 * dx0] = stones_in_seq * stone
            if k1 > 0:
                board[y + k1 * dy1][x + k1 * dx1] = stones_in_seq * stone
    







def ai(move_sequence, y, x):
    directions = (((1, 0), (-1, 0)), ((1, 1), (-1, -1)), ((0, 1), (0, -1)), ((-1, 1), (1, -1)))
    state = [[[None if not (i == 0 or j == 0 or i == x + 1 or j == x + 1) else 0
    for i in range(x + 2)] for j in range(y + 2)] for k in range(4)]
    points = [0 for i in range(4)]

    
    for i, j in enumerate(move_sequence):
        y, x, z = j
        update(state, y + 1, x + 1, points, directions, i)
        


ai([], 6, 6)
for n in range(10):
    print()

a = [[None for i in range(7)]]
points_diff = [0, 0, 0, 0]
update_one_board(a, 0, 2, points_diff, ((0, 1), (0, -1)), 1, 1, change=True)
update_one_board(a, 0, 1, points_diff, ((0, 1), (0, -1)), 1, 1, change=True)
update_one_board(a, 0, 3, points_diff, ((0, 1), (0, -1)), -1, -1, change=True)

print(a, points_diff)
