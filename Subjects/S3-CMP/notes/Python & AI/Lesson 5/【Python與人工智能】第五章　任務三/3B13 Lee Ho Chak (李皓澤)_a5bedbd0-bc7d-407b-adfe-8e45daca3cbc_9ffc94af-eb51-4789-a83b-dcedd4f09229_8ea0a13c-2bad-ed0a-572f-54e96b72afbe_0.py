import torch
import torch.nn as nn

class PlayerBrain(nn.Module):
    def __init__(self, input_dim, action_dim):
        super(PlayerBrain, self).__init__()
        # State: Ball pos, Teammate pos, Opponent pos, Stamina
        self.network = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim) # Actions: Move, Pass, Shoot, Tackle
        )

    def forward(self, state):
        return self.network(state)

# Training loop allows players to 'invent' tactics FC26 doesn't have
import networkx as nx

# Create a graph of player relationships
G = nx.Graph()
G.add_edge("Mbappe", "Vinicius", weight=0.85) # High chemistry
G.add_edge("Mbappe", "NewSigning", weight=0.10) # Low chemistry

# Calculate how passing efficiency drops based on 'social distance'
def get_pass_accuracy(player_a, player_b):
    base_acc = 0.90
    chem = G.get_edge_data(player_a, player_b, default={'weight': 0.5})['weight']
    return base_acc * chem