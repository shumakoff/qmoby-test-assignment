from random import randint


def generate_shots():
    vacant_id = 0
    map_row = [vacant_id] * 10
    map_arr = [map_row.copy() for x in range(10)]
    return map_arr


def generate_map():
    vacant_id = 0
    ship_id = 1
    map_row = [vacant_id] * 10
    map_arr = [map_row.copy() for x in range(10)]
    ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
    ship_sizes = [4]
    for i in range(len(ship_sizes)):
        ship_size = ship_sizes[i]
        ship_direction = randint(0, 1)  # 0 for horizontal, 1 for vertical
        ship_placed = False
        while not ship_placed:
            # pick a random location
            x_cor = randint(0, len(map_row) - 1)
            y_cor = randint(0, len(map_arr) - 1)
            #print(f'checking for coordinates {x_cor}, {y_cor}')
            # check if it's free
            if map_arr[y_cor][x_cor] == vacant_id:
                # check if there's enough space to place a ship
                # if it's a one cell ship we can place it without any extra checks
                # but not really, better check if there's any adjacent ships
                if ship_size == 1:
                    try:
                        if map_arr[y_cor][x_cor-1] or map_arr[y_cor][x_cor+1] \
                            or map_arr[y_cor+1][x_cor] or map_arr[y_cor-1][x_cor] \
                            or map_arr[y_cor-1][x_cor-1] or map_arr[y_cor-1][x_cor+1] \
                            or map_arr[y_cor+1][x_cor-1] or map_arr[y_cor+1][x_cor+1]:
                            continue
                    except IndexError:
                        continue
                    map_arr[y_cor][x_cor] = ship_id
                    ship_placed = True
                    #print(f'ship {ship_size}-{ship_direction} placed at {x_cor},{y_cor}')
                    break
                # for horizontal placement
                if ship_direction == 0:
                    direction = check_space(map_arr, vacant_id, y_cor, x_cor, ship_size, ship_direction)
                    if direction:
                        # place the ship
                        for x in range(ship_size):
                            x *= direction
                            map_arr[y_cor][x_cor + x] = ship_id
                        ship_placed = True
                        #print(f'ship {ship_size}-{ship_direction} placed at {x_cor},{y_cor}')
                    else:
                        continue
                # for vertical placement
                else:
                    direction = check_space(map_arr, vacant_id, y_cor, x_cor, ship_size, ship_direction)
                    if direction:
                        # place the ship
                        for x in range(ship_size):
                            x *= direction
                            map_arr[y_cor + x][x_cor] = ship_id
                        ship_placed = True
                        #print(f'ship {ship_size}-{ship_direction} placed at {x_cor},{y_cor}')
                    else:
                        continue

    return map_arr


def check_space(map_arr, vacant_id, y_cor, x_cor, ship_size, ship_direction):
    # check if there's enough space to place a ship
    space_found = False
    while not space_found:
        if ship_direction == 0:
            # checking horizontally
            checked_horizontally = False
            checked_left, checked_right = False, False
            while not checked_horizontally:
                # if we at 0 coordinate on X
                # then there's no point in checking left
                if x_cor == 0:
                    checked_left = True
                if ((x_cor + ship_size + 1) > len(map_arr[0])) or ((x_cor - ship_size) < 0):
                    checked_horizontally = True
                    continue
                if not checked_left:
                    checking_direction = -1
                else:
                    checking_direction = 1
                for idx in range(ship_size+1):
                    idx *= checking_direction
                    if map_arr[y_cor][x_cor + idx] == vacant_id:
                        continue
                    else:
                        # there's a ship in this position
                        # check if we already checked everything to the left
                        if checked_left:
                            # if we are that means there's no mor options
                            checked_horizontally = True
                            break
                        else:
                            # that's the first pass, we checked everything to the left
                            # and there was a ship
                            checked_left = True
                            break
                else:
                    space_found = True
                    checked_horizontally = True
        else:
            # checking vertically
            checked_vertically = False
            checked_up, checked_down = False, False
            while not checked_vertically:
                # if we at 0 coordinate on X
                # then there's no point in checking left
                if y_cor == 0:
                    checked_up = True
                if ((y_cor + ship_size + 1) > len(map_arr[0])) or ((y_cor - ship_size) < 0):
                    checked_vertically = True
                    continue
                if not checked_up:
                    checking_direction = -1
                else:
                    checking_direction = 1
                for idx in range(ship_size+1):
                    idx *= checking_direction
                    if map_arr[y_cor + idx][x_cor] == vacant_id:
                        continue
                    else:
                        if checked_up:
                            checked_vertically = True
                            break
                        else:
                            checked_up = True
                            break
                else:
                    space_found = True
                    checked_vertically = True

        if space_found:
            return checking_direction
        return False
