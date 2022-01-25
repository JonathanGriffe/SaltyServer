from django.core.management.base import BaseCommand, CommandError
from board.models import Champion, Matchup
import os


class Command(BaseCommand):
    help = "Adds data in database"

    def handle(self, *args, **options):
        file = open("winrate.txt", "r")
        lines = file.readlines()
        for line in lines:
            data = line.split(";")
            print(data[0][:-1])
            champ, created = Champion.objects.get_or_create(
                name=data[0][:-1],
                defaults={
                    "wins": int(data[1]),
                    "losses": int(data[2]),
                    "avgBetShare": 0.5,
                },
            )
            if not created:
                champ.wins += int(data[1])
                champ.losses += int(data[2])
                champ.save()
        file.close()
        os.remove("winrate.txt")
        file = open("result.txt", "r")
        lines = file.readlines()
        for line in lines:
            data = line.split(";")
            print(data[0][:-1])
            try:
                champ1 = Champion.objects.get(name=data[0][:-1])
                champ2 = Champion.objects.get(name=data[1][:-1])
                try:
                    matchup = Matchup.objects.get(name1=champ1, name2=champ2)
                    matchup.wins1 += int(data[2])
                    matchup.wins2 += int(data[3])
                    matchup.save()
                except Matchup.DoesNotExist:
                    try:
                        matchup = Matchup.objects.get(name1=champ2, name2=champ1)
                        matchup.wins1 += int(data[3])
                        matchup.wins2 += int(data[2])
                        matchup.save()
                    except Matchup.DoesNotExist:
                        Matchup.objects.create(
                            name1=champ1,
                            name2=champ2,
                            wins1=int(data[2]),
                            wins2=int(data[3]),
                            betShare1=0.5,
                        )
            except Champion.DoesNotExist:
                print("can't find champ")

        file.close()
        os.remove("result.txt")
        print("done !")
