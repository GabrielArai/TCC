import pandas as pd
import numpy as np
import requests
import datetime as dt
from bs4 import BeautifulSoup

__all__ = ["creating_club_dataframe","Transfmkt"]


class Transfmkt():
    """
    This module is responsible for encapsulating all the functions related to the creation of the
    predictive model, providing all the common functions for probabilistic time series forecasting.
    """

    def __init__(self, club_name, club_id, headers):
        self.club_name = club_name
        self.club_id = club_id
        self.headers = headers
        self.endereco_da_pagina = "https://www.transfermarkt.com.br/"+club_name+"/startseite/verein/"+club_id+"?"
        self.transfmkt_site = 'https://www.transfermarkt.com.br'
        # Lists
        self.nomes_jog = None
        self.club_jog = None
        self.camp_jog = None
        self.posicoes_jog = None
        self.idade_jog = None
        self.alt_jog = None
        self.nac_jog = None
        self.links_jog = None
        self.links_values_jog = None
        self.link_transfers_jog = None


    def creating_lists(self):
        # endereco_da_pagina stands for the data page address

        # In the objeto_response variable we will the download of the web page
        objeto_response = requests.get(self.endereco_da_pagina, headers=self.headers)

        pagina_bs = BeautifulSoup(objeto_response.content, 'html.parser')

        self.transfmkt_site = 'https://www.transfermarkt.com.br'

        # Players names
        self.nomes_jog = [] # List that will receive all the players names - check
        tags_nomes = pagina_bs.find_all("span", {"class": "show-for-small"})
        for tag_nome in tags_nomes:
            self.nomes_jog.append(tag_nome.text)

        # Players links
        self.links_jog = [] # List that will receive all the players profile links - check
        tags_links = BeautifulSoup(str(tags_nomes).strip('[]'), 'html.parser')
        for a in tags_links.find_all('a', href=True):
            self.links_jog.append(a['href'])

        # Players Values links
        self.links_values_jog = []
        for link in self.links_jog:
            self.links_values_jog.append(str(link).replace("profil","marktwertverlauf"))

        # Players transfers links
        self.link_transfers_jog = []
        for link in self.links_values_jog:
            self.link_transfers_jog.append(link.replace('marktwertverlauf','transfers'))

        # Players clubs
        club_name_of = self.club_name.replace("-","_")
        self.club_jog = [] # List that will receive all the players club - check
        for c in range(len(self.nomes_jog)):
            self.club_jog.append(club_name_of)

        # Clubs championship
        camp_jog = []
        tags_camp = pagina_bs.find_all("span", {"class": "hauptpunkt"})
        for tag_camp in tags_camp:
            camp = str(tag_camp.text).replace(" ", "").replace("\n","")

        for c in range(len(self.nomes_jog)):
            camp_jog.append(camp)

        # Players Positions
        posicoes_jog = [] # List that will receive all the players positions - check
        tags_goleiros = pagina_bs.find_all("td", {"class": "zentriert rueckennummer bg_Torwart"})
        tags_zagueiros = pagina_bs.find_all("td", {"class": "zentriert rueckennummer bg_Abwehr"})
        tags_meias = pagina_bs.find_all("td", {"class": "zentriert rueckennummer bg_Mittelfeld"})
        tags_atacantes = pagina_bs.find_all("td", {"class": "zentriert rueckennummer bg_Sturm"})

        # Gk positions
        for c in range(len(tags_goleiros)):
            posicoes_jog.append("Goleiro")

        # Defenders positions
        for c in range(len(tags_zagueiros)):
            posicoes_jog.append("Defensor")

        # Midfielders positions
        for c in range(len(tags_meias)):
            posicoes_jog.append("Meia")

        # Strikers positions
        for c in range(len(tags_atacantes)):
            posicoes_jog.append("Atacante")

        # Players age, heights, nacionalities
        self.idade_jog = [] # List that will receive all the players age - check
        self.alt_jog = [] # List that will receive all the players height - check
        self.nac_jog = [] # List that will receive all the players nacionalities - check

        for link in self.links_jog:
            end = self.transfmkt_site + link
            obj_resp = requests.get(end, headers=self.headers)
            pag_bs = BeautifulSoup(obj_resp.content, 'html.parser')
            tags_idades = pag_bs.find_all("span", {"itemprop": "birthDate"})
            tags_nac = pag_bs.find_all("span", {"itemprop": "nationality"})
            tags_alt = pag_bs.find_all("span", {"itemprop": "height"})
            for tag_idade in tags_idades:
                self.idade_jog.append(str(tag_idade.text).replace(" ", "")[12:14])

            for tag_nac in tags_nac:
                self.nac_jog.append(str(tag_nac.text).replace(" ", "")[1:])

            for tag_alt in tags_alt:
                self.alt_jog.append(float(str(tag_alt.text).replace(",",".")[:5].rstrip()))

    def get_all_seasons(self,temp,temp_limit):
        all = []
        all.append(temp)
        if temp == temp_limit:
            pass
        else:
            seasons_n = int(temp_limit[3:]) - int(temp[:2])
            for season in range(1,seasons_n):
                if float(temp[3:]) < 9.0:
                    temp = str(temp[3:]) + str('/0'+str(int(float(temp[3:])+1)))
                    all.append(temp)
                else:
                    temp = str(temp[3:]) + str('/'+str(int(float(temp[3:])+1)))
                    all.append(temp)
        return all

    def get_players_seasons(self):
        # Players Seasons
        temps_all = []
        for link in self.link_transfers_jog:
            end = self.transfmkt_site + link
            obj_resp = requests.get(end, headers=self.headers)
            pag_bs = BeautifulSoup(obj_resp.content, 'html.parser')
            tags_seasons = pag_bs.find_all("div", {"class": "tm-player-transfer-history-grid__season"})
            for tag in tags_seasons:
                temps_all.append(str(tag.text).replace(" ", "").replace("\n",""))

        cont = temps_all.count('Temporada')
        idxs = []
        c = 0
        temps_jog = []

        for d in range(0,cont):
            i = temps_all.index('Temporada',c)
            c = i + 1
            idxs.append(i)
            c = i + 1
        idxs.append(len(temps_all))
        idxs.pop(0)

        c = 0
        for d in range(0,cont):
            part = temps_all[c:idxs[d]]
            temps_jog.append(part)
            c += len(part)

        for lst in temps_jog:
            lst.pop(0)

        for lst in temps_jog:
            if len(lst) == 0:
                lst.append('21/22')
            else:
                pass

        temp_inicial_jog = []
        for lst in temps_jog:
            last = lst[-1]
            temp_inicial_jog.append(last)

        temps_sep_jog = []
        for lst in temp_inicial_jog:
            temps_sep_jog.append(self.get_all_seasons(lst,'21/22'))

        return temps_sep_jog









def creating_club_dataframe(
        club_name, 
        club_id, 
        headers
    ):

    # endereco_da_pagina stands for the data page address
    endereco_da_pagina = "https://www.transfermarkt.com.br/"+club_name+"/startseite/verein/"+club_id+"?"

    # In the objeto_response variable we will the download of the web page
    objeto_response = requests.get(endereco_da_pagina, headers=headers)

    pagina_bs = BeautifulSoup(objeto_response.content, 'html.parser')

    club_jog = [] # List that will receive all the players club - 

    transfmkt_site = 'https://www.transfermarkt.com.br'

    # Players names
    nomes_jog = [] # List that will receive all the players names - check
    tags_nomes = pagina_bs.find_all("span", {"class": "show-for-small"})
    for tag_nome in tags_nomes:
        nomes_jog.append(tag_nome.text)

    # Players links
    links_jog = [] # List that will receive all the players profile links - check
    tags_links = BeautifulSoup(str(tags_nomes).strip('[]'), 'html.parser')
    for a in tags_links.find_all('a', href=True):
        links_jog.append(a['href'])

    # Players Values links
    links_values_jog = []
    for link in links_jog:
        links_values_jog.append(str(link).replace("profil","marktwertverlauf"))

    # Players clubs
    club_name_of = club_name.replace("-","_")
    club_jog = [] # List that will receive all the players club - check
    for c in range(len(nomes_jog)):
        club_jog.append(club_name_of)

    # Clubs championship
    camp_jog = []
    tags_camp = pagina_bs.find_all("span", {"class": "hauptpunkt"})
    for tag_camp in tags_camp:
        camp = str(tag_camp.text).replace(" ", "").replace("\n","")

    for c in range(len(nomes_jog)):
        camp_jog.append(camp)

    # Players Positions
    posicoes_jog = [] # List that will receive all the players positions - check
    tags_goleiros = pagina_bs.find_all("td", {"class": "zentriert rueckennummer bg_Torwart"})
    tags_zagueiros = pagina_bs.find_all("td", {"class": "zentriert rueckennummer bg_Abwehr"})
    tags_meias = pagina_bs.find_all("td", {"class": "zentriert rueckennummer bg_Mittelfeld"})
    tags_atacantes = pagina_bs.find_all("td", {"class": "zentriert rueckennummer bg_Sturm"})

    # Gk positions
    for c in range(len(tags_goleiros)):
        posicoes_jog.append("Goleiro")

    # Defenders positions
    for c in range(len(tags_zagueiros)):
        posicoes_jog.append("Defensor")

    # Midfielders positions
    for c in range(len(tags_meias)):
        posicoes_jog.append("Meia")

    # Strikers positions
    for c in range(len(tags_atacantes)):
        posicoes_jog.append("Atacante")

    # Players age, heights, nacionalities
    idade_jog = [] # List that will receive all the players age - check
    alt_jog = [] # List that will receive all the players height - check
    nac_jog = [] # List that will receive all the players nacionalities - check

    for link in links_jog:
        end = transfmkt_site + link
        obj_resp = requests.get(end, headers=headers)
        pag_bs = BeautifulSoup(obj_resp.content, 'html.parser')
        tags_idades = pag_bs.find_all("span", {"itemprop": "birthDate"})
        tags_nac = pag_bs.find_all("span", {"itemprop": "nationality"})
        tags_alt = pag_bs.find_all("span", {"itemprop": "height"})
        for tag_idade in tags_idades:
            idade_jog.append(str(tag_idade.text).replace(" ", "")[12:14])

        for tag_nac in tags_nac:
            nac_jog.append(str(tag_nac.text).replace(" ", "")[1:])

        for tag_alt in tags_alt:
            alt_jog.append(float(str(tag_alt.text).replace(",",".")[:5].rstrip()))

    # Players performance
    gols_jog = []
    
    
    
    
    
    
    
    # Players value
    valor_jog = []


    
    dic = {
        'nome':nomes_jog,
        'clube_atual':club_jog,
        'campeonato':camp_jog,
        'posicao':posicoes_jog,
        'idade':idade_jog,
        'nacionalidade':nac_jog,
        'altura':alt_jog
    }

    df = pd.DataFrame(dic)

    # Players transfers links
    link_transfers_jog = []
    for link in links_values_jog:
        link_transfers_jog.append(link.replace('marktwertverlauf','transfers'))

    # Players Seasons
    temps_all = []
    for link in link_transfers_jog:
        end = transfmkt_site + link
        obj_resp = requests.get(end, headers=headers)
        pag_bs = BeautifulSoup(obj_resp.content, 'html.parser')
        tags_seasons = pag_bs.find_all("div", {"class": "tm-player-transfer-history-grid__season"})
        for tag in tags_seasons:
            temps_all.append(str(tag.text).replace(" ", "").replace("\n",""))

    cont = temps_all.count('Temporada')
    idxs = []
    c = 0
    temps_jog = []

    for d in range(0,cont):
        i = temps_all.index('Temporada',c)
        c = i + 1
        idxs.append(i)
        c = i + 1
    idxs.append(len(temps_all))
    idxs.pop(0)

    c = 0
    for d in range(0,cont):
        part = temps_all[c:idxs[d]]
        temps_jog.append(part)
        c += len(part)

    for lst in temps_jog:
        lst.pop(0)

    for lst in temps_jog:
        if len(lst) == 0:
            lst.append('21/22')
        else:
            pass

    temp_inicial_jog = []
    for lst in temps_jog:
        last = lst[-1]
        temp_inicial_jog.append(last)
    
    return temp_inicial_jog