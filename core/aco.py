# core/aco.py
import numpy as np
import random

class AntColonyOptimizer:
    def __init__(self, distances, n_ants, n_best, n_iterations, decay, alpha=1, beta=1):
        self.distances = distances
        # Feromon matrisini başlat
        self.pheromone = np.ones(self.distances.shape) / len(distances)
        self.all_inds = range(len(distances))
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        self.history = [] 

    def run(self):
        best_overall_path = None
        best_overall_dist = float('inf')

        for i in range(self.n_iterations):
            all_paths = []
            for _ in range(self.n_ants):
                path = self.gen_path(0) # 0 -> Merkez
                if path is None:
                    continue
                
                dist = self.gen_path_dist(path)
                all_paths.append((path, dist))
                
                if dist < best_overall_dist:
                    best_overall_dist = dist
                    best_overall_path = path

            # En iyi yollara feromon bırak
            if all_paths:
                self.spread_pheronome(all_paths, self.n_best)
                self.history.append(best_overall_dist)
        
        # Hata koruması: Eğer yol bulunamadıysa varsayılan rota dön
        if best_overall_path is None:
            return list(self.all_inds) + [0], 0, []

        return best_overall_path, best_overall_dist, self.history

    def gen_path(self, start_node):
        path = [start_node]
        visited = set(path)
        prev = start_node
        
        for _ in range(len(self.distances) - 1):
            move = self.pick_move(self.pheromone[prev], self.distances[prev], visited)
            if move is None:
                return None 
            path.append(move)
            prev = move
            visited.add(move)
        
        path.append(start_node) # Merkeze dönüş
        return path

    def pick_move(self, pheromone, dist, visited):
        pheromone = np.copy(pheromone)
        pheromone[list(visited)] = 0 

        # Olasılık hesaplama (0'a bölme korumalı)
        try:
            row = (pheromone ** self.alpha) * ((1.0 / (dist + 0.0001)) ** self.beta)
        except RuntimeWarning:
            available = list(set(self.all_inds) - visited)
            return random.choice(available)

        # NaN değerleri temizle
        row = np.nan_to_num(row)

        if row.sum() == 0:
            available = list(set(self.all_inds) - visited)
            if not available:
                return None
            return random.choice(available)

        norm_row = row / row.sum()
        
        if np.isnan(norm_row).any():
             available = list(set(self.all_inds) - visited)
             return random.choice(available)

        move = np.random.choice(self.all_inds, 1, p=norm_row)[0]
        return move

    def spread_pheronome(self, all_paths, n_best):
        """
        DÜZELTİLEN KISIM BURASI:
        Artık tek bir noktaya değil, iki şehir arasındaki yola (edge) feromon bırakıyor.
        Böylece 'Array truth value ambiguous' hatası asla oluşmaz.
        """
        sorted_paths = sorted(all_paths, key=lambda x: x[1])
        
        for path, dist in sorted_paths[:n_best]:
            # Rotadaki her bir adım için (örn: A'dan B'ye)
            for i in range(len(path) - 1):
                start_node = path[i]
                end_node = path[i+1]
                
                # İki nokta arasındaki mesafe
                d = self.distances[start_node][end_node]
                
                if d > 0:
                    # Feromon miktarını arttır (Mesafe kısaysa daha çok artar)
                    delta = 1.0 / d
                    self.pheromone[start_node][end_node] += delta
                    self.pheromone[end_node][start_node] += delta # Ters yönü de güçlendir
        
        # Buharlaşma
        self.pheromone *= self.decay

    def gen_path_dist(self, path):
        total_dist = 0
        for i in range(len(path) - 1):
            total_dist += self.distances[path[i]][path[i+1]]
        return total_dist