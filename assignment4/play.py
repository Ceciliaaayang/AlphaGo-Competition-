import pexpect
from timeit import default_timer as timer

#player2='flat_mc_player/Gomoku3.py'
player1='gomoku4/Gomoku4.py'
player2 = 'pure_mcts_player/Gomoku_mcts.py'
# player2='random_player/Gomoku2.py'
# player2 = 'a3_player/Gomoku3.py'

win1=0
win2=0
numTimeout=0
draw=0
timeout=60
result_output_filename = "result_a3_a4.txt"

def getMove(p,color):
    p.sendline('genmove '+color)
    p.expect([pexpect.TIMEOUT,'= [A-Z][0-9]','= resign','= pass'])
    if p.after==pexpect.TIMEOUT:
        return 'timeout'
    return p.after.decode("utf-8")[2:]

def playMove(p,color,move):
    p.sendline('play '+color+' '+move)

def printToFile(anything):
    with open(result_output_filename, "a") as f:
        f.write(anything)

def showBoard(ob):
    ob.sendline('showboard')
    # ob.expect('\r\n')
    ob.expect('.*\$')
    print(ob.before.decode("utf-8"))

def setupPlayer(p):
    p.sendline('boardsize 7')
    p.sendline('clear_board')
    p.sendline('timelimit {}'.format(timeout))

def playSingleGame(alternative=False):
    if not alternative:
        p1=pexpect.spawn('python3 '+player1,timeout=timeout+1)
        p2=pexpect.spawn('python3 '+player2,timeout=timeout+1)
    else:
        p1=pexpect.spawn('python3 '+player2,timeout=timeout+1)
        p2=pexpect.spawn('python3 '+player1,timeout=timeout+1)
    ob=pexpect.spawn('python3 random_player/Gomoku2.py')
    setupPlayer(p1)
    setupPlayer(p2)
    result=None
    numTimeout=0
    sw=0
    while 1:
        if sw==0:
            start_p1 = timer()
            move=getMove(p1,'b')
            end_p1 = timer()
            time_p1 = end_p1 - start_p1
            assert(move!='pass')
            if move=='resign':
                result=2
                break
            elif move=='timeout':
                result=2
                break
            playMove(p2,'b',move)
            playMove(ob,'b',move)
        else:
            start_p2 = timer()
            move=getMove(p2,'w')
            end_p2 = timer()
            time_p2 = end_p2 - start_p2
            assert(move!='pass')
            if move=='resign':
                result=1
                break
            elif move=='timeout':
                result=1
                break
            playMove(p1,'w',move)
            playMove(ob,'w',move)
        if sw == 0:
            print(move, 'b', " time= ", time_p1, '\n')
            printToFile(move + " " + 'b' + " time=" + str(time_p1)  + '\n')
        else:
            print(move, 'w', " time= ", time_p2, '\n')
            printToFile(move + " " + 'w' + " time=" + str(time_p2) + '\n')
        sw=1-sw
        # print(move)
        ob.sendline('gogui-rules_final_result')
        ob.expect(['= black','= white','= draw','= unknown'])
        status=ob.after.decode("utf-8")[2:]
        if status=='black':
            result=1
            break
        elif status=='white':
            result=2
            break
        elif status=='draw':
            result=0
            break
        else:
            assert(status=='unknown')
    return result,numTimeout

def playGames(numGame=10):
    global win1,win2,draw,numTimeout
    for i in range(0,numGame):
        if(i<numGame/2):
            alter=False
        else:
            alter=True
        result,timeout=playSingleGame(alternative=alter)
        if timeout>0:
            numTimeout+=1
        else:
            if result==0:
                print("Game{}: {}\n".format(i, "draw"))
                printToFile("Game{}: {}\n".format(i, "draw"))
                draw+=1
            else:
                if result==1 and alter==False or result==2 and alter==True:
                    print("Game{}: {}\n".format(i, "player1 win"))
                    printToFile("Game{}: {}\n".format(i, "player1 win"))
                    win1+=1
                else:
                    assert(result==1 and alter==True or result==2 and alter==False)
                    print("Game{}: {}\n".format(i, "player2 win"))
                    printToFile("Game{}: {}\n".format(i, "player2 win"))
                    win2+=1

def outputResult():
    print('player1 win',win1,'player2 win',win2,'draw',draw)

def saveResult():
    f = open("game_results.txt", "w")
    f.write("player 1: {}\n".format(player1))
    f.write("player 2: {}\n".format(player2))
    f.write("player 1 wins {}\n".format(win1))
    f.write("player 2 wins {}\n".format(win2))
    f.write("draw {}\n".format(draw))
    f.close()

playGames()
outputResult()
saveResult()


