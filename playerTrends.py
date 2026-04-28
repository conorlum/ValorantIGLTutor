import pyautogui
import time
import json
import os
import shutil
from PIL import Image
import imagehash
import glob
import shutil
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout
import re
from trackerScraper import *

def createKillOrderGraph():
	G = nx.DiGraph()
	G.add_weighted_edges_from([
		("5v5", "4v5", 0),
		("5v5", "5v4", 0),

		("4v5", "3v5", 0),
		("4v5", "4v4", 0),
		("5v4", "4v4", 0),
		("5v4", "5v3", 0),

		("3v5", "2v5", 0),
		("3v5", "3v4", 0),
		("4v4", "3v4", 0),
		("4v4", "4v3", 0),
		("5v3", "4v3", 0),
		("5v3", "5v2", 0),

		("2v5", "1v5", 0),
		("2v5", "2v4", 0),
		("3v4", "2v4", 0),
		("3v4", "3v3", 0),
		("4v3", "3v3", 0),
		("4v3", "4v2", 0), 
		("5v2", "4v2", 0),
		("5v2", "5v1", 0),

		("1v5", "0v5", 0),
		("1v5", "1v4", 0),
		("2v4", "1v4", 0),
		("2v4", "2v3", 0),
		("3v3", "2v3", 0),
		("3v3", "3v2", 0),
		("4v2", "3v2", 0),
		("4v2", "4v1", 0),
		("5v1", "4v1", 0),
		("5v1", "5v0", 0),

		("1v4", "0v4", 0),
		("1v4", "1v3", 0),
		("2v3", "1v3", 0),
		("2v3", "2v2", 0),
		("3v2", "2v2", 0),
		("3v2", "3v1", 0),
		("4v1", "3v1", 0),
		("4v1", "4v0", 0),

		("1v3", "0v3", 0),
		("1v3", "1v2", 0),
		("2v2", "1v2", 0),
		("2v2", "2v1", 0),
		("3v1", "2v1", 0),
		("3v1", "3v0", 0),

		("1v2", "0v2", 0),
		("1v2", "1v1", 0),
		("2v1", "1v1", 0),
		("2v1", "2v0", 0),

		("1v1", "0v1", 0),
		("1v1", "1v0", 0)
	])
	return G

def diamond_layout(G, layers):
    pos = {}
    y_gap = 1.0
    x_gap = 1.0

    node_list = list(G.nodes)
    idx = 0

    for layer_idx, layer_size in enumerate(layers):
        y = -layer_idx * y_gap

        # center nodes horizontally
        x_start = - (layer_size - 1) / 2

        for i in range(layer_size):
            if idx >= len(node_list):
                break

            x = x_start + i * x_gap
            pos[node_list[idx]] = (x, y)
            idx += 1

    return pos

def AddToKillOrderGraph(roundKillLogs, playersRoundInfo, player, G):

	player = playersRoundInfo[player]
	agent = player["Agent"]
	team = player["Team"]

	for roundIndex in range(0,len(player["RoundInfo"])):

		for killLog in roundKillLogs[str(roundIndex+1)]:

			if killLog["Event"] == "Kill":
				beforeState = None
				afterState = None
				if killLog["killerCharacter"] == agent and killLog["killerTeam"] == team:
					if "1" in team:
						beforeState = str(killLog["playersOnTeam"][0]) + "v" + str(killLog["playersOnTeam"][1])
						afterState = str(killLog["playersOnTeam"][0]) + "v" + str(killLog["playersOnTeam"][1] - 1)
					else:
						beforeState = str(killLog["playersOnTeam"][1]) + "v" + str(killLog["playersOnTeam"][0])
						afterState = str(killLog["playersOnTeam"][1]) + "v" + str(killLog["playersOnTeam"][0] - 1)

					if G.has_edge(beforeState, afterState):
						G[beforeState][afterState]["weight"] += 1
					else:
						G.add_edge(beforeState, afterState, weight=1)



				if killLog["deathCharacter"] == agent and killLog["deathTeam"] == team:
					if "1" in team:
						beforeState = str(killLog["playersOnTeam"][0]) + "v" + str(killLog["playersOnTeam"][1])
						afterState = str(killLog["playersOnTeam"][0] - 1) + "v" + str(killLog["playersOnTeam"][1])
					else:
						beforeState = str(killLog["playersOnTeam"][1]) + "v" + str(killLog["playersOnTeam"][0])
						afterState = str(killLog["playersOnTeam"][1] - 1) + "v" + str(killLog["playersOnTeam"][0])

					if G.has_edge(beforeState, afterState):
						G[beforeState][afterState]["weight"] -= 1
					else:
						G.add_edge(beforeState, afterState, weight=1)


def displayKillOrderGraph(killOrderGraph):
	layers = [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]
	pos = diamond_layout(killOrderGraph, layers)

	plt.figure(figsize=(7,5))

	# Draw nodes
	nx.draw_networkx_nodes(killOrderGraph, pos, node_size=800, node_color="lightblue")

	# Draw edges with arrowheads
	nx.draw_networkx_edges(
		killOrderGraph, pos,
		arrowstyle='-|>',
		arrowsize=20,
		width=2
	)

	# Draw labels on nodes
	nx.draw_networkx_labels(killOrderGraph, pos, font_size=12)

	# Draw edge labels (weights)
	edge_labels = nx.get_edge_attributes(killOrderGraph, 'weight')
	nx.draw_networkx_edge_labels(killOrderGraph, pos, edge_labels=edge_labels, font_size=12)

	plt.axis("off")
	plt.show()

def getFilenamesForUsername(playerUsername):
	with open('UsernameToFilename.json', 'r') as file:
		data = json.load(file)

	return data[playerUsername]


if __name__ == "__main__":
	playerUsername = input("enter player name: ")

	killOrderGraph = createKillOrderGraph()

	filenames = getFilenamesForUsername(playerUsername)

	for filename in filenames:
		(roundOutcomes, roundKillLogs, playersRoundInfo) = getBasicInfo(filename)
		AddToKillOrderGraph(roundKillLogs, playersRoundInfo, playerUsername, killOrderGraph)

	displayKillOrderGraph(killOrderGraph)
