# Import
import copy
import random
import os
import string

from colorama import init
from termcolor import colored


# Constantes
NB_LIGNES = 15
NB_COLONNES = 15
DICTIONNAIRE = 'data/dico.txt'
LETRRES = 'data/lettres.txt'
ASCCI_SCRABBLE = """


                ███████╗ ██████╗██████╗  █████╗ ██████╗ ██████╗ ██╗     ███████╗
                ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝
                ███████╗██║     ██████╔╝███████║██████╔╝██████╔╝██║     █████╗
                ╚════██║██║     ██╔══██╗██╔══██║██╔══██╗██╔══██╗██║     ██╔══╝
                ███████║╚██████╗██║  ██║██║  ██║██████╔╝██████╔╝███████╗███████╗
                ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚══════╝╚══════╝

"""

REGLES = """

Fonctionnement du jeu :

Le Scrabble (marque déposée) est un jeu de société et un jeu de lettres dont l’objectif est de réaliser des
points en plaçant des mots, au départ de tirages aléatoires de lettres, sur une grille carrée dont certaines
cases sont primées.
Le plateau de jeu est une grille carrée de 15 sur 15 (soit 225 cases en tout), dont certaines cases colorées,
dites “cases multiplicatrices”, valorisent la lettre ou le mot placé dessus. Il y a 102 lettres en tout dans
la version francophone. La lettre E est la plus fréquente avec 15 occurrences, mais ne vaut qu’un point,
tandis que les “lettres chères” J, K, Q, W, X, Y et Z sont uniques mais valent 8 (J et Q) ou 10 points (K, W,
X, Y et Z).
Chaque  joueur  dispose  d’un  chevalet  contenant  ses  7  lettres.  Au  premier  tour  et  après  avoir  joué,  le
joueur tire aléatoirement des lettres dans le sachet afin de compléter son chevalet. Le premier mot doit
passer par la case centrale et les mots suivants doivent s’appuyer sur
des mots déjà placés. Par ailleurs, un mot ne se lit que de gauche à doite ou de haut en bas.
Le joueur qui parvient à placer 7 lettres en posant un mot reçoit un bonus de 50 points. Ce genre de
coup est appelé “scrabble” (en anglais, on dit bonus ou bingo). Le joueur a “scrabblé”. La recherche d’un
scrabble doit évidemment être la priorité lors de chaque coup.
Si un scrabble se révèle impossible à former (par exemple, sur un tirage tel que “BGIOOUV”), le joueur
doit porter son attention sur les cases “mot compte triple” et “mot compte double”, si elles sont acces-
sibles.

Inspiré de Wikipedia.


"""

# Variables
sets_mots = []
current_tour = 1
tour_affiche = 1
current_player = 0
players = []
players_score = {}
players_color = {}
colors = ['yellow', 'magenta', 'cyan', 'red']
jeu_en_cours = True
joueur_passe = 0
lettres_joueurs = {}
plateau = []

retirer_accent_dico = {' ': '', 'é': 'e', 'è': 'e',
                       'ê': 'e', 'à': 'a', 'î': 'i', 'û': 'u', 'ô': 'o'}

mot_compte_double = [(1, 1), (2, 2), (3, 3), (4, 4), (7, 7), (10, 10), (11, 11), (12, 12),
                     (13, 13), (13, 1), (12, 2), (11, 3), (10, 4), (4, 10), (3, 11), (2, 12), (1, 13)]
mot_compte_triple = [(0, 0), (0, 7), (0, 14), (7, 0),
                     (7, 14), (14, 0), (14, 7), (14, 14)]
lettre_compte_double = [(0, 3), (0, 11), (2, 6), (2, 8), (3, 0), (3, 7), (3, 14), (6, 2), (6, 6), (6, 8), (6, 12), (
    7, 3), (7, 11), (8, 2), (8, 6), (8, 8), (8, 12), (11, 0), (11, 7), (11, 14), (12, 6), (12, 8), (14, 3), (14, 11)]
lettre_compte_triple = [(1, 5), (1, 9), (5, 1), (5, 5), (5, 9),
                        (5, 13), (9, 1), (9, 5), (9, 9), (9, 13), (13, 5), (13, 9)]

# Fonctions


def load_fichier_lettres(nom_fichier_lettres):
    """Cette fonction ouvre et lit un fichier texte
    dont le nom est fourni en argument.
    Ce fichier contient 26 lignes (une pour
    chaque lettre de l'alphabet). Chaque ligne
    est composée d'une lettre, d'un nombre
    d'occurences de cette lettre dans le jeu
    et des points que la lettre rapporte au
    joueur s'il la place, chacun séparé par
    un espace. (cf fin de la page 2 de l'énoncé
    pour voir un extrait du fichier
    (lettres.txt)).
    Elle renvoie ensuite deux dictionnaires dont
    les clés sont les lettres contenues dans le
    fichier texte et les valeurs sont respectivement
    le nombre d'occurences et les points que la lettre
    rapporte.
    Arguments :
    - nom_fichier_lettres (str) : Un chaine de caractère
    qui représente le nom du fichier texte à ouvrir
    Valeurs de retour (dans cet ordre):
    - dict : un dictionnaire avec comme clés les lettres contenues dans le fichier et
    comme valeur le nombre d'occurences de
    cette lettre
    - dict : un dictionnaire avec comme clés
    les lettres contenues dans le fichier et
    comme valeur les points associés à chaque lettre
    """

    dict1 = {}
    dict2 = {}
    fs = open(nom_fichier_lettres)
    splite = fs.read().split()
    for i in range(26):
        dict1[splite[i*3]] = int(splite[(i*3)+1])
        dict2[splite[i*3]] = int(splite[(i*3)+2])
    fs.close()
    return(dict1, dict2)


def pioche_init(occurences_lettres):
    """ Cette fonction renvoie une chaine de
    caractères (str) contenant toutes les
    lettres disponibles lors de
    l'initialisation du jeu, classées dans l'ordre alphabétique.
    Arguments:
    - occurences_lettres (dict) : dictionnaire ayant comme clés
    toutes les lettres de l'alphabet
    et comme valeur, le nombre de fois (int)
    que chaque lettre devra être ajoutée
    à la pioche
    Valeur de retour:
    - str : une chaine de caractère contenant toutes les lettres de la pioche classées dans l'ordre
    alphabétique.
    """

    ret = []
    for i in occurences_lettres:
        for j in range(occurences_lettres[i]):
            ret.append(i)
    return(sorted(ret))


def plateau_init(dimensions):
    """Cette fonction va créer le plateau
    de jeu. Le plateau de jeu consiste
    en une liste de nb_lignes sous-listes,
    chacune de longueur nb_colonnes, où
    chaque élément représente une case
    du plateau grâce à la valeur "_"
    (underscore).
    Si nb_lignes = nb_colonnes = 3, on aura
    par exemple:
    plateau = [["_", "_", "_"], ["_", "_", "_"],["_", "_", "_"]]
    Arguments:
    - dimensions (tuple) : un tuple de deux nombres
    entiers et positifs. Le premier élément est le
    nombre de lignes (nb_lignes (int)) et le deuxième
    élément est le nombre de colonnes (nb_colonnes (int))
    Valeur de retour:
    - liste: la liste de sous-listes qui représente le plateau
    """

    nb_lignes, nb_colonnes = dimensions
    plateau = []
    sublist = []
    for i in range(nb_colonnes):
        sublist.append('_')

    for j in range(nb_lignes):
        plateau.append(copy.deepcopy(sublist))
    return(plateau)


def propose_mot(msg_position_ligne, msg_err_position_ligne, msg_position_colonne, msg_err_position_colonne, msg_direction, msg_mot, msg_err_mot, tour):
    """Cette fonction demande au joueur où et quel mot
    il désire placer.
    La séquence d'inputs et de vérification
    est la suivante:
    1. Demander le numéro de la ligne de la
    première lettre du mot à placer. Utilisez comme
    argument de la fonction input() : msg_position_ligne
    1.1 Tant que le joueur n'entre pas un numéro de ligne valide
    (un caractère convertible en un nombre entier compris entre 0
    et NB_lIGNE-1), retourner en 1.
    2. Demander le numéro de la colonne de la
    première lettre du mot à placer. Utilisez comme
    argument de la fonction input() : msg_position_colonne
    2.1 Tant que le joueur n'entre pas un numéro de colonne valide(un caractère
    convertible en un nombre entier compris entre 0 et NB_COLONNE-1),
    retourner en 2.
    3. Demander la direction du mot à placer ("h" ou "v"). Utilisez comme
    argument de la fonction input() : msg_direction
    3.1 Tant que le joueur n'entre pas une direction valide(le caractère "h" ou "v"),
    retourner en 3.
    4. Demander le mot à placer. Utilisez comme
    argument de la fonction input() : msg_mot
    4.1 Tant que le joueur n'entre pas un mot valide(uniquement des lettres en majuscule
    ou minuscule), retourner en 4.
    Attention, si le mot à placer s'appuie sur une ou
    plusieurs lettres présentes sur le plateau, il faut
    préciser tout le mot qui sera formé et pas seulement
    les lettres à placer. Par exemple, partons de la situation
    initial suivante:
    plateau = [["_", "_", "_"], ["_", "_", "S"],["_", "_", "_"]]
    lettres = ['A','N','Z','Y','W','U','V']
    Si on veut placer le mot "ANS" avec les lettres "A", "N",
    à la position (1,0), avec comme direction "h"
    il faut proposer le mot "ANS" et non pas "AN" à placer.
    De même, imaginons que nous partons de la deuxième situation
    initiale suivante :
    plateau = [["_", "_", "_","_"], ["D", "_", "_", "_"],["E","_", "_", "_"]]
    lettres = ['A','N','S','Y','W','U','V']
    Si on veut placer le mot "ANS" avec les lettres "A", "N","S",
    à la position (1,1), avec comme direction "h". Le mot final sera "DANS".
    Il faut alors proposer "DANS" comme mot, et non pas "ANS".
    Arguments :
    - msg_position_ligne (str) : une chaine de caractère à afficher à l'écran
    du joueur lors de l'input pour lui demander quelle est le numéro
    de ligne de la première lettre de son mot.
    - msg_position_colonne (str) : une chaine de caractère à afficher à l'écran
    du joueur lors de l'input pour lui demander quelle est le numéro
    de colonne de la première lettre de son mot.
    - msg_direction (str) : une chaine de caractère à afficher à l'écran
    du joueur lors de l'input pour lui demander quelle est la
    direction pour son mot ("h" = horizontale ou "v" = verticale)
    - msg_mot (str) : une chaine de caractère à afficher à l'écran
    du joueur lors de l'input pour lui demander quel mot le joueur
    désire placer
    Valeurs de retour (dans cet ordre):
    - (str): une chaine de caractère en MAJUSCULE qui indique le mot à placer
    - tuple: un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l),
    et le numéro de la colonne (c) de la première lettre du mot à placer
    - (str): un charactère ("h" ou "v") qui indique la direction du mot
    """

    #ret = ('',(0, 0), '')

    """if tour == 1:
        msg_position_ligne = msg_position_ligne_tour1
        msg_err_position_ligne = msg_err_position_ligne_tour1"""

    position_ligne = retirer_accent(input(msg_position_ligne)).upper()
    position_ligne_validity_list = ['P', 'R']

    for i in range(NB_LIGNES):
        position_ligne_validity_list.append(str(i))
    while position_ligne not in position_ligne_validity_list:
        position_ligne = retirer_accent(input(msg_err_position_ligne)).upper()

    if position_ligne == 'P':
        ret = 'P'
    elif position_ligne == 'R':
        ret = 'R'
    else:

        position_colonne = retirer_accent(input(msg_position_colonne))
        position_colonne_validity_list = []

        for i in range(NB_COLONNES):
            position_colonne_validity_list.append(str(i))
        while position_colonne not in position_colonne_validity_list:
            position_colonne = retirer_accent(input(msg_err_position_colonne))

        direction = retirer_accent(input(msg_direction)).lower()
        while direction not in ['h', 'v']:
            direction = retirer_accent(input(msg_direction)).lower()

        mot = retirer_accent(input(msg_mot))
        # print(mot)
        while not mot.replace('*', '').isalpha():
            mot = retirer_accent(input(msg_err_mot))

        ret = (mot.upper(), (int(position_ligne), int(
            position_colonne)), direction.lower())

    return(ret)


def retirer_accent(mot):
    """Cette fonction permet de retirer les accents et les espaces
    Arguments :
    - mot (str): une chaine de caractère avec des accents ou des espaces
    Valeurs de retour:
    - mot_sans_accent (str): le même mot que passé en argument mais sans espaces et accents
    """

    mot_sans_accent = mot
    for r in retirer_accent_dico.keys():
        if r in mot_sans_accent:
            mot_sans_accent = mot_sans_accent.replace(
                r, retirer_accent_dico[r])
    return(mot_sans_accent)


def verif_bornes(coup, dimensions):
    """Cette fonction renvoie True si le mot à placer ne
    dépasse pas les des bornes du plateau de jeu. False, sinon.
    Arguments :
    - coup (tuple): un tuple à 3 éléments:
    - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
    - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l),
    et le numéro de la colonne (c) de la première lettre du mot à placer
    - dir (str) : un charactère (h ou v) qui indique la direction du mot
    - dimensions (tuple) : un tuple de deux nombres entiers et positifs. Le premier élément est le nombre de lignes 
    Valeurs de retour:
    - bool (True ou False)
    """

    ret = False
    mot, pos, dir = coup
    l, c = pos
    nb_lignes, nb_colonnes = dimensions

    if dir == 'h' and nb_colonnes-c-len(mot) >= 0:
        ret = True

    if dir == 'v' and nb_lignes-l-len(mot) >= 0:
        ret = True
    return(ret)


def verif_premier_tour(coup):
    """Cette fonction retourne True si le mot à placer passe bien par la case (7,7).
    On considère que le mot à placer ne dépasse pas des bornes du plateau
    et ne fait pas plus de 7 lettres. On considère également que cette fonction ne
    sera appelée qu'au premier tour. Le plateau est donc totalement vide.
    Arguments :
    - coup (tuple): un tuple à 3 éléments:
    - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
    - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l),
    et le numéro de la colonne (c) de la première lettre du mot à placer
    - dir (str) : un charactère (h ou v) qui indique la direction du mot
    Valeurs de retour :
    - bool : True ou False
    """

    ret = False
    mot, pos, dir = coup
    l, c = pos

    if dir == 'h' and l == 7 and c+len(mot) >= 7:
        ret = True
    elif dir == 'v' and c == 7 and l+len(mot) >= 7:
        ret = True

    return(ret)


def verif_lettres_joueur(plateau, lettres_joueur, coup):
    """
    Cette fonction renvoie True:
    - Si le mot à placer appartient au lettres du joueur (lettres_joueurs)
    ou
    - Si une ou plusieurs lettres manquent mais sont déjà placées à la place
    adéquate sur le plateau (plateau).
    Sinon, la fonction renvoie False.
    On pré-suppose que le mot ne dépasse pas des bornes du plateau
    Arguments :
    - plateau (liste) : une liste de sous-listes qui représentent
    chacune une ligne du plateau de jeu.
    Elles contiennent chacune, soit un underscore pour
    indiquer que la case est vide, soit une lettre
    si elle a déjà été placée là auparavant.
    - lettres_joueur (liste) : une liste qui contient chacune
    des lettres que le joueur possède sur son chevalet.
    Toutes ces lettres sont en MAJUSCULE.
    - coup (tuple): un tuple à 3 éléments:
    - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
    - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l),
    et le numéro de la colonne (c) de la première lettre du mot à placer
    - dir (str) : un charactère (h ou v) qui indique la direction du mot
    Valeurs de retour:
    - bool (True ou False)
    """

    re = False
    ret = []
    mot, pos, dir = coup
    l, c = pos

    if dir == 'h':
        for i in range(len(mot)):
            current_letter = plateau[l][c + i]

            if (mot[i] in lettres_joueur) or (mot[i] == current_letter):
                ret.append('True')
            else:
                ret.append('False')

    elif dir == 'v':
        for j in range(len(mot)):
            current_letter = plateau[l + j][c]

            if (mot[j] in lettres_joueur) or (mot[j] == current_letter):
                ret.append('True')
            else:
                ret.append('False')

    if 'False' not in ret:
        re = True
    return(re)


def verif_mot(mot, dico):
    """Cette fonction renvoie True si le mot à placer est bien un mot du dictionnaire.
    False sinon.
    Arguments :
    - mot (str): une chaine de caractères en majuscule qui indique le mot à placer
    - dico (list) : une liste dont chaque élément d'indice i, est un set de mots du dictionnaire de
    longueur (i+1). Par exemple, dico[3] pointe vers un set de tous les mots à 4 lettres.
    Valeurs de retour :
    - bool (True ou False)"""

    ret = False
    if len(mot) <= len(dico) and mot in dico[len(mot)-1]:
        ret = True
    return(ret)


def verif_emplacement(coup, plateau):
    """Cette fonction renvoie True si le mot à placer n'entre
    pas en conflit avec d'autres lettres déjà placées
    auparavant sur le plateau, qui ne correspondent pas aux
    lettres du mot.
    Sinon, la fonction renvoie False.
    On pré-suppose que le mot ne dépasse pas des bornes du plateau.
    Arguments :
    - coup (tuple): un tuple à 3 éléments:
    - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
    - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l),
    et le numéro de la colonne (c) de la première lettre du mot à placer
    - dir (str) : un charactère (h ou v) qui indique la direction du mot
    - plateau (liste): une liste de sous-listes qui représentent
    chacune une ligne du plateau de jeu.
    Elles contiennent chacune, soit un underscore pour
    indiquer que la case est vide, soit une lettre
    si elle a déjà été placée là auparavant.
    Valeurs de retour:
    - bool (True ou False)"""

    ret = True
    mot, pos, dir = coup
    l, c = pos

    list_mot = list(mot)

    for i in range(len(mot)):
        if dir == 'h':
            current_letter = plateau[l][c + i]
        elif dir == 'v':
            current_letter = plateau[l + i][c]

        desired_letter = list_mot[i]

        if current_letter != '_' and current_letter != desired_letter:
            ret = False

    return(ret)


def mot_accepte(plateau, lettres_joueur, coup, dictionnaire, tour):
    """Cette fonction renvoie True si chacune des fonctions suivantes renvoient True:
    verif_premier_tour (uniquement au premier tour)
    verif_lettres_joueur
    verif_mot
    verif_bornes
    verif_emplacement
    Sinon, la fonction renvoie False. Vous devez donc également définir les 5 fonctions ci- dessus pour pouvoir les appeler Arguments :
    - lettres_joueur (liste) : une liste contenant les lettres du joueur
    - plateau (liste): une liste de sous-listes qui représentent
    chacune une ligne du plateau de jeu.
    Elles contiennent chacune, soit un underscore pour
    indiquer que la case est vide, soit une lettre
    si elle a déjà été placée là auparavant.
    - coup (tuple): un tuple à 3 éléments:
    - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
    - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l),
    et le numéro de la colonne (c) de la première lettre du mot à placer
    - dir (str) : un charactère (h ou v) qui indique la direction du mot
    - tour (int) : un entier qui représente le tour du jeu (tour = 1 représente le premier tour)
    - dictionnaire (list) : une liste dont chaque élément d'indice i, est un set de mots du dictionnaire de
    longueur (i+1). Par exemple, dico[3] pointe vers un set de tous les mots à 4 lettres.
    Valeurs de retour:
    - bool (True ou False)
    """

    ret_1 = True
    ret = False

    mot, pos, direction = coup

    if tour == 1 and verif_premier_tour(coup) == False:
        ret_1 = False

    if verif_bornes(coup, (len(plateau), len(plateau[0]))) and verif_lettres_joueur(plateau, lettres_joueur, coup) and verif_mot(mot, dictionnaire) and verif_emplacement(coup, plateau) and ret_1:
        ret = True

    return(ret)


def compte_points(mots, points_lettres):
    """Cette fonction calcule et renvoie le score
    associé à un mot
    Arguments :
    - mot (str) : une chaine de caractère en majuscule qui indique le mot à placer
    - points_lettres (dict) : un dictionnaire contenant
    comme clés les différentes lettres de l'alphabet,
    en majuscule; et comme valeur, les points
    associées à chaque lettre.
    Par exemple:
    points_lettres = {"A" : 1, "B": 3}, si on ne considère
    que les deux premières lettres de l'alphabet
    Valeur de retour:
    - int : points associés au mot placé.
    """

    points = 0

    for i in mots:
        points += points_lettres[i]

    return(points)


def placer_mot(plateau, coup):
    """ Cette fonction modifie le plateau de
    sorte que les lettres du mot à placer soient
    insérées au bon endroit dans la liste de
    sous-listes qui représente le plateau;
    cette fonction renvoie ensuite les lettres du mot
    à placer qui sont déjà présentes sur le plateau
    à l'endroit exact où cette lettre devrait etre
    placée (et qu'il ne faut donc pas retirer du
    chevalet du joueur par la suite)
    Arguments:
    - coup (tuple): un tuple à 3 éléments:
    - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
    - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l),
    et le numéro de la colonne (c) de la première lettre du mot à placer
    - dir (str) : un charactère (h ou v) qui indique la direction du mot
    - plateau (liste) : une liste de sous-listes
    qui représentent chacune une ligne du plateau
    de jeu. Elles contiennent chacune, soit un
    underscore pour indiquer que la case est vide,
    soit une lettre si elle a déjà été placée là
    auparavant.
    Valeur de retour:
    - str : chaine de caractères contenant les lettres déjà présentes sur le plateau à
    l'emplacement du mot (qu'il ne faut donc pas retirer du chevalet du joueur)
    Exemple:
    >>> plateau = [["_", "_", "A","R"],
    ["_", "_", "_","_"],
    ["_", "_", "_","_"],
    ["_", "_", "_","_"]]
    >>> mot = "BAR"
    >>> position = (0,1)
    >>> direction = "h"
    >>> coup = mot,position,direction
    >>> lettres_presentes = placer_mot(plateau,coup)
    >>> print(plateau)
    >>> [["_", "B", "A","R"],
    ["_", "_", "_","_"],
    ["_", "_", "_","_"],
    ["_", "_", "_","_"]]
    >>> print(lettres_presentes)
    >>> "AR"
    """

    ret = ''
    mot, pos, direction = coup
    l, c = pos

    list_mot = list(mot)

    for i in range(len(mot)):
        desired_letter = list_mot[i]

        if direction == 'h':
            current_letter_h = plateau[l][c + i]
            if current_letter_h == '_':
                plateau[l][c + i] = desired_letter
            else:
                ret += current_letter_h

        elif direction == 'v':
            current_letter_v = plateau[l + i][c]
            if current_letter_v == '_':
                plateau[l + i][c] = desired_letter
            else:
                ret += current_letter_v

    return(ret)


def utilise_lettre_plateau(coup, plateau):
    """
    Cette fonction renvoie True si le mot à placer utilise une ou plusieurs lettres
    déjà présentes sur le plateau de jeu.
    Elle renvoie False sinon
    Arguments:
    - coup (tuple) : à 3 éléments :
    - mot (str) : une chaine de caractère en majuscule
    qui indique le mot à placer
    - direction (str) : un charactère (h ou v) qui
    indique la direction du mot
    - position (tuple) : un tuple d'entiers (l,c) qui
    indiquent le numéro de ligne (l),
    et le numéro de la colonne (c) de la première lettre
    du mot à placer
    - plateau (liste) : une liste de 15 sous-listes
    qui représentent chacune une ligne du plateau
    de jeu. Elles contiennent chacune, soit un
    underscore pour indiquer que la case est vide,
    soit une lettre si elle a déjà été placée là
    auparavant.
    - Valeurs de retour:
    - bool (True / False)"""

    ret = False
    mot, pos, dir = coup
    l, c = pos

    list_mot = list(mot)

    for i in range(len(mot)):
        if dir == 'h':
            current_letter = plateau[l][c + i]
        elif dir == 'v':
            current_letter = plateau[l + i][c]

        desired_letter = list_mot[i]

        if current_letter == desired_letter:
            ret = True

    return(ret)


def mots_perpendiculaires(coup, plateau, dico):
    """
    Lorsqu'un mot est placé sur le plateau de jeu, il est
    possible qu'il soit adjacent à des lettres déjà
    présentes sur le plateau. De nouveaux mots perpendiculaires
    au mot à placer sont alors formés.
    3 cas sont possibles:
    - Si aucun mot perpendiculaire n'est formé, cette fonction
    renvoie une liste contenant un élément : le mot à placer.
    - S'il existe des mots perpendiculaires et qu'ils appartiennet
    TOUS au dictionnaire, cette fonction renvoie la liste contenant tous
    les nouveaux mots formés (le mot à placer et les nouveaux mots
    perpendiculaires), triés dans l'ordre alphabétique.
    - S'il existe des mots perpendiculaires et qu'au moins un d'entre
    eux n'existe pas dans le dictionnaire, la fonction renvoie une
    liste vide [].
    On considère que le mot à placer respecte bien les bornes du plateau et
    qu'il n'y a pas de conflit entre les lettres que le joueur veut placer
    sur le plateau et les lettres existantes, aux positions qui seront
    utilisées pour ces lettres. Autrement dit, pour chaque lettre à placer,
    soit la case est vide, soit la lettre à placer est déjà présente.
    Ceci n'est pas à tester dans la fonction, mais c'est un pré-requis à
    son utilisation.
    -Arguments:
    - coup (tuple): un tuple à 3 éléments:
    - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
    - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l),
    et le numéro de la colonne (c) de la première lettre du mot à placer
    - dir (str) : un charactère ("h" ou "v") qui indique la direction du mot
    - plateau (liste) : une liste de 15 sous-listes
    qui représentent chacune une ligne du plateau
    de jeu. Elles contiennent chacune, soit un
    underscore pour indiquer que la case est vide,
    soit une lettre si elle a déjà été placée là
    auparavant.
    - dico (list) : une liste dont chaque élément d'indice i, est un set de mots du dictionnaire de
    longueur (i+1). Par exemple, dico[3] pointe vers un set de tous les mots à 4 lettres.
    - Valeurs de retour:
    - liste de chaine de caractères
    """

    ret = []
    mot, pos, dir = coup
    l, c = pos

    if verif_bornes(coup, (NB_LIGNES, NB_COLONNES)):
        plat = copy.deepcopy(plateau)
        for b in range(len(mot)):
            if dir == "h":
                if plat[l][c + b] == "_":
                    plat[l][c + b] = mot[b].lower()
            elif dir == "v":
                if plat[l + b][c] == "_":
                    plat[l + b][c] = mot[b].lower()

        mot_exist = []
        list_mot_exist = []

        if dir == "h":
            for a in range(len(mot)):
                alist = []
                alistmot = ""
                for b in range(len(plateau)):
                    alist.append(plat[b][c + a])

                d = 1
                whiled = True
                while d < l and whiled:
                    if (l-d) <= len(alist) and alist[l-d] == "_":
                        del alist[:l-d+1]
                        whiled = False

                    d += 1

                e = 1
                whilee = True
                while e < len(alist) and whilee:
                    if (l - (l-d+2) + e) <= len(alist) and alist[l - (l-d+2) + e] == "_":
                        del alist[l - (l-d+2) + e:]
                        whilee = False

                    e += 1
                alistmot = ''.join(alist)

                if len(alistmot) == 1:
                    mot_exist.append('_')
                elif alistmot.isupper():
                    mot_exist.append('-')
                elif alistmot.upper() in dico[len(alistmot)-1]:
                    list_mot_exist.append(alistmot.upper())
                    mot_exist.append('True')
                else:
                    mot_exist.append('False')

        elif dir == "v":
            for a in range(len(mot)):
                alist = copy.deepcopy(plat[l+a])
                alistmot = ""

                d = 1
                whiled = True
                while d < c and whiled:
                    if (c-d) < len(alist) and alist[c-d] == "_":
                        del alist[:c-d+1]
                        whiled = False

                    d += 1

                e = 1
                whilee = True
                while e <= len(plat[0])-c+(c-d) and whilee:
                    if (c - (c-d+2) + e) < len(alist) and alist[c - (c-d+2) + e] == "_":
                        del alist[c - (c-d+2) + e:]
                        whilee = False

                    e += 1
                alistmot = ''.join(alist)

                if len(alistmot) == 1:
                    mot_exist.append('_')
                elif alistmot.isupper():
                    mot_exist.append('-')
                elif alistmot.upper() in dico[len(alistmot)-1]:
                    list_mot_exist.append(alistmot.upper())
                    mot_exist.append('True')
                else:
                    mot_exist.append('False')

        tr = "True" not in mot_exist
        fal = "False" not in mot_exist
        if tr and fal:
            ret = [mot.upper()]
        elif fal:
            list_mot_exist.append(mot.upper())
            ret = sorted(list_mot_exist)
        else:
            ret = []

        # print(mot_exist)

    return(ret)


def casse_multiplicatrice(coup, points_lettres):
    """Cette fonction renvoie True si le mot à placer utilise une ou plusieurs lettres
    déjà présentes sur le plateau de jeu.
    Elle renvoie False sinon
    Arguments:
    - coup (tuple) : à 3 éléments :
        - mot (str) : une chaine de caractère en majuscule
        qui indique le mot à placer
        - direction (str) : un charactère (h ou v) qui
        indique la direction du mot
        - position (tuple) : un tuple d'entiers (l,c) qui
        indiquent le numéro de ligne (l),
        et le numéro de la colonne (c) de la première lettre
        du mot à placer
    - points_lettres (dict) : un dictionnaire contenant
    comme clés les différentes lettres de l'alphabet,
    en majuscule; et comme valeur, les points
    associées à chaque lettre.
    - Valeurs de retour:
    - points (int): les points à rajouter au score
    """

    points = 0
    mot, pos, dir = coup
    l, c = pos

    tupple_a_retirer_lettre_compte_double = []
    tupple_a_retirer_lettre_compte_triple = []
    tupple_a_retirer_mot_compte_double = []
    tupple_a_retirer_mot_compte_triple = []

    for m in range(len(mot)):
        if dir == 'h':
            if (l, c+m) in lettre_compte_double:
                points += points_lettres[mot[m]]
                tupple_a_retirer_lettre_compte_double.append((l, c+m))
            elif (l, c+m) in lettre_compte_triple:
                points += points_lettres[mot[m]]*2
                tupple_a_retirer_lettre_compte_triple.append((l, c+m))
            elif (l, c+m) in mot_compte_double:
                pdh = 0
                for o in mot:
                    pdh += points_lettres[o]
                points += pdh
                tupple_a_retirer_mot_compte_double.append((l, c+m))
            elif (l, c+m) in mot_compte_triple:
                pth = 0
                for p in mot:
                    pth += points_lettres[p]
                points += pth*2
                tupple_a_retirer_mot_compte_triple.append((l, c+m))
        elif dir == 'v':
            if (l+m, c) in lettre_compte_double:
                points += points_lettres[mot[m]]
                tupple_a_retirer_lettre_compte_double.append((l+m, c))
            elif (l+m, c) in lettre_compte_triple:
                points += points_lettres[mot[m]]*2
                tupple_a_retirer_lettre_compte_triple.append((l+m, c))
            elif (l+m, c) in mot_compte_double:
                pdv = 0
                for o in mot:
                    pdv += points_lettres[o]
                points += pdv
                tupple_a_retirer_mot_compte_double.append((l+m, c))
            elif (l+m, c) in mot_compte_triple:
                pt = 0
                for p in mot:
                    pt += points_lettres[p]
                points += pt*2
                tupple_a_retirer_mot_compte_triple.append((l+m, c))

    for tarlcd in tupple_a_retirer_lettre_compte_double:
        lettre_compte_double.remove(tarlcd)
    for tarlct in tupple_a_retirer_lettre_compte_triple:
        lettre_compte_triple.remove(tarlct)
    for tarmcd in tupple_a_retirer_mot_compte_double:
        mot_compte_double.remove(tarmcd)
    for tarmct in tupple_a_retirer_mot_compte_triple:
        mot_compte_triple.remove(tarmct)

    return(points)


def joker(joker_mot, dico_points, dico, lettres_joueurs):
    """Cette fonction propose tout les mots qui peuvents être formé
    en remplacant * par toutes les lettres de l'alphabet.
    Arguments:
    - joker_mot (str): un mot contenant 1 ou 2 caractère *
    - dico_points (dict) : un dictionnaire contenant
    comme clés les différentes lettres de l'alphabet,
    en majuscule; et comme valeur, les points
    associées à chaque lettre.
    - dictionnaire (list) : une liste dont chaque élément d'indice i, est un set de mots du dictionnaire de
    longueur (i+1). Par exemple, dico[3] pointe vers un set de tous les mots à 4 lettres.
    - lettres_joueurs (dict): un dictionnaire contenant
    comme clés le nom des différents joueur; et comme valeur, les lettres
    de celui-ci.
    - Valeurs de retour:
    - points (int): les points à rajouter au score
    - lettres_joueurs (dict): un dictionnaire contenant
    comme clés le nom des différents joueur; et comme valeur, les lettres
    de celui-ci ou le(s) caractère(s) * a(ont) été remplacé par la(les) lettre(s) souhaitée(s)
    """

    mot_choisi = ''

    if joker_mot.count('*') == 2:
        choix_mot1 = []
        for n1 in list(string.ascii_uppercase):
            for m1 in list(string.ascii_uppercase):
                joker_mot1 = copy.deepcopy(joker_mot)
                joker_mot1 = joker_mot1.replace('*', n1, 1)
                joker_mot1 = joker_mot1.replace('*', m1, 1)
                temp_mot1 = verif_mot(joker_mot1, dico)
                if temp_mot1:
                    print(str(n1)+' - '+str(m1)+' : '+joker_mot1)
                    choix_mot1.append((n1, m1))
        if len(choix_mot1) != 0:
            mot_a_jouer1 = retirer_accent(
                input('Avec quelles lettres voulez vous jouer ? : ').replace('-', '')).upper()
            while (len(mot_a_jouer1) != 2) or ((mot_a_jouer1[0], mot_a_jouer1[1]) not in choix_mot1):
                mot_a_jouer1 = retirer_accent(input(
                    'Avec quelles lettres voulez vous jouer ? (les lettres doivent être dans la liste ci-dessus) : ').replace('-', '')).upper()
            mot_choisi = joker_mot.replace('*', mot_a_jouer1[0], 1)
            mot_choisi = joker_mot.replace('*', mot_a_jouer1[1], 1)

            lettres_joueurs = lettres_joueurs.replace('*', mot_a_jouer1[0], 1)
            lettres_joueurs = lettres_joueurs.replace('*', mot_a_jouer1[1], 1)
    else:
        choix_mot3 = []
        for n3 in list(string.ascii_uppercase):
            temp_mot3 = verif_mot(joker_mot.replace('*', n3), dico)
            if temp_mot3:
                print(str(n3)+' : '+joker_mot.replace('*', n3))
                choix_mot3.append(n3)
        if len(choix_mot3) != 0:
            mot_a_jouer3 = retirer_accent(
                input('Avec quelle lettre voulez vous jouer ? : ')).upper()
            while mot_a_jouer3 not in choix_mot3:
                mot_a_jouer3 = retirer_accent(input(
                    'Avec quelle lettre voulez vous jouer ? (la lettre doit être dans la liste ci-dessus) : ')).upper()
            mot_choisi = joker_mot.replace('*', mot_a_jouer3)

            lettres_joueurs = lettres_joueurs.replace('*', mot_a_jouer3)

    return(mot_choisi, lettres_joueurs)


def print_tableau(plateau, lettres_joueur, tour, current_player_number):
    """Cette fonction imprime le plateau et toutes les informations du jeu.
    Arguments: 
    - plateau (liste) : une liste de 15 sous-listes
    qui représentent chacune une ligne du plateau
    de jeu. Elles contiennent chacune, soit un
    underscore pour indiquer que la case est vide,
    soit une lettre si elle a déjà été placée là
    auparavant.
    - lettres_joueurs (dict): un dictionnaire contenant
    comme clés le nom des différents joueur; et comme valeur, les points
    de celui-ci.
    - tour (int): le numero du tour
    - current_player_number (int): l'identifiand du joueur qui joue
    Valeur de retour: /
    """
    t_affiche = str(tour_affiche)
    if len(t_affiche) == 1:
        t_affiche = t_affiche + ' '

    print('\n\n'+('-'*43)+' '+colored('Tour ' +
                                      t_affiche, 'green')+' '+('-'*43)+'\n')
    # print('-----------------------------------------------|-----------------------------------------------')
    print((' '*46)+'SCORE')
    score_number = 1
    for f in players_score.items():
        if score_number == 1 and len(f) > 1:
            score_number = 2
    maxim = 0
    for m in range(len(players)):
        if len(players[m]) > maxim:
            maxim = len(players[m])
    print((' '*((82-maxim)//2))+'  +'+('-'*maxim)+'--+----+')
    rank = 1
    for v, k in reversed(sorted(players_score.items(), key=lambda x: x[1])):
        print((' '*((82-maxim)//2))+str(rank)+' | '+colored(v, players_color[v])+(
            ' '*(maxim-len(v)))+' | '+str(k)+((1+score_number-len(str(k)))*' ')+'|')
        print((' '*((82-maxim)//2))+'  +'+('-'*maxim)+'--+----+')
        rank += 1
    print('\n'+(' '*12)+colored('Mot compte triple', 'white', 'on_red')+' '+colored('Mot compte double', 'white', 'on_magenta') +
          ' '+colored('Lettre compte triple', 'white', 'on_blue')+' '+colored('Lettre compte double', 'white', 'on_cyan'))
    # print('-----------------------------------------------|-----------------------------------------------')#95
    print('\n'+str(' '*((77-len(players[current_player_number]))//2))+"C'est à " + colored(
        players[current_player_number], players_color[players[current_player_number]])+' de jouer !'+'\n')

    nbrh = "       "
    for fnbrh in range(15):
        if fnbrh < 10:
            nbrh += (str(fnbrh) + (' '*5))
        else:
            nbrh += (str(fnbrh) + (' '*4))

    print(nbrh)

    seph = "    "
    for fseph in range(15):
        seph += ('+' + ('-'*5))
    seph += '+'
    print(seph)

    for li in range(15):
        actual_ligne = ""
        if li < 10:
            actual_ligne += (str(li)+'   |')
        else:
            actual_ligne += (str(li)+'  |')

        for ci in range(15):
            if (li, ci) in mot_compte_triple:
                actual_ligne += colored('  ', 'white', 'on_red')+colored(
                    plateau[li][ci], 'white', 'on_red')+colored('  ', 'white', 'on_red')
            elif (li, ci) in mot_compte_double:
                actual_ligne += colored('  ', 'white', 'on_magenta')+colored(
                    plateau[li][ci], 'white', 'on_magenta')+colored('  ', 'white', 'on_magenta')
            elif (li, ci) in lettre_compte_triple:
                actual_ligne += colored('  ', 'white', 'on_blue')+colored(
                    plateau[li][ci], 'white', 'on_blue')+colored('  ', 'white', 'on_blue')
            elif (li, ci) in lettre_compte_double:
                actual_ligne += colored('  ', 'white', 'on_cyan')+colored(
                    plateau[li][ci], 'white', 'on_cyan')+colored('  ', 'white', 'on_cyan')
            else:
                actual_ligne += '  '+plateau[li][ci]+'  '

            actual_ligne += '|'

        print(actual_ligne)
        print(seph)

    print('\n\n=> '+colored(players[current_player_number],
                            players_color[players[current_player_number]])+' appuie sur ENTER pour voir ton chevalet')
    input()
    print(('-'*32)+colored(' | '+' | '.join(lettres_joueur) +
                           ' | ', 'green')+('-'*32)+'\n')


# Main


if not os.path.isfile(DICTIONNAIRE):
    print('Il manque le fichier ', DICTIONNAIRE)
    input('Appuyez sur une touche pour quitter...')
    exit()

if not os.path.isfile(LETRRES):
    print('Il manque le fichier ', LETRRES)
    input('Appuyez sur une touche pour quitter...')
    exit()


init()  # Permet la compatibilité des couleurs pour les terminaux (colorama).


for b in range(15):
    sets_mots.append(set([]))

fl = open(DICTIONNAIRE)
splited = fl.read().split()
for a in range(len(splited)):
    sets_mots[len(splited[a])-1].add(splited[a])
fl.close()

dico_occurences, dico_points = load_fichier_lettres(LETRRES)
lettres_dispo = pioche_init(dico_occurences)
lettres_dispo.extend(['*', '*'])
plateau = plateau_init((15, 15))

print(ASCCI_SCRABBLE)

reg = retirer_accent(input(
    'Appuyez sur R puis ENTER pour voir les règles ou ENTER pour commencer à jouer : ')).upper()
if reg == 'R':
    print(REGLES)

nbr_joueur = input('Nombre de joueur(s) (1 - 4): ')
while nbr_joueur not in ['1', '2', '3', '4']:
    nbr_joueur = input('Nombre de joueur(s) (1 - 4): ')


for j in range(int(nbr_joueur)):
    joueur_nom = input('Nom du Joueur '+str(j+1)+' : ')
    while joueur_nom in players:
        print('Ce nom est déjà pris !')
        joueur_nom = input('Nom du Joueur '+str(j+1)+' : ')

    players.append(joueur_nom)
    players_score[joueur_nom] = 0
    players_color[players[j]] = colors[j]
    lettres_joueurs[players[j]] = ''
    for l in range(7):
        lettre_pioche1 = random.choice(lettres_dispo)
        lettres_joueurs[players[j]] += lettre_pioche1
        lettres_dispo.remove(lettre_pioche1)


while jeu_en_cours:
    print_tableau(
        plateau, lettres_joueurs[players[current_player]], current_tour, current_player)
    not_accepted = True
    mot_accepted = False
    utilise_lettre_plateau_accepted = False
    mots_perpendiculaires_accepted = False
    current_coup = ('', (0, 0), '')
    current_mot = []
    passe = False
    repioche = False
    while not_accepted:
        coup = propose_mot('Numéro de ligne de la première lettre de votre mot (P pour passer son tour et R pour repiocher) : ', 'Numéro de ligne de la première lettre de votre mot (P pour passer son tour, R pour repiocher et seul les chiffres entre 0 et 14 sont acceptés) : ',
                           'Numéro de colonne de la première lettre de votre mot : ', 'Numéro de colonne de la première lettre de votre mot (seul les chiffres sont acceptés) : ', 'Donnez la direction (h = horizontal, v= vertical) : ', 'Quel mot proposez-vous ? : ', 'Quel mot proposez-vous ? (seul les lettres sont acceptés) : ', current_tour)
        if coup == 'P':
            mot_accepted = True
            utilise_lettre_plateau_accepted = True
            mots_perpendiculaires_accepted = True
            passe = True
        elif coup == 'R':
            mot_accepted = True
            utilise_lettre_plateau_accepted = True
            mots_perpendiculaires_accepted = True
            repioche = True
        else:
            passmot, passpos, passdir = coup
            if passmot.count('*') != 0:
                passmot, lettres_joueurs[players[current_player]] = joker(
                    passmot, dico_points, sets_mots, lettres_joueurs[players[current_player]])
            coup = passmot, passpos, passdir
            mot_accepted = mot_accepte(
                plateau, lettres_joueurs[players[current_player]], coup, sets_mots, current_tour)
            if current_tour == 1 and verif_bornes(coup, (NB_LIGNES, NB_COLONNES)):
                utilise_lettre_plateau_accepted = True
            elif verif_bornes(coup, (NB_LIGNES, NB_COLONNES)):
                utilise_lettre_plateau_accepted = utilise_lettre_plateau(
                    coup, plateau)
            mots_perpendiculaires_return = mots_perpendiculaires(
                coup, plateau, sets_mots)
            if len(mots_perpendiculaires_return) > 1:
                utilise_lettre_plateau_accepted = True
            if not mot_accepted:
                if current_tour == 1:
                    print(colored(
                        'Ce mot ne rentre pas dans la grille, veuillez réesayer ! (au 1er tour le mot doit passer par la casse (7, 7))', 'red'))
                else:
                    print(
                        colored('Ce mot ne rentre pas dans la grille, veuillez réesayer !', 'red'))
            elif len(mots_perpendiculaires_return) == 0:
                print(
                    colored('Un ou plusieurs mot(s) perpendiculaire(s) pose(nt) problème !', 'red'))
            elif utilise_lettre_plateau_accepted == False:
                print(colored(
                    'Votre mot doit utiliser au moins une lettre déjà présente sur le plateau !', 'red'))

            else:
                mots_perpendiculaires_accepted = True

            current_mot = mots_perpendiculaires_return
            current_coup = coup

        if mot_accepted == True and utilise_lettre_plateau_accepted == True and mots_perpendiculaires_accepted == True:
            not_accepted = False

    if passe == False and repioche == False:
        for cp in current_mot:
            cp = compte_points(cp, dico_points)
            players_score[players[current_player]] += cp
            print('+ '+str(cp))

            cmpo = casse_multiplicatrice(current_coup, dico_points)
            players_score[players[current_player]] += cmpo
            print('+ '+str(cmpo))

        lettres_deja_presente = placer_mot(plateau, current_coup)

        lettres_a_supprimer = copy.deepcopy(current_coup[0])
        for li in lettres_deja_presente:
            if li in lettres_a_supprimer:
                lettres_a_supprimer = lettres_a_supprimer.replace(li, "", 1)

        for k in lettres_a_supprimer:
            lettres_joueurs[players[current_player]] = lettres_joueurs.get(
                players[current_player]).replace(k, "", 1)

        if len(lettres_a_supprimer) == 7:
            players_score[players[current_player]] += 50
            print(colored(ASCCI_SCRABBLE, 'red'))

        if len(lettres_dispo) >= len(lettres_a_supprimer):
            for p in range(len(lettres_a_supprimer)):
                lettre_pioche2 = random.choice(lettres_dispo)
                lettres_joueurs[players[current_player]] += lettre_pioche2
                lettres_dispo.remove(lettre_pioche2)
        else:
            jeu_en_cours = False

        current_tour += 1

    elif repioche:
        lettres_a_repiocher = retirer_accent(input(
            'Quelle(s) lettre(s) voulez vous échanger ? (/ pour changer de chevalet) : ')).upper()
        lettre_ok = False

        while (lettres_a_repiocher != '/' and lettres_a_repiocher.replace('*', '').isalpha() == False) or (lettres_a_repiocher != '/' and lettre_ok == False):
            ljl = copy.deepcopy(list(lettres_joueurs[players[current_player]]))
            lokl = []
            for v in list(lettres_a_repiocher.upper()):
                if v in ljl:
                    lokl.append('True')
                    ljl.remove(v)
                else:
                    lokl.append('False')
            if not 'False' in lokl:
                lettre_ok = True

            if lettres_a_repiocher.replace('*', '').isalpha() and lettre_ok == False:
                print('Vous ne possédez pas toutes les lettres !')
                lettres_a_repiocher = retirer_accent(input(
                    'Quelle(s) lettre(s) voulez vous échanger ? (/ pour changer de chevalet) : ')).upper()
            elif lettres_a_repiocher.replace('*', '').isalpha() == False:
                lettres_a_repiocher = retirer_accent(input(
                    'Quelle(s) lettre(s) voulez vous échanger ? (/ pour changer de chevalet et seul les lettres sont accaptées) : ')).upper()

        if lettres_a_repiocher == '/':
            if len(lettres_dispo) >= 7:
                lettres_remettre = copy.deepcopy(
                    lettres_joueurs[players[current_player]])
                lettres_joueurs[players[current_player]] = ''
                for l in range(7):
                    lettre_pioche4 = random.choice(lettres_dispo)
                    lettres_joueurs[players[current_player]] += lettre_pioche4
                    lettres_dispo.remove(lettre_pioche4)
                for rm in list(lettres_remettre):
                    lettres_dispo.append(rm)

            else:
                jeu_en_cours = False
        else:
            uplists = list(lettres_a_repiocher.upper())

            for rp in uplists:
                lettre_pioche3 = random.choice(lettres_dispo)
                lettres_joueurs[players[current_player]] += lettre_pioche3
                lettres_dispo.remove(lettre_pioche3)

            for kis in uplists:
                lettres_joueurs[players[current_player]
                                ] = lettres_joueurs[players[current_player]].replace(kis, '', 1)
                lettres_dispo.append(kis)

    elif passe == True:
        joueur_passe += 1

    if current_player == len(players)-1:
        current_player = 0
        tour_affiche += 1
    else:
        current_player += 1

    if len(players) == joueur_passe:
        jeu_en_cours = False

score_list = sorted(players_score.items(), key=lambda x: x[1])
nom_gagnant, points_gagnant = score_list[-1]
print("La partie est finie et c'est "+colored(nom_gagnant,
                                              players_color[nom_gagnant])+' qui a gagné avec '+colored(points_gagnant, players_color[nom_gagnant])+' points !')
