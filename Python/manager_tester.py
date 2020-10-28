if __name__ == "__main__":
    runner = Planner()
    map = [[True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True]]
    runner.set_new_plate(map)
    runner.main_loop()
    runner.main_loop()
    runner.main_loop()
    runner.main_loop()
    runner.current_plate.print_out_map()

    