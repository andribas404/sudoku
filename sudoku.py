import copy

SIZE = 9
MASK = 0x1ff
mboard = []
solution = []
state = []
ONEBIT = [1 << x for x in range(SIZE)]


class NoChoice(Exception):
    pass


def print_solution():
    global SIZE
    global solution, mboard
    for i in range(SIZE + 1):
        if i % 3 == 0:
            print(''.join(('-') * (SIZE + 4)))
        if i == SIZE:
            break
        for j in range(SIZE):
            if j % 3 == 0:
                print('|', end='')
#            print('.', end='')
            print(solution[i][j], end='')
        print('|')
    '''
    for i in range(SIZE + 1):
        if i % 3 == 0:
            print(''.join(('-') * (SIZE + 4)))
        if i == SIZE:
            break
        for j in range(SIZE):
            if j % 3 == 0:
                print('|', end='')
#            print('.', end='')
            print ("{0:09b}".format(mboard[i][j]), end='|')
        print('|')
    '''


def check_solution():
    global SIZE, MASK
    global solution

    checksum = [[0] * SIZE] * 3
    result = True

    for i in range(SIZE):
        for j in range(SIZE):
            checksum[0][i] |= 1 << (solution[i][j] - 1)
            checksum[1][j] |= 1 << (solution[i][j] - 1)
            region = i // 3 * 3 + j // 3
            checksum[1][region] |= 1 << (solution[i][j] - 1)

    for i in range(3):
        for j in range(SIZE):
            if checksum[i][j] != MASK:
                "Error in checksum[{i}][{j}]".format(i=i, j=j)
                result = False

    print ("Check ", end='')
    if result:
        print("[OK]")
    else:
        print("[Failed]")


def is_onebit(bit):
    if bit in ONEBIT:
        return ONEBIT.index(bit)
    else:
        return -1


def get_bit(m):
    global SIZE
    b = 0
    while m > 0:
        m >>= 1
        b += 1

    return b - 1


def check(i, j, d, stack):
    global solution, SIZE, mboard
    if solution[i][j] != 0:
        return -1
    oldm = mboard[i][j]
    if oldm == 0:
        raise NoChoice()
    mboard[i][j] = mboard[i][j] & (~mboard[d[0]][d[1]])
    if oldm == mboard[i][j]:
        return -1

    b = is_onebit(mboard[i][j])
    if b >= 0:
        stack.append([i, j, b + 1])
    return b


def apply_digit(d, stack):
    ''' add mask to line, column and region
        if mask is 1 bit - add to stack
    '''
    global solution, SIZE, mboard
    if mboard[d[0]][d[1]] & (1 << (d[2] - 1)) == 0:
        return 0
    mboard[d[0]][d[1]] = 1 << (d[2] - 1)
    solution[d[0]][d[1]] = d[2]
#    print (d)
    try:
        for i in range(SIZE):
            check(d[0], i, d, stack)
            check(i, d[1], d, stack)

        for i in range((d[0] // 3) * 3, (d[0] // 3 + 1) * 3):
            for j in range((d[1] // 3) * 3, (d[1] // 3 + 1) * 3):
                check(i, j, d, stack)
    except NoChoice:
        #print(d)
        return 0

    return 1


def get_unique(d):
    global SIZE, solution, mboard
    m = mboard[d[0]][d[1]]
    mboard[d[0]][d[1]] = ~m
    mu= [m] * 3
    for i in range(SIZE):
        mu[0] = mu[0] & (~mboard[d[0]][i])
        mu[1] = mu[1] & (~mboard[i][d[1]])

    for i in range((d[0] // 3) * 3, (d[0] // 3 + 1) * 3):
        for j in range((d[1] // 3) * 3, (d[1] // 3 + 1) * 3):
            mu[2] = mu[2] & (~mboard[i][j])

    mboard[d[0]][d[1]] = m

    for i in range(3):
        u = is_onebit(mu[i]) + 1
        if u > 0:
            return u

    return 0


def guess():
    global SIZE, solution
    for i in range(SIZE):
        for j in range(SIZE):
            if solution[i][j] == 0:
                return [i, j]
    return [-1, -1]


def save_state(stack):
    global solution, mboard, state
    d = guess()
    m = copy.deepcopy(mboard)
    s = copy.deepcopy(solution)
    b = get_bit(mboard[d[0]][d[1]])
    if b < 0:
        restore_state(stack)
        print("Restored in SAVE state with ", len(state), " in state stack")
        return save_state(stack)
    m[d[0]][d[1]] = m[d[0]][d[1]] & (~ (1 << b))
    stack.append([d[0], d[1], b + 1])
    state.append([m, s])


def restore_state(stack):
    global solution, mboard, state
    while stack:
        stack.pop()
    s = state.pop()
    mboard = copy.deepcopy(s[0])
    solution = copy.deepcopy(s[1])


def get_solved():
    global SIZE, solution
    solved = 0
    for i in range(SIZE):
        for j in range(SIZE):
            if solution[i][j] > 0:
                solved += 1

    return solved


def solve(table):
    global MASK, SIZE, mboard, solution
    print("Table")
    t = [[0 for x in range(SIZE)] for y in range(SIZE)]
    i = 0
    stack = []
    for str in table:
        j = 0
        for ch in str:
            if ch in ('-', '|', '\n'):
                continue
            else:
                if ch == ' ':
                    t[i][j] = 0
                else:
                    t[i][j] = int(ch)
                    stack.append([i, j, t[i][j]])
                j += 1
        if str[0] != '-':
            i += 1

    mboard = [[MASK for x in range(SIZE)] for y in range(SIZE)]
    solution = [[0 for x in range(SIZE)] for y in range(SIZE)]
    solved = 0
    oldsolved = 0
    while solved < SIZE ** 2:
        while stack:
            digit = stack.pop()
            if solution[digit[0]][digit[1]] == 0:
                solved += 1
                if not apply_digit(digit, stack):
                    restore_state(stack)
                    solved = get_solved()
                    print("Restored state with ", solved, "solved")

        for i in range(SIZE):
            for j in range(SIZE):
                if solution[i][j] > 0:
                    continue
                u = get_unique([i, j])
                if u > 0:
                    stack.append([i, j, u])

        if not stack and solved == oldsolved:
            if solved == SIZE ** 2:
                break
#           guess with stack  need to catch error
#            break
            print("Saved state with ", solved, "solved")
            save_state(stack)
            solved = get_solved()

        oldsolved = solved


def main():
    table = []
    with open('sudoku1.txt') as f:
        for line in f:
            if line == '\n':
                solve(table)
                check_solution()
                print_solution()
                table = []
                continue

            table.append(line)

    solve(table)
    check_solution()
    print_solution()


main()
