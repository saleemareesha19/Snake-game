import curses
import random
import time
import os
import sys

# HIGH SCORE FIX V4: Script wali folder mein file banao
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HIGHSCORE_FILE = os.path.join(SCRIPT_DIR, "highscore.txt")

def load_highscore():
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip() or 0)
    except:
        pass
    return 0

def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except Exception as e:
        pass

def game_loop(stdscr):
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()

    if sh < 22 or sw < 60:
        return "SMALL_SCREEN"

    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)
    w.timeout(100)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    w.attron(curses.color_pair(3))
    w.border()
    w.attroff(curses.color_pair(3))

    snk_x = sw//4
    snk_y = sh//2
    snake = [[snk_y, snk_x], [snk_y, snk_x-1], [snk_y, snk_x-2]]
    food = [sh//2, sw//2]
    w.addch(food[0], food[1], '*', curses.color_pair(2))

    key = curses.KEY_RIGHT
    score = 0
    highscore = load_highscore()

    while True:
        w.addstr(1, 2, f' Score: {score} ', curses.color_pair(4) | curses.A_BOLD)
        w.addstr(1, sw-22, f' High Score: {highscore} ', curses.color_pair(4) | curses.A_BOLD)
        w.addstr(sh-2, 2, ' Q:Quit Arrows:Move ', curses.color_pair(3))

        next_key = w.getch()
        key = key if next_key == -1 else next_key
        if key == ord('q'):
            return "QUIT", score, highscore

        prev_key = key
        if next_key in [curses.KEY_DOWN, curses.KEY_UP, curses.KEY_LEFT, curses.KEY_RIGHT]:
            if (prev_key == curses.KEY_DOWN and next_key == curses.KEY_UP) or \
               (prev_key == curses.KEY_UP and next_key == curses.KEY_DOWN) or \
               (prev_key == curses.KEY_LEFT and next_key == curses.KEY_RIGHT) or \
               (prev_key == curses.KEY_RIGHT and next_key == curses.KEY_LEFT):
                key = prev_key
            else: key = next_key

        new_head = [snake[0][0], snake[0][1]]
        if key == curses.KEY_DOWN: new_head[0] += 1
        if key == curses.KEY_UP: new_head[0] -= 1
        if key == curses.KEY_LEFT: new_head[1] -= 1
        if key == curses.KEY_RIGHT: new_head[1] += 1
        if key in [curses.KEY_UP, curses.KEY_DOWN]: time.sleep(0.03)

        snake.insert(0, new_head)

        # GAME OVER FIX V4
        if (snake[0][0] < 1 or snake[0][0] > sh-2 or
            snake[0][1] < 1 or snake[0][1] > sw-2 or
            snake[0] in snake[1:]):

            # HIGH SCORE SAVE KARO
            new_record = False
            if score > highscore:
                highscore = score
                save_highscore(highscore)
                new_record = True

            # Data return karo, drawing main() mein hogi
            return "GAMEOVER", score, highscore, new_record

        if snake[0] == food:
            score += 10
            if score > highscore: highscore = score
            food = None
            while food is None:
                nf = [random.randint(2, sh-3), random.randint(2, sw-3)]
                if nf not in snake: food = nf
            w.addch(food[0], food[1], '*', curses.color_pair(2))
            new_timeout = max(25, 100 - (score//8)*6)
            w.timeout(new_timeout)
        else:
            tail = snake.pop()
            w.addch(tail[0], tail[1], ' ')

        w.addch(snake[0][0], snake[0][1], 'O', curses.color_pair(1) | curses.A_BOLD)
        if len(snake) > 1: w.addch(snake[1][0], snake[1][1], 'o', curses.color_pair(1))

def main():
    result = curses.wrapper(game_loop)

    # CURSES KHATAM HONE KE BAAD GAME OVER PRINT KARO
    if result == "SMALL_SCREEN":
        print("ERROR: CMD window choti hai! Alt+Enter daba ke fullscreen karo.")
        input("Press Enter to exit...")
        return

    if isinstance(result, tuple) and result[0] == "GAMEOVER":
        _, score, highscore, new_record = result
        print("\n" + "="*40)
        print(" G A M E O V E R")
        print("="*40)
        if new_record:
            print(f" *** NEW HIGH SCORE: {score} ***")
        else:
            print(f" Final Score: {score}")
            print(f" High Score: {highscore}")
        print("="*40)
        input("\nPress Enter to exit...") # AB YE RUKAY GA 100%

    elif isinstance(result, tuple) and result[0] == "QUIT":
        print("\nGame quit kiya. Bye!")
        time.sleep(1)

if __name__ == "__main__":
    main()