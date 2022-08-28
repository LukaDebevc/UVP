import random

# najzanimivejsi del projektne naloge
def n_th_stone(n):
    return {1: -1, 2: 0}.get(n, 0 if (n + 1) % 2 == 0 else 1 - (n % 4))


def n_th_color(n):
    return 1 - 2 * ((n % 4) // 2) if n != 1 else -1


def all_possible_moves(state):
    return [
        (i, j)
        for i in range(1, len(state[0]) - 1)
        for j in range(1, len(state[0][0]) - 1)
        if state[0][i][j] is None
    ]


def update(state, y, x, points, directions, n, change=True):
    # to je treba še narediti
    stone = n_th_stone(n)
    color = n_th_color(n)
    for i in range(4):
        update_one_board(
            state[i], y, x, points, directions[i], color, stone, change=change
        )


def update_one_board(board, y, x, points_diff, directions, color, stone, change=True):
    dy0, dx0 = directions[0]
    dy1, dx1 = directions[1]

    a0 = board[y + dy0][x + dx0]
    a1 = board[y + dy1][x + dx1]
    # if type(a0) == type((0,)) or type(a1) == type((0,)):
    #    print(a0, a1, board, directions, y, x)

    k0 = 0 if a0 is None else a0 * stone
    k1 = 0 if a1 is None else a1 * stone

    stones_in_seq = 1
    if k0 > 0:
        stones_in_seq += k0
    if k1 > 0:
        stones_in_seq += k1

    ak0, ak1 = abs(k0), abs(k1)

    if k0 > 0 or k1 > 0:

        b0 = board[y + (k0 + 1) * dy0][x + (k0 + 1) * dx0]
        b1 = board[y + (k1 + 1) * dy1][x + (k1 + 1) * dx1]

        if k0 > 0 and k1 > 0:

            points_diff[color] -= ak0 + ak1
            points_diff[1 - color] += (
                stones_in_seq * (stones_in_seq - 1) - ak0 * (ak0 - 1) - ak1 * (ak1 - 1)
            ) // 2
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


def undo(state, move, points, directions):
    y, x, diff, z = move
    # points = [i - j for i, j in zip(points, diff)]
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
            if not k:  # abs(k) == 1 or :
                pass
            elif (
                0 if board[y + dy0][x + dx0] is None else board[y + dy0][x + dx0]
            ) * k > 0:
                board[y + (abs(k) - 1) * dy0][x + (abs(k) - 1) * dx0] = (
                    k - 1 if k > 0 else k + 1
                )
            elif k:
                board[y + (abs(k) - 1) * dy1][x + (abs(k) - 1) * dx1] = (
                    k - 1 if k > 0 else k + 1
                )

        board[y][x] = None


def search(
    state,
    n_th_move,
    points,
    directions,
    d=0,
    num_of_moves=(1,),
    difficulty=10,
    factor=0,
):
    ans0 = []
    color = n_th_color(n_th_move)
    for y, x in all_possible_moves(state):
        diff = [0 for i in range(4)]
        update(state, y, x, diff, directions, n_th_move, change=False)
        p = (diff[0] * (2 + factor) + diff[1] - diff[2] * (2 + factor) - diff[3]) + color * (
            min(y, len(state[0]) - 1 - y) / len(state[0])
            + min(x, len(state[0][0]) - 1 - x) / len(state[0][0])
        )

        ans0.append([y, x, diff, p])

    # random pop
    if difficulty != 10:
        random.shuffle(ans0)
        for i in range(int(len(ans0) * 0.05 * (10 - difficulty))):
            ans0.pop()

    ans0.sort(key=lambda x: -color * x[-1])
    ans0 = ans0[: num_of_moves[d]]
    if (not d) or len(ans0) == 1:
        ans0[0][-1] = (p_0 := sum(a[-1] for a in ans0) / len(ans0))
        return [p_0, [ans0[0]]]

    ans1 = []
    for i in ans0:
        update(state, i[0], i[1], [0, 0, 0, 0], directions, n_th_move, change=True)
        # print([i + j for i, j in zip(points, i[2])])
        path = search(
            state,
            n_th_move + 1,
            [i + j for i, j in zip(points, i[2])],
            directions,
            d=d - 1,
            num_of_moves=num_of_moves,
            difficulty=difficulty,
            factor=factor,
        )
        path[-1].append(i)
        path[0] += i[-1]
        ans1.append(path)
        undo(state, i, points, directions)

    ans1.sort(key=lambda x: -color * x[0])
    return ans1[0]


def ai(move_sequence, y_dim, x_dim, difficulty):
    print("AI..dela")
    directions = (
        ((1, 0), (-1, 0)),
        ((1, 1), (-1, -1)),
        ((0, 1), (0, -1)),
        ((-1, 1), (1, -1)),
    )

    num_of_moves_dict = {
        1: (5, 3, 3),
        2: (5, 4, 3),
        3: (6, 4, 3),
        4: (6, 4, 3, 3),
        5: (7, 4, 3, 3),
        6: (7, 4, 3, 3, 3),
        7: (7, 4, 3, 3, 3, 3),
        8: (8, 4, 3, 3, 3, 3),
        9: (8, 4, 3, 3, 3, 3, 3),
        10: (8, 5, 4, 4, 4, 3, 3, 3),
    }

    state = [
        [
            [
                None
                if not (i == 0 or j == 0 or i == x_dim + 1 or j == y_dim + 1)
                else 0
                for i in range(x_dim + 2)
            ]
            for j in range(y_dim + 2)
        ]
        for k in range(4)
    ]
    points = [0 for i in range(4)]

    for i, j in enumerate(move_sequence):
        y, x, z = j
        update(state, y + 1, x + 1, points, directions, i)

    p = search(
        state,
        len(move_sequence),
        points,
        directions,
        len(num_of_moves_dict[difficulty]) - 1,
        num_of_moves_dict[difficulty],
        difficulty,
        len(move_sequence) / x_dim / y_dim,
    )
    re = []
    color = n_th_color(len(move_sequence))
    print(p)
    for i, j in enumerate(reversed(p[1])):
        print(i)
        if color == n_th_color(len(move_sequence) + i):
            re.append((j[0] - 1, j[1] - 1))
        else:
            break
    return list(reversed(re))
