from django.db import models

# Create your models here.

#Table representing characters, their wins, losses and average share of total bet amount [0,1]
class Champion(models.Model):
    name = models.CharField(max_length=50)
    wins = models.IntegerField()
    losses = models.IntegerField()
    avgBetShare = models.FloatField(default=0)

    def __str__(self):
        return '{"name":"'+str(self.name)+'", "wins":'+str(self.wins)+', "losses":'+str(self.losses)+', "avgBetShare":'+str(self.avgBetShare)+'}'

#Represents matches between 2 characters, and the share of bets on red [0,1]
class Matchup(models.Model):
    name1 = models.ForeignKey(Champion, on_delete=models.CASCADE, related_name ='name1', null=True)
    name2 = models.ForeignKey(Champion, on_delete=models.CASCADE, related_name = 'name2', null=True)
    wins1 = models.IntegerField()
    wins2 = models.IntegerField()
    betShare1 = models.FloatField(default=0.5)

    def __str__(self):
        return "Matchup winrate : " + str(self.wins1) + " - " + str(self.wins2)

def NScore(name):
    try:
        champ = Champion.objects.get(name=name)
    except Champion.DoesNotExist:
        return 0.5
    CScore = (champ.wins+champ.losses)/(10+champ.wins+champ.losses)
    NScore = 0.5
    if CScore:
        NScore = 0.5*(1 - CScore) + (champ.wins/(champ.wins+champ.losses)) * CScore
    return NScore

#Represents matches played
class Match(models.Model):
    time = models.DateTimeField(auto_now_add = True, null=True)
    winner = models.ForeignKey(Champion, on_delete=models.CASCADE, related_name = 'red', null=True)
    looser = models.ForeignKey(Champion, on_delete=models.CASCADE, related_name = 'blue', null=True)
    NScoreDifference = models.FloatField()
    winnerTotalBets = models.IntegerField()
    looserTotalBets = models.IntegerField()

#Represents current status
class Status(models.Model):
    time = models.DateTimeField(auto_now = True, null=True)
    status = models.CharField(max_length=10)
    red = models.CharField(max_length=50)
    blue = models.CharField(max_length=50)
    betRed = models.IntegerField()
    betBlue = models.IntegerField()
    covariance = models.FloatField()
    avgDiff = models.FloatField()
    n = models.IntegerField()
    balance = models.IntegerField()

    def __str__(self):
        red = Champion.objects.get(name=self.red)
        blue = Champion.objects.get(name=self.blue)
        NScoreDiff = NScore(self.red) - NScore(self.blue)
        a = '{"red":'+str(red)+', "blue":'+str(blue)+', "status":"'+self.status+'", "NScoreDiff":'+str(NScoreDiff)+"}"
        return a
        