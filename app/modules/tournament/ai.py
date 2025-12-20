import random
import time
# No json needed anymore for cloning
from app.modules.tournament.engine import QuantumState

class QuantumAI:
    def __init__(self):
        self.cols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.piece_values = {'p': 10, 'n': 30, 'b': 30, 'r': 50, 'q': 90, 'k': 900}

    def get_color(self, char):
        return 'white' if char.isupper() else 'black'

    def evaluate_board(self, frontend_data, ai_color):
        score = 0
        for data in frontend_data.values():
            val = self.piece_values.get(data['type'].lower(), 0)
            prob = data['prob']
            if self.get_color(data['type']) == ai_color:
                score += val * prob
            else:
                score -= val * prob
        return score

    def calculate_move(self, engine: QuantumState, ai_color='black', difficulty='normal'):
        time.sleep(0.5)
        
        candidates = []
        board_simple = engine.get_simple_board()
        my_pieces = [sq for sq, p in board_simple.items() if self.get_color(p) == ai_color]
        
        for src in my_pieces:
            p_type = board_simple[src]
            valid_targets = engine._get_valid_targets(src, p_type)
            for tgt in valid_targets:
                candidates.append(f"{src}{tgt}")
                if difficulty == 'hard' and random.random() < 0.1 and len(valid_targets) > 1:
                    t2 = random.choice(valid_targets)
                    if t2 != tgt:
                        candidates.append(f"{src}{tgt}^{src}{t2}")

        random.shuffle(candidates)
        if not candidates: return []

        if difficulty == 'easy': return candidates

        if difficulty == 'normal':
            captures = [m for m in candidates if m[2:] in board_simple]
            return captures + candidates

        # HARD MODE
        best_moves = []
        best_score = -99999
        
        for move in candidates[:15]:
            # CRITICAL FIX: Use clone() instead of JSON
            test = engine.clone()
            
            if test.apply_move(move):
                score = self.evaluate_board(test.get_frontend_board(), ai_color)
                if score > best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)
        
        return best_moves if best_moves else candidates
