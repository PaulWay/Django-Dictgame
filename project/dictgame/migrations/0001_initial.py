# Generated by Django 3.2.7 on 2021-09-17 06:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Definition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('definition', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.SlugField(max_length=16)),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('alias', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=64)),
                ('theme', models.CharField(choices=[('W', 'Word'), ('O', 'Organisation'), ('M', 'Movie plot'), ('P', 'Person'), ('D', 'Date')], max_length=1)),
                ('state', models.CharField(choices=[('1', 'Ready to be shown'), ('2', 'Word being shown, ready for definitions'), ('3', 'Definitions being voted on, ready for scoring'), ('4', 'Scoring done')], max_length=1)),
                ('dasher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictgame.player')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictgame.event')),
            ],
        ),
        migrations.CreateModel(
            name='Guess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scored', models.BooleanField(default=False)),
                ('score', models.PositiveSmallIntegerField(default=0)),
                ('chose', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guesses', to='dictgame.definition')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictgame.player')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictgame.player'),
        ),
        migrations.AddField(
            model_name='definition',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictgame.player'),
        ),
        migrations.AddField(
            model_name='definition',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='definitions', to='dictgame.question'),
        ),
    ]