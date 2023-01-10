import os
import discord
import datetime
from discord.ext import tasks
from discord import app_commands as apc
import json
from pytz import timezone



class Petlider(apc.Group):
    """Comandos de liderança"""
    def __init__(self, bot: discord.Client):
        super().__init__()
        self.bot = bot
        self.months_names = { "1": "Janeiro", "2": "Fevereiro","3": "Março","4": "Abril","5": "Maio","6": "Junho","7": "Julho","8": "Agosto","9": "Setembro","10": "Outubro","11": "Novembro","12": "Dezembro",}
        self.leadership = self.readLeaderFile()
        
    @apc.command(name="lideres", description="Mostra os líderes do mês")
    async def month_leadership(self, interaction: discord.Interaction):
        self.leadership = self.readLeaderFile()
        await interaction.response.defer()
        if self.leadership == {}:
            await interaction.followup.send("Não há líderes cadastrados!")
            return
        current_month = datetime.date.today().month
        if str(current_month) not in self.leadership.keys():
            await interaction.followup.send("Não há líderes cadastrados para este mês!")
            return
        
        current_leadership = self.leadership[f'{current_month}']
        em = discord.Embed(
            title=f"**Liderança:**",
            description=f"Neste mês de {self.months_names[f'{current_month}'].lower()}, o líder é **{current_leadership[0]}** e o vice é **{current_leadership[1]}**.\n\nPara os próximos meses:",
            color=0xFDFD96
        )
        while current_month <= 12:
            embed_month = str(current_month)
            if embed_month in self.leadership.keys():
                next_leadership = self.leadership[embed_month]
                em.add_field(
                    name=f"**{self.months_names[embed_month]}**",
                    value=f"__Líder__: {next_leadership[0]}\n__Vice__: {next_leadership[1]}",
                    inline=False
                )
            current_month += 1
            
        await interaction.followup.send(embed=em)
        
    @apc.command(name="adicionar", description="Adiciona uma dupla à liderança")
    async def addLider(self, interaction: discord.Interaction, mes: int, lider: str, vice: str):
        if f'{mes}' not in self.leadership:
            self.leadership[f'{mes}'] = [lider, vice]
            json.dump(self.leadership, open("data/leadership.json", "w"))
            await interaction.response.send_message("Adicionado com sucesso!")
        else:
            await interaction.response.send_message("Mês já existe!")
       
    @apc.command(name="remover", description="Remove uma dupla da liderança")
    async def remLider(self, interaction: discord.Interaction, mes: int):
        if f'{mes}' in self.leadership:
            del self.leadership[f'{mes}']
            json.dump(self.leadership, open("data/leadership.json", "w"))
            await interaction.response.send_message("Removido com sucesso!")
        else:
            await interaction.response.send_message("Mês não existe!")
            
    @apc.command(name="clear", description="Limpa todas as duplas da liderança")
    async def clearLider(self, interaction: discord.Interaction, confirmacao: bool):
        if not confirmacao:
            await interaction.response.send_message("Confirmação necessario para executar esse comando!")
        else:
            self.leadership = {}
            json.dump(self.leadership, open("data/leadership.json", "w"))
            await interaction.response.send_message("Lideres do ano deletados!")
        
    @tasks.loop(time=datetime.time(hour=12, minute=54, tzinfo=timezone('America/Sao_Paulo')))
    async def leadership_alert(self):
        if not datetime.date.today().day == 1:
            return
        
        data = self.readLeaderFile()
        leadership = data[f'{datetime.date.today().month}']
        channel = self.bot.get_channel(int(os.getenv("LEADERSHIP_CHANNEL", 0)))
        await channel.send(f'Atenção, <@&{os.getenv("PETIANES_ID", 0)}>!\nNesse mês, nosso ditador passa a ser {leadership[0]} e nosso vice, {leadership[1]}.')

    @tasks.loop(count=1)
    async def startTasks(self):
        self.leadership_alert.start()
        
    def readLeaderFile(self) -> dict:
        with open("data/leadership.json", 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data
        