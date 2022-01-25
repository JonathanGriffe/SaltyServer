# Generated by Django 3.1.5 on 2021-01-28 15:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("board", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="match",
            name="blueName",
        ),
        migrations.RemoveField(
            model_name="match",
            name="redName",
        ),
        migrations.AddField(
            model_name="match",
            name="blue",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="blue",
                to="board.champion",
            ),
        ),
        migrations.AddField(
            model_name="match",
            name="red",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="red",
                to="board.champion",
            ),
        ),
        migrations.AddField(
            model_name="match",
            name="time",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="matchup",
            name="name1",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="name1",
                to="board.champion",
            ),
        ),
        migrations.AlterField(
            model_name="matchup",
            name="name2",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="name2",
                to="board.champion",
            ),
        ),
        migrations.AlterField(
            model_name="matchup",
            name="wins1",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="matchup",
            name="wins2",
            field=models.IntegerField(),
        ),
    ]
