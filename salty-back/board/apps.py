from django.apps import AppConfig
import websocket
import django.dispatch as dispatch
from threading import Thread
import requests
import json
from asgiref.sync import async_to_sync
import channels.layers
import math
import time
import os

url_status = "https://www.saltybet.com/state.json"  # url to get status
url_sid = (
    "https://www.saltybet.com:2096/socket.io/?EIO=3&transport=polling"  # url to get sid
)
url_ws = "wss://www.saltybet.com:2096/socket.io/?EIO=3&transport=websocket&sid="  # url to open websocket
url_balance = "https://www.saltybet.com/zdata.json"  # url to get balance
PHPSESSID = os.environ["SB_PHPSESSID"]

# send new status to clients
def broadcast_status(status):
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "status",
        {
            "type": "new_status",
            "content": str(status),
        },
    )


# if message signals new status, trigger signal ws
def on_message(ws, message):
    print(message)
    if message == '42["message"]':
        ws.sig.send(ws)


def on_error(ws, error):
    print(error)


def on_open(ws):
    def run(*args):  # initialize connection by sending "2probe" and "5"
        ws.send("2probe")
        time.sleep(1)
        ws.send("5")
        print("WS Online")
        while 1:  # keep connection alive by sending "2" periodically
            time.sleep(25)
            ws.send("2")
        time.sleep(1)
        print("thread terminating...")

    t = Thread(target=run)
    t.start()


# initialize websocket
def runWS(signal):
    r = requests.get(url_sid)  # get sid to identify to server
    sid = r.text.split('"')[3]
    ws = websocket.WebSocketApp(url_ws + sid, on_message=on_message, on_error=on_error)
    ws.sig = signal
    ws.on_open = on_open
    ws.run_forever()


# returns player to bet on, depending on NScores
def betNScore(redNScore, blueNScore):
    if redNScore > blueNScore + 0.1:
        return "player1"
    if blueNScore > redNScore + 0.1:
        return "player2"
    return ""


models = None

# gets data from database and computes NScore of character with name "name"
def NScore(name, models):
    try:
        champ = models.Champion.objects.get(name=name)
    except models.Champion.DoesNotExist:
        return 0.5
    CScore = (champ.wins + champ.losses) / (10 + champ.wins + champ.losses)
    NScore = 0.5
    if CScore:
        NScore = (
            0.5 * (1 - CScore) + (champ.wins / (champ.wins + champ.losses)) * CScore
        )
    return NScore


# function run everytime status changes
def updateStatus(**kwargs):
    global models
    if models == None:
        print("not loaded")
        return
    print("updating")

    # gets new data
    CS = models.Status.objects.first()
    r = requests.get(url_status)
    S = json.loads(r.text)
    status = S["status"]

    # if status indeed changed, process new data
    if status != CS.status:
        CS.status = status

        # red won
        if status == "1":
            CS.red = S["p1name"]
            CS.blue = S["p2name"]
            betRed = S["p1total"].replace(",", "")
            betBlue = S["p2total"].replace(",", "")
            scoreDiff = NScore(CS.red, models) - NScore(CS.blue, models)
            writeResult(CS.red, CS.blue, int(betRed), int(betBlue), scoreDiff)
            print(CS.red + " won against " + CS.blue)
            CS.avgDiff = (CS.avgDiff * CS.n + abs(scoreDiff)) / (CS.n + 1)
            CS.covariance = (CS.n * CS.covariance + scoreDiff) / (CS.n + 1)
            CS.n += 1

        # blue won
        if status == "2":
            CS.red = S["p1name"]
            CS.blue = S["p2name"]
            betRed = S["p1total"].replace(",", "")
            betBlue = S["p2total"].replace(",", "")
            writeResult(CS.blue, CS.red, int(betBlue), int(betRed), scoreDiff)
            print(CS.blue + " won against " + CS.red)
            scoreDiff = NScore(CS.red, models) - NScore(CS.blue, models)
            CS.avgDiff = (CS.avgDiff * CS.n + abs(scoreDiff)) / (CS.n + 1)
            CS.covariance = (CS.n * CS.covariance - scoreDiff) / (CS.n + 1)
            CS.n += 1

        # bets are open
        if status == "open":
            CS.red = S["p1name"]
            CS.blue = S["p2name"]
            red, created = models.Champion.objects.get_or_create(
                name=CS.red, defaults={"wins": 0, "losses": 0, "avgBetShare": 0}
            )
            blue, created = models.Champion.objects.get_or_create(
                name=CS.blue, defaults={"wins": 0, "losses": 0, "avgBetShare": 0}
            )
            winner = betNScore(NScore(CS.red, models), NScore(CS.blue, models))
            print("Next match : " + CS.red + " against " + CS.blue)
            cookies = {"PHPSESSID": PHPSESSID}
            r = requests.get(url_balance)
            l = json.loads(r.text)
            if "804660" in l:
                CS.balance = int(l["804660"]["b"])
            amount = math.floor(
                max(min(max(325, CS.balance / 2), 10000), CS.balance / 10)
            )
            if winner != "":
                r = requests.post(
                    "https://www.saltybet.com/ajax_place_bet.php",
                    data={"selectedplayer": winner, "wager": str(amount)},
                    cookies=cookies,
                )

        # bets are locked
        if status == "locked":
            print("Bets locked !")
            CS.red = S["p1name"]
            CS.blue = S["p2name"]
            red, created = models.Champion.objects.get_or_create(
                name=CS.red, defaults={"wins": 0, "losses": 0, "avgBetShare": 0}
            )
            blue, created = models.Champion.objects.get_or_create(
                name=CS.blue, defaults={"wins": 0, "losses": 0, "avgBetShare": 0}
            )

        # send new status to clients, and save new status to database
        broadcast_status(CS)
        CS.save()
    else:
        print("Same")


# writes new results into database
def writeResult(winnerName, looserName, betWinner, betLooser, scoreDiff):
    print("write")

    # create character into database, or get data if it already exists
    winner, created = models.Champion.objects.get_or_create(
        name=winnerName,
        defaults={
            "wins": 1,
            "losses": 0,
            "avgBetShare": betWinner / (betWinner + betLooser),
        },
    )
    if not created:
        winner.avgBetShare = (
            winner.avgBetShare * (winner.wins + winner.losses)
            + betWinner / (betWinner + betLooser)
        ) / (winner.wins + winner.losses + 1)
        winner.wins += 1
        winner.save()
    looser, created = models.Champion.objects.get_or_create(
        name=looserName,
        defaults={
            "wins": 0,
            "losses": 1,
            "avgBetShare": betLooser / (betWinner + betLooser),
        },
    )
    if not created:
        looser.avgBetShare = (
            looser.avgBetShare * (looser.wins + looser.losses)
            + betLooser / (betWinner + betLooser)
        ) / (looser.wins + looser.losses + 1)
        looser.losses += 1
        winner.save()

    try:  # try to get Matchup to change it, create it if it doesn't exist
        match = models.Matchup.objects.get(name1=winner, name2=looser)
        match.betShare1 = (
            match.betShare1 * (match.wins1 + match.wins2)
            + betWinner / (betWinner + betLooser)
        ) / (match.wins1 + match.wins2 + 1)
        match.wins1 += 1
        match.save()
    except models.Matchup.DoesNotExist:
        try:
            match = models.Matchup.objects.get(name1=looser, name2=winner)
            match.betShare1 = (
                match.betShare1 * (match.wins1 + match.wins2)
                + betLooser / (betWinner + betLooser)
            ) / (match.wins1 + match.wins2 + 1)
            match.wins2 += 1
            match.save()
        except models.Matchup.DoesNotExist:
            match = models.Matchup.objects.create(
                name1=winner,
                name2=looser,
                wins1=1,
                wins2=0,
                betShare1=betWinner / (betWinner + betLooser),
            )
    models.Match.objects.create(
        NScoreDifference=scoreDiff,
        winnerTotalBets=betWinner,
        looserTotalBets=betLooser,
        winner=winner,
        looser=looser,
    )
    print("written")


signal = dispatch.Signal()
signal.connect(updateStatus)  # update the data everytime the signal is triggered


class BoardConfig(AppConfig):
    name = "board"
    started = False

    def ready(self):
        global models
        from . import models

        if self.started:
            return
        self.started = True
        signal.send(self)
        t = Thread(target=runWS, args=(signal,))
        t.start()
