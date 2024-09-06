from random import randint
import uuid
import math
import os

# ADJUSTEMENTS

STARTING_CASH = 1000
ROUNDS = 2
TURN_ACTIONS = 3

CASH_COST_STEAL_PLAYER = 50
CASH_COST_STEAL_BUSINESS = 200

ACTION_COST_INVEST = 1
ACTION_COST_WITHDRAW = 1
ACTION_COST_STEAL_PLAYER = 2
ACTION_COST_STEAL_BUSINESS = 3

PROFIT_RATE_HOTEL = 0.20
PROFIT_RATE_DRUGSTORE = 0.10
PROFIT_RATE_SUPERMARKET = 0.05

LEVELS_HOTEL        = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
LEVELS_DRUGSTORE    = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
LEVELS_SUPERMARKET  = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

DEFAULT_WITHDRAW_RATE = 0.1


class Message:

    colors = {
        'BLUE':'\033[94m',
        'GREEN':'\033[92m',
        'RED':'\033[91m',
        'YELLOW':'\033[93m',
        'PURPLE':'\033[95m',
        'LIGHT_BLUE':'\033[96m',
        'GRAY':'\033[0m',
        '':'\033[0m'
    }

    END = '\033[0m'

    
    @staticmethod
    def color(color, text):
        return Message.colors[color] + text + Message.END

    @staticmethod
    def print(color, message):
        print(Message.color(color, message))

    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def printScoreboard():
        players = {}
        for player in Player.list:
            players[player.name] = player.cash
        players = dict(sorted(players.items(), reverse=True, key=lambda item: item[1]))
        position = 1
        Message.print('GREEN', f"\n##### SCOREBOARD #####")
        for player in players:
            Message.print('GREEN', f"#{position} - ${players[player]} - {player}")
            position += 1
        Message.print('GREEN', f"######################\n")

    @staticmethod
    def printBusinessesStatus():
        Message.print('GREEN', f"\n##### BUSINESSES #####")
        for business in Business.list:
            Message.print('GREEN', f"${business.investments.getTotalInvestmentValue()} \t- (lvl {business.level}) - {business.getName()} ")
        Message.print('GREEN', f"######################\n")

    @staticmethod
    def printConfiguration():
        Message.print('PURPLE', f"Starting cash: {STARTING_CASH}\n" +
                                f"Rounds: {ROUNDS}\n" +
                                f"Turn actions: {TURN_ACTIONS}\n" +
                                f"Profit rate for Hotel: {PROFIT_RATE_HOTEL}\n" +
                                f"Profit rate for Drugstore: {PROFIT_RATE_DRUGSTORE}\n" +
                                f"Levels for Hotel: {LEVELS_HOTEL}\n" +
                                f"Levels for Drugstore: {LEVELS_DRUGSTORE}\n")
        
    @staticmethod
    def printPlayerInvestments(player):
        Message.print('GREEN', f"\n##### INVESTMENTS #####")
        for business in Business.list:
            if player.uid in business.investments.amounts:
                Message.print('GREEN', f"${business.investments.amounts[player.uid]}\t- {business.getName()} ")
        Message.print('GREEN', f"######################\n")



class Player:
    list = []

    def __init__(self, name):
        Player.list.append(self)
        self.cash = STARTING_CASH
        self.name = name
        self.uid = str(uuid.uuid4())
        Message.print('PURPLE', f"{self.__class__.__name__} created: \t{name} \t({self.uid})")

    def checkFunds(self, amount):
        if self.cash < amount:
            Message.print('RED', f"{self.name} tried to invest ${amount}, but failed due to insufficient funds.")
            return False
        return True

    def invest(self, business, amount):
        if not self.checkFunds(amount):
            return False
        if not business.invest(self, amount):
            return False
        self.cash -= amount
        return True

    def receiveCash(self, source, amount):
        self.cash += amount
        Message.print('GREEN', f"{self.name} received ${amount} from {source.getName()}")

    @staticmethod
    def getPlayerByUid(uid):
        for player in Player.list:
            if player.uid == uid:
                return player
        Message.print('', "Player not found")
        return False
    
    @staticmethod
    def getActionList():
        listing = []
        for index in range(len(Player.list)):
            listing.append(f"{index} - {Player.list[index].name}")
        return listing

class HumanPlayer(Player):
    pass

class AIPlayer(Player):
    pass



class Investments:

    def __init__(self, business):
        self.amounts = {}
        self.business = business

    def add(self, player, amount):
        Message.print('', player.name + " invested $" + str(amount) + " in " + self.business.name)
        if player.uid not in self.amounts:
            self.amounts[player.uid] = 0
        self.amounts[player.uid] += amount
        return True

    def getInvestments(self):
        amounts = self.amounts
        for index in amounts:
            player = Player.getPlayerByUid(index)
            Message.print('', player.name + "\t = " + str(amounts[index]))

    def getMajorInvestor(self):
        majorInvestor = None
        majorInvestment = 0

        for index in self.amounts:
            if self.amounts[index] > majorInvestment:
                majorInvestor = index
                majorInvestment = self.amounts[index]

        if majorInvestor:
            return Player.getPlayerByUid(majorInvestor)

        return None

    def getTotalInvestmentValue(self):
        total = 0
        for index in self.amounts:
            total += self.amounts[index]
        return total

class Business:

    list = []

    def __init__(self, name):

        Business.list.append(self)

        self.investments = Investments(self)
        self.level = 1
        self.name = name
        self.owner = None
        self.uid = str(uuid.uuid4())
        self.withdrawRate = DEFAULT_WITHDRAW_RATE

        Message.print('PURPLE', f"{self.getName()} created: \t{name}")

    def getName(self):
        return f"{self.__class__.__name__} {self.name}"

    def invest(self, player, amount):
        if self.investments.add(player, amount):
            newTotal = self.investments.getTotalInvestmentValue()
            Message.print('', f"New total investment value is ${newTotal}")
            self.checkOwnerChange()
            return True
        return False
    
    def checkOwnerChange(self):
        owner = self.investments.getMajorInvestor()
        if owner and owner != self.owner:
            self.owner = owner
            Message.print('YELLOW', f"New owner of {self.getName()} is {owner.name}")

    def generateProfit(self):
        if self.owner == None:
            Message.print('', f"{self.getName()} has no owner, therefore no profit is generated")
            return False
        profit = self.investments.getTotalInvestmentValue() * self.profit_rate
        profit = math.floor(profit)
        Message.print('', f"{self.getName()} generated ${profit} in profit")
        self.owner.receiveCash(self, profit)

    def checkLevelChange(self):

        totalInvestment = self.investments.getTotalInvestmentValue()
        newLevel = 1

        for level in range(1, len(self.levelsTable)):
            newLevel = level
            if totalInvestment < self.levelsTable[level]:
                break;

        if newLevel != self.level:
            self.level = newLevel
            Message.print('YELLOW', f"{self.getName()} is now level {self.level}")

    @staticmethod
    def getActionList():
        listing = []
        for index in range(len(Business.list)):
            listing.append(f"{index} - {Business.list[index].getName()}")
        return listing
    
    @staticmethod
    def getWithdrawList(player):
        listing = []
        for index in range(len(Business.list)):
            if player.uid in Business.list[index].investments.amounts:
                listing.append(f"{index} - {Business.list[index].getName()} (Rate: {int(Business.list[index].withdrawRate * 100)}%) - ${Business.list[index].investments.amounts[player.uid]}")
        return listing
    
    def withdraw(self, player, amount):
        if not self.investments.amounts[player.uid]:
            Message.print('RED', f"{player.name} can't withdraw from {self.getName()} as he/she has no investments in it.")
            return False
        if self.investments.amounts[player.uid] < amount:
            Message.print('RED', f"{player.name} can't withdraw ${amount} from {self.getName()} as he/she has only ${self.investments.amounts[player.uid]} invested in it.")
            return False
        self.investments.amounts[player.uid] -= amount
        Message.print('RED', f"{self.getName()} is down ${amount} in investments, the new total is ${self.investments.getTotalInvestmentValue()}")
        self.checkOwnerChange()
        player.receiveCash(self, amount * self.withdrawRate)
        return True
        


class Hotel(Business):
    def __init__(self, name):
        self.profit_rate = PROFIT_RATE_HOTEL
        self.levelsTable = LEVELS_HOTEL
        super().__init__(name)

class Drugstore(Business):
    def __init__(self, name):
        self.profit_rate = PROFIT_RATE_DRUGSTORE
        self.levelsTable = LEVELS_DRUGSTORE
        super().__init__(name)

class Supermarket(Business):
    def __init__(self, name):
        self.profit_rate = PROFIT_RATE_SUPERMARKET
        self.levelsTable = LEVELS_SUPERMARKET
        super().__init__(name)



class Round:

    number = 1

    def __init__(self, game):
        self.game = game
        Message.print('PURPLE', f"\n#### START ROUND {Round.number} ####\n")
        for player in Player.list:
            Turn(self, player)

    def __del__(self):
        Message.printBusinessesStatus()
        Message.printScoreboard()
        Game.generateProfits();
        Game.checkBusinessesLevels()
        Message.print('BLUE',f"#### END OF ROUND {Round.number} ####\n")
        Action.enterToContinue()
        Round.number += 1

class Turn:

    number = 1

    def __init__(self, round, player):
        self.actions = 0
        self.round = round
        self.player = player

        while self.actions < TURN_ACTIONS:
            action = Action(self)
            self.actions += action.mainAction()
        Turn.number += 1
        del self

    def getRemainingActions(self):
        return TURN_ACTIONS - self.actions

    def __del__(self):
        Message.print('GREEN', f"# End Turn #\n")

    @staticmethod
    def printTurnHeader(player):
        Message.print('PURPLE', f"#### {player.name} ####")



class Action:

    def __init__(self, turn):
        self.turn = turn
        self.player = turn.player

    def checkEnoughAp(self, apNeeded):
        if self.turn.getRemainingActions() < apNeeded:
            Message.print('RED', f"{self.player.name} doesn't have enough actions to perform this action. (Needed: {apNeeded} | Remaining: {self.turn.getRemainingActions()})")
            return False
        return True
    
    def checkEnoughCash(self, amount):
        if self.player.cash < amount:
            Message.print('RED', f"{self.player.name} doesn't have enough cash to perform this action. (Needed: ${amount} | Remaining: ${self.player.cash})")
            return False
        return True

    def mainAction(self):
        Message.print('PURPLE', f"#### Round{self.turn.round.number}|Turn{Turn.number} ####\n" +
                                f"#### {self.player.name} | ${self.player.cash} ####")
        choice = Action.getPlayerAction(f"ACTIONS {self.turn.actions}/{TURN_ACTIONS}", [
            "1 - Check status",
            "2 - Invest in business",
            "3 - Withdraw from business",
            "4 - Hire robber",
            "0 - Pass"
        ])
        match choice:
            case '1':
                return self.checkAction()
            case '2':
                return self.investAction()
            case '3':
                return self.withdrawAction()
            case '4':
                return self.stealAction()
            case '0':
                return TURN_ACTIONS
            case _:
                return Action.invalidChoice()
            
    def checkAction(self):
        choice = Action.getPlayerAction('CHECK ...', [
            "1 - ... my investments",
            "2 - ... businesses",
            "3 - ... scoreboard",
            "0 - Back"
        ])
        Message.clear()
        match choice:
            case '1':
                Message.printPlayerInvestments(self.turn.player)
                return 0
            case '2':
                Message.printBusinessesStatus()
                return 0
            case '3':
                Message.printScoreboard()
                return 0
            case '0':
                return 0
            case _:
                return Action.invalidChoice();
            
    def investAction(self):
        if not self.checkEnoughAp(ACTION_COST_INVEST): return 0
        business = Action.getPlayerAction('INVEST IN ...', Business.getActionList())
        try:
            business = Business.list[int(business)]
            amount = Action.getAmount()
            if amount == 0:
                Message.clear()
                Message.print('RED', "Investment cancelled")
                return 0
            Message.clear()
            if self.player.invest(business, amount):
                return ACTION_COST_INVEST
            return 0
        except:
            return Action.invalidChoice()
    
    def withdrawAction(self):
        if not self.checkEnoughAp(ACTION_COST_WITHDRAW): return 0
        business = Action.getPlayerAction('CHOOSE WHERE TO WITHDRAW FROM', Business.getWithdrawList(self.turn.player))
        try:
            business = Business.list[int(business)]
            # amount = Action.getAmount()
            amount = business.investments.amounts[self.player.uid]
            print(amount)
            if amount == 0:
                Message.clear()
                Message.print('RED', "Withdraw cancelled")
                return 0
            Message.clear()
            if business.withdraw(self.player, amount):
                return ACTION_COST_WITHDRAW
            return 0
        except:
            return Action.invalidChoice()
        
    def stealAction(self):
        choice = Action.getPlayerAction('SELECT THE TARGET', [
            "1 - Player",
            "2 - Business",
            "0 - Back"
        ])
        match choice:
            case '1':
                return self.stealPlayerAction()
            case '2':
                return self.stealBusinessAction()
            case '0':
                return 0
            case _:
                return Action.invalidChoice()
            
    def stealPlayerAction(self):
        if not self.checkEnoughAp(ACTION_COST_STEAL_PLAYER): return 0
        if not self.checkEnoughCash(CASH_COST_STEAL_PLAYER): return 0
        choice = Action.getPlayerAction('SELECT THE TARGET PLAYER', Player.getActionList())
        try:
            player = Player.list[int(choice)]
            if Thief.stealPlayer(self.player, player):
                return ACTION_COST_STEAL_PLAYER
            else:
                return 0
        except:
            return Action.invalidChoice()
        
    def stealBusinessAction(self):
        if not self.checkEnoughAp(ACTION_COST_STEAL_BUSINESS): return 0
        if not self.checkEnoughCash(CASH_COST_STEAL_BUSINESS): return 0
        choice = Action.getPlayerAction('SELECT THE TARGET BUSINESS', Business.getActionList())
        try:
            business = Business.list[int(choice)]
            if Thief.stealBusiness(self.player, business):
                return ACTION_COST_STEAL_BUSINESS
            else:
                return 0
        except:
            return Action.invalidChoice()

    @staticmethod
    def getAmount():
        return int(input("Enter the amount: "))

    @staticmethod
    def invalidChoice():
        Message.print('RED', "Invalid choice")
        return 0

    @staticmethod
    def getPlayerAction(title, options):
        Action.printChoiceList(title, options)
        return input("Choose an option: ")

    @staticmethod
    def printChoiceList(title, options):
        Message.print('LIGHT_BLUE', f"\n##### {title} #####\n")
        for option in range(len(options)):
            Message.print('LIGHT_BLUE', f"{options[option]}")
        Message.print('LIGHT_BLUE', f"####################\n")

    @staticmethod
    def getPlayerInput():
        return input("Choose an action: ")
    
    @staticmethod
    def enterToContinue():
        input("Press Enter to continue...")

class Thief:

    @staticmethod
    def stealPlayer(client, target):
        stealValue = randint(0, CASH_COST_STEAL_PLAYER * 2)
        client.cash -= CASH_COST_STEAL_PLAYER
        Message.print('RED', f"{client.name} paid ${CASH_COST_STEAL_PLAYER} to steal from {target.name}")
        if target.cash < stealValue:
            stealValue = target.cash
        target.cash -= stealValue
        client.cash += stealValue
        Message.print('RED', f"{client.name} stole ${stealValue} from {target.name}")
        return True

    @staticmethod
    def stealBusiness(client, target):
        Message.print('RED', f"Not Implemented")
        return 0
        stealValue = randint(0, CASH_COST_STEAL_BUSINESS * 3)
        if target.investments.getTotalInvestmentValue() < stealValue:
            stealValue = target.investments.getTotalInvestmentValue()
        pass

class Game:

    def __init__(self):

        Message.printConfiguration()

        HumanPlayer('Joao')
        HumanPlayer('Maria')
        HumanPlayer('Pedro')

        Drugstore("Drogasil"),
        Hotel("Copacabana Palace"),
        Hotel("Ibis Budget"),
        Supermarket("Tauste")

        Action.enterToContinue()
        Message.clear()

        for i in range(ROUNDS):
            self.round = Round(self)
            del self.round
        
        Message.printScoreboard()

    @staticmethod
    def checkBusinessesLevels():
        for business in Business.list:
                business.checkLevelChange()

    @staticmethod
    def generateProfits():
        for business in Business.list:
            business.generateProfit()

Game()