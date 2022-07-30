import cmd_parser as parser
from actions import *
from router import *
import multiprocessing as mp
from queue import Empty
import threading, time


ORANGE = (255, 150, 100)
WHITE = (255, 255, 255)
BLUE = (5, 180, 255)
GREEN = (0, 240, 10)
BLACK = (0, 0, 0)
ws = 720  # window size


def display(display_queue: mp.Queue):
    import pygame
    pygame.init()
    sc = pygame.display.set_mode((ws, ws))
    sc.fill(WHITE)
    radius_size = 30
    font = pygame.font.Font(None, 45)
    display_queue.put('init')

    while True:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                return

        try:
            [rml, edge_list]  = display_queue.get(timeout=0.9)  # rml means routers_meta_list
            #draw lines
            for edges in edge_list:
                pygame.draw.line(sc, BLACK, (ws * rml[edges[0]].x, ws * rml[edges[0]].y),
                                 (ws * rml[edges[1]].x, ws * rml[edges[1]].y)
                )
            #draw circles
            for meta in rml:
                router_color = ORANGE
                if meta.state == RouterStateType.FinishNode:
                    router_color = GREEN
                elif meta.state == RouterStateType.Transits:
                    router_color = BLUE

                pygame.draw.circle(sc, router_color, (
                    int(meta.x * ws),
                    int(meta.y * ws)),
                    radius_size
                )
                text = font.render(str(meta.id), 1, (10, 0, 0))
                sc.blit(text, (int(meta.x * ws - radius_size // 3), int(meta.y * ws - radius_size // 3)))
        except Empty:
            pass

        pygame.display.update()

key = ''
read_input = False

def input_thread():
    global key
    global read_input
    lock = threading.Lock()
    while True:
        with lock:
            key = input()
            read_input = True
            if key.__eq__('exit'):
                break

if __name__ == "__main__":
    net = Net()
    display_queue = mp.Queue()  # for update display
    display_process = mp.Process(target=display, args=(display_queue,))
    display_process.start()
    display_queue.get()  # waiting for pygame loads in display process

    input_thread = threading.Thread(target=input_thread)
    input_thread.start()

    while True:
        if read_input and key != '':
            read_input = False
            action = parser.cmd_parse(key)
            if action.actionType == ActionType.Exit:
                break
            action.start(net)

        routers_meta_list = []
        net.update_states()
        for router in net.routers.values():
            routers_meta_list.insert(router.meta.id, router.meta)

        display_queue.put([routers_meta_list, net.edge_list])

        time.sleep(0.9)

    display_process.terminate()
    net.terminate()
    