import random
import json
import cmath
import math

class QuantumState:
    def __init__(self):
        self.board = self._init_board()
        self.entanglements = {} 
        self.cols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.piece_values = {'p': 10, 'n': 30, 'b': 30, 'r': 50, 'q': 90, 'k': 900}

    def _init_board(self):
        data = {}
        cols = ['a','b','c','d','e','f','g','h']
        def place(r, c, p):
            sq = f"{cols[c]}{r}"
            pid = (r * 8) + c 
            data[sq] = [{'type': p, 'amp': complex(1.0, 0.0), 'id': pid, 'phase': 0.0}]

        for i in range(8): place(2, i, 'P'); place(7, i, 'p')
        place(1, 0, 'R'); place(1, 1, 'N'); place(1, 2, 'B'); place(1, 3, 'Q')
        place(1, 4, 'K'); place(1, 5, 'B'); place(1, 6, 'N'); place(1, 7, 'R')
        place(8, 0, 'r'); place(8, 1, 'n'); place(8, 2, 'b'); place(8, 3, 'q')
        place(8, 4, 'k'); place(8, 5, 'b'); place(8, 6, 'n'); place(8, 7, 'r')
        return data

    # --- CRITICAL FIX: Proper Cloning ---
    def clone(self):
        """Creates a deep copy of the state preserving Complex Numbers."""
        new_state = QuantumState()
        new_board = {}
        for sq, pieces in self.board.items():
            new_pieces = []
            for p in pieces:
                # Copy dict but keep complex numbers intact
                new_p = p.copy() 
                new_pieces.append(new_p)
            new_board[sq] = new_pieces
        
        new_state.board = new_board
        new_state.entanglements = self.entanglements.copy()
        return new_state

    # --- HELPERS ---
    def _get_color(self, p_type):
        return 'white' if p_type.isupper() else 'black'

    def _is_on_board(self, c, r):
        return 0 <= c < 8 and 1 <= r <= 8

    def _get_valid_targets(self, src, p_type):
        c_idx = self.cols.index(src[0])
        r_idx = int(src[1])
        color = self._get_color(p_type)
        type_lower = p_type.lower()
        valid_targets = []

        def add_if_valid(c, r, check_path=False):
            if not self._is_on_board(c, r): return False
            tgt = f"{self.cols[c]}{r}"
            
            if check_path:
                if tgt in self.board and self.board[tgt]:
                    if self._get_color(self.board[tgt][0]['type']) != color:
                        valid_targets.append(tgt)
                    return False
                else:
                    valid_targets.append(tgt)
                    return True
            else:
                if tgt in self.board and self.board[tgt]:
                    if self._get_color(self.board[tgt][0]['type']) != color:
                        valid_targets.append(tgt)
                else:
                    valid_targets.append(tgt)
                return True

        if type_lower == 'p':
            direction = 1 if color == 'white' else -1
            f1 = f"{self.cols[c_idx]}{r_idx + direction}"
            if self._is_on_board(c_idx, r_idx + direction) and (f1 not in self.board or not self.board[f1]):
                valid_targets.append(f1)
                start = 2 if color == 'white' else 7
                f2 = f"{self.cols[c_idx]}{r_idx + direction*2}"
                if r_idx == start and (f2 not in self.board or not self.board[f2]):
                    valid_targets.append(f2)
            for dc in [-1, 1]:
                if self._is_on_board(c_idx + dc, r_idx + direction):
                    tgt = f"{self.cols[c_idx+dc]}{r_idx + direction}"
                    if tgt in self.board and self.board[tgt] and self._get_color(self.board[tgt][0]['type']) != color:
                        valid_targets.append(tgt)

        elif type_lower == 'n':
            for dc, dr in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
                add_if_valid(c_idx+dc, r_idx+dr)

        elif type_lower == 'k':
            for dc in [-1,0,1]:
                for dr in [-1,0,1]:
                    if dc or dr: add_if_valid(c_idx+dc, r_idx+dr)

        else:
            dirs = []
            if type_lower in ['r','q']: dirs += [(0,1),(0,-1),(1,0),(-1,0)]
            if type_lower in ['b','q']: dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
            for dc, dr in dirs:
                for i in range(1, 8):
                    if not add_if_valid(c_idx + dc*i, r_idx + dr*i, check_path=True): break
        
        return valid_targets

    def apply_move(self, move_str):
        if '^' in move_str:
            parts = move_str.split('^')
            m1, m2 = parts[0], parts[1]
            src = m1[:2]; t1 = m1[2:]; t2 = m2[2:]
            
            if src not in self.board or not self.board[src]: return False
            piece = self.board[src][0]
            if piece['type'].lower() == 'p': return False
            
            valid_targets = self._get_valid_targets(src, piece['type'])
            if t1 not in valid_targets or t2 not in valid_targets: return False
            if t1 == t2: return False

            self.board[src].pop(0)
            if not self.board[src]: del self.board[src]
            
            factor_real = complex(1.0/math.sqrt(2), 0)
            factor_imag = complex(0, 1.0/math.sqrt(2))
            
            p1 = piece.copy(); p1['amp'] = piece['amp'] * factor_real
            p2 = piece.copy(); p2['amp'] = piece['amp'] * factor_imag
            
            self.board.setdefault(t1, []).append(p1)
            self.board.setdefault(t2, []).append(p2)
            
            if piece['id'] not in self.entanglements:
                self.entanglements[piece['id']] = f"#{random.randint(0, 0xFFFFFF):06x}"
            return True

        src = move_str[:2]; tgt = move_str[2:]
        if src not in self.board or not self.board[src]: return False
        
        piece = self.board[src][0]
        valid_targets = self._get_valid_targets(src, piece['type'])
        
        is_merge = False
        if tgt in self.board:
            for tp in self.board[tgt]:
                if tp['id'] == piece['id']:
                    is_merge = True
                    break
        
        if not is_merge and tgt not in valid_targets: return False

        if is_merge:
            target_list = self.board[tgt]
            for tp in target_list:
                if tp['id'] == piece['id']:
                    tp['amp'] += piece['amp']
                    prob = abs(tp['amp'])**2
                    if prob > 1.0: tp['amp'] /= abs(tp['amp'])
                    self.board[src].pop(0)
                    if not self.board[src]: del self.board[src]
                    return True
            return False

        if tgt in self.board and self.board[tgt]:
            target_piece = self.board[tgt][0]
            target_prob = abs(target_piece['amp']) ** 2
            if random.random() > target_prob: return False 
            else: self.board[tgt] = []
        
        p = self.board[src].pop(0)
        if not self.board[src]: del self.board[src]
        self.board.setdefault(tgt, []).append(p)
        return True

    def get_simple_board(self):
        output = {}
        for sq, pieces in self.board.items():
            if pieces: 
                best_p = max(pieces, key=lambda x: abs(x['amp']))
                output[sq] = best_p['type']
        return output

    def get_frontend_board(self):
        output = {}
        for sq, pieces in self.board.items():
            if not pieces: continue
            total_prob = sum([abs(p['amp'])**2 for p in pieces])
            if total_prob < 0.01: continue
            
            p = pieces[0]
            phase = math.degrees(cmath.phase(p['amp']))
            data = {'type': p['type'], 'prob': min(1.0, total_prob), 'id': p['id'], 'phase': int(phase)}
            if p['id'] in self.entanglements:
                data['entangle_color'] = self.entanglements[p['id']]
            output[sq] = data
        return output

    def check_game_over(self):
        white_prob = 0; black_prob = 0
        for pieces in self.board.values():
            for p in pieces:
                if p['type'] == 'K': white_prob += abs(p['amp'])**2
                if p['type'] == 'k': black_prob += abs(p['amp'])**2
        
        if white_prob < 0.1: return {"game_over": True, "winner": "black"}
        if black_prob < 0.1: return {"game_over": True, "winner": "white"}
        return {"game_over": False}

    def load_game(self, hist):
        if not hist: return
        for m in hist.split(','): self.apply_move(m)

QuantumEngine = QuantumState
def get_board_state(h):
    e = QuantumState()
    e.load_game(h)
    return {"board_data": e.get_frontend_board()}
