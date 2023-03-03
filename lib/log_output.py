import discord
import datetime


def log_output(ctx: discord.ApplicationContext, cmd: str):
    time = datetime.datetime.now().strftime('%m/%d - %H:%M:%S')
    log = f'{time} / {ctx.guild.name} / #{ctx.channel.name} / {ctx.author.name} / {cmd}'
    print(log)


def log_output_interaction(interaction: discord.Interaction, cmd: str):
    time = datetime.datetime.now().strftime('%m/%d - %H:%M:%S')
    log = f'{time} / {interaction.user.guild.name} --Channel-- {interaction.user.name} / {cmd}'
    print(log)

#from lib.log_output import log_output, log_output_interaction
