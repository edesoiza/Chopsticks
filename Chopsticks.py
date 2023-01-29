import json
from os import system

class Hand:
    def __init__(self):
        self.fingers = 1
        self.active = True
        self.game_mode = None

    def addToCount(self, fingers):
        if not self.active:
            raise Exception("Hand is not active")

        self.fingers += fingers
        self.checkMax()

    def checkMax(self):
        if self.game_mode == "standard":
            if self.fingers >= 5:
                self.killHand()
        elif self.game_mode == "rollover":
            if self.fingers == 5:
                self.killHand()
            else:
                self.fingers = self.fingers % 5
        elif self.game_mode == "game of five":
            if self.fingers > 5:
                self.killHand()

    def killHand(self):
        self.setFingers(0)
        self.active = False

    def subFromCount(self, fingers):
        if self.fingers < fingers:
            raise Exception("not enough fingers to take")
        self.fingers -= fingers

    def setFingers(self, count):
        self.fingers = count
        self.active = self.fingers != 0

class Player:
    def __init__(self):
        self.left_hand = Hand()
        self.right_hand = Hand()
        self.chopstick_sum = self.left_hand.fingers + self.right_hand.fingers

    def splitHands(self, left, right):
        self.updateSum()

        if not self.left_hand.active or not self.left_hand.active:
            raise Exception("Can't split into a dead hand")

        if left + right != self.chopstick_sum:
            raise Exception("split sum does not match hand sum")

        if left == self.left_hand.fingers and right == self.right_hand.fingers:
            raise Exception("split is identical to current hands")

        self.left_hand.setFingers(left)
        self.right_hand.setFingers(right)

    def updateSum(self):
        self.chopstick_sum = self.left_hand.fingers + self.right_hand.fingers

    def updateGamemode(self, variation):
        self.left_hand.game_mode = variation
        self.right_hand.game_mode = variation

class Game:
    def __init__(self):
        self.game_mode = None
        self.player1 = Player()
        self.player2 = Player()
        self.player_dict = {1:self.player1, 0:self.player2}
        self.mod_to_player = {1:"player1", 0:"player2"}
        self.valid_actions = {"split":self.splitAction, "attack":self.attackAction, "save": self.saveMatch, "quit": self.quitMatch}
        self.winner = None
        self.turn = 1
        self.current_player = self.player_dict[self.turn % 2]
        self.opposing_player = self.player_dict[(self.turn + 1) % 2]
        
    def start(self):
        system("clear")
        print("welcome to Eric's Chopsticks Game!")
        print("Would you like to play a new game or load a save?")
        print("Options: \nNew \nLoad")

        save_choices = {"load": self.loadSave, "new": self.newSave}
        game_save_choice = input().lower()

        if game_save_choice not in save_choices:
            print("Invalid choice, Please type New or Load")
            self.start()

        save_choices[game_save_choice]()

    def newSave(self):
        print("A new game! How fun")
        print("What game mode would you like to play?")
        print("Options: \nStandard \nRollover \nGame of Five")
        game_variations = {"standard", "rollover", "game of five"}
        variation_choice = input().lower()

        if variation_choice not in game_variations:
            print("invalid variation choice, currently")
            print("Your options are {}".format(game_variations.items()))
            self.newSave()
        
        self.updateGamemode(variation_choice)
        self.play()

    def loadSave(self):
        print("please provide your save ID:")
        game_id = input()

        with open("game_saves.json") as f:
            json_copy = json.load(f)[game_id]

        self.updateGamemode(json_copy["game_mode"])
        self.turn = json_copy["turn"]

        self.current_player = self.player_dict[self.turn % 2]
        self.current_player.left_hand.fingers = json_copy["current_left"]
        self.current_player.right_hand.fingers = json_copy["current_right"]

        self.opposing_player = self.player_dict[(self.turn + 1) % 2]
        self.opposing_player.left_hand.fingers = json_copy["opposing_left"]
        self.opposing_player.right_hand.fingers = json_copy["opposing_right"]
        self.play()
    
    def updateGamemode(self,variation):
        self.player1.updateGamemode(variation)
        self.player2.updateGamemode(variation)

    def play(self):
        self.displayBoard()
        print("the current turn is {}".format(self.turn))
        print("the current player is {}".format(self.mod_to_player[self.turn % 2]))
        print("would you like to split or attack?")
        print("You can also quit or save the game :)")
        action_response = input().lower()

        if action_response not in self.valid_actions:
            print("Invalid Action")
            print("please type any of the following: Split/Attack/Save/Quit")
            self.play()
        self.valid_actions[action_response]()

    def displayBoard(self):
        system('clear')
        print("jezz", self.current_player.right_hand.game_mode)
        c = self.current_player
        o = self.opposing_player
        print(self.game_mode)
        print("Opposing Hands:")
        print("L , R")
        print("{} , {}".format(o.left_hand.fingers, o.right_hand.fingers))
        print("Your Hands:")
        print("L , R")
        print("{} , {}".format(c.left_hand.fingers, c.right_hand.fingers))

    def splitAction(self):
        print("how would you like to split your hands?")
        print("please provide in Left,Right form")
        values = input().split(",")
        print(values)
        try:
            self.current_player.splitHands(int(values[0]), int(values[1]))
        except:
            self.splitAction()
        self.updateTurns()
    
    def attackAction(self):
        print("Would you like to use your Left or Right Hand?")
        print("Please type Left or Right")
        current_choice = input().lower()
        self.checkAttackInput(current_choice)

        print("Which hand would you like to hit?")
        opposing_choice = input().lower()
        self.checkAttackInput(opposing_choice)

        c_hands = self.current_player
        o_hands = self.opposing_player

        c_hand_choice = {"left":c_hands.left_hand, "right":c_hands.right_hand}
        o_hand_choice = {"left":o_hands.left_hand, "right":o_hands.right_hand}

        your_hand_count = c_hand_choice[current_choice].fingers
        o_hand_choice[opposing_choice].addToCount(your_hand_count)

        self.updateTurns()

    def checkAttackInput(self, hand):
        if hand != "left" and hand != "right":
            print("invalid input for hand choice. Please Try Again")
            self.attackAction()

    def updateTurns(self):
        self.player1.updateSum()
        self.player2.updateSum()

        self.current_player = self.player_dict[(self.turn+1) % 2]
        self.opposing_player = self.player_dict[(self.turn) % 2]

        self.checkForWinner()

    def saveMatch(self):
        print("what ID would you like to give this game?")
        print("provide a string :)")
        self.game_id = input()

        with open("game_saves.json") as f:
            json_copy = json.load(f)

        c = self.current_player
        o = self.opposing_player
        json_copy[self.game_id] = {}
        json_copy[self.game_id]["game_mode"] = self.game_mode
        json_copy[self.game_id]["turn"] = self.turn
        json_copy[self.game_id]["current_left"] = c.left_hand.fingers
        json_copy[self.game_id]["current_right"] = c.right_hand.fingers
        json_copy[self.game_id]["opposing_left"] = o.left_hand.fingers
        json_copy[self.game_id]["opposing_right"] = o.right_hand.fingers

        with open("game_saves.json", 'w') as f:
            json.dump(json_copy, f)
        
        print("save completed!")
        quit()

    def quitMatch(self):
        self.turn += 1
        print("It's okay to lose!")
        self.congratulate()

    def checkForWinner(self):
        system('clear')
        if self.current_player.chopstick_sum != 0:
            self.turn += 1
            self.play()

        self.congratulate()

    def congratulate(self):
        print("The Winner is {}!!!".format(self.mod_to_player[self.turn % 2]))
        quit()


if __name__ == "__main__":
    chopsticks = Game()
    chopsticks.start()

