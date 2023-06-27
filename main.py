import random
import concurrent.futures
import threading
import numpy as np
import soundfile as sf

class Catraca(threading.Thread):
    def __init__(self, key):
        super().__init__()
        self.torcedores = None
        self.torcedores_casa = None
        self.torcedores_rival = None
        self.key = key

    def run(self):
        self.gerar_numeros()
        self.encriptar(chave=self.key)

    #Complexidade O(1)
    def gerar_numeros(self):
        self.torcedores = random.randint(0, 1000)
        self.torcedores_casa = random.randint(0, self.torcedores)
        self.torcedores_rival = self.torcedores - self.torcedores_casa

    #Complexidade O(1)
    def _aplicar_cifra_cesar(self, valor, chave):
        return (valor + chave) * 1001

    #Complexidade O(1)
    def encriptar(self, chave):
        self.torcedores = self._aplicar_cifra_cesar(self.torcedores, chave)
        self.torcedores_casa = self._aplicar_cifra_cesar(self.torcedores_casa, chave)
        self.torcedores_rival = self._aplicar_cifra_cesar(self.torcedores_rival, chave)
   
class CatracaManager:
    def __init__(self, num_catracas, key):
        self.num_catracas = num_catracas
        self.catracas = []
        self.key = key

    #complexidade O(N)
    def criar_catracas(self):
        for _ in range(self.num_catracas):
            catraca = Catraca(self.key)
            self.catracas.append(catraca)

    #complexidade O(N)
    def gerar_numeros_catracas(self):
        for catraca in self.catracas:
            catraca.start()

        for catraca in self.catracas:
            catraca.join()

    #Complexidade O(N)
    def desencriptar(self, chave):
        for catraca in self.catracas:
            catraca.torcedores = self._desaplicar_cifra_cesar(catraca.torcedores, chave)
            catraca.torcedores_casa = self._desaplicar_cifra_cesar(catraca.torcedores_casa, chave)
            catraca.torcedores_rival = self._desaplicar_cifra_cesar(catraca.torcedores_rival, chave)

    #Complexidade O(1)
    def _desaplicar_cifra_cesar(self, valor, chave):
        return (valor // 1001) - chave

    #complexidade O(N)
    def calcular_total(self):
        total_torcedores = 0
        total_casa = 0
        total_visitante = 0

        for catraca in self.catracas:
            total_torcedores += catraca.torcedores
            total_casa += catraca.torcedores_casa
            total_visitante += catraca.torcedores_rival

        return total_torcedores, total_casa, total_visitante

    #complexidade O(1)
    def imprimir_total(self, total_torcedores, total_casa, total_visitante):
        print(f"Total de torcedores: {total_torcedores}")
        print(f"Total de torcedores do time da casa: {total_casa}")
        print(f"Total de torcedores do time de fora: {total_visitante}")

    #complexidade O(N)
    def imprimir_catracas(self):
        for i, catraca in enumerate(self.catracas, start=1):
            print(f"Catraca {i}")
            print(f"Torcedores: {catraca.torcedores}")
            print(f"Torcedores do time da casa: {catraca.torcedores_casa}")
            print(f"Torcedores do time de fora: {catraca.torcedores_rival}")

    #complexidade O(N^2)
    @staticmethod
    def organizar_ordem(lista):
        n = len(lista)

        for i in range(n):
            for j in range(0, n - i - 1):
                if lista[j] > lista[j + 1]:
                    lista[j], lista[j + 1] = lista[j + 1], lista[j]

        return lista

    #complexidade O(N)
    def imprimir_ordem_crescente(self):
        lista_torcedores_catraca = []
        lista_torcedores_casa = []
        lista_torcedores_visitante = []

        for catraca in self.catracas:
            lista_torcedores_catraca.append(catraca.torcedores)
            lista_torcedores_casa.append(catraca.torcedores_casa)
            lista_torcedores_visitante.append(catraca.torcedores_rival)

        semaforo = threading.Semaphore(1)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            def organizar_e_imprimir(tipo, lista):
                semaforo.acquire()
                print(f"Ordem crescente do total de torcedores {tipo} por catraca: ")
                print(self.organizar_ordem(lista))
                semaforo.release()

            futures = []
            futures.append(executor.submit(organizar_e_imprimir, "geral", lista_torcedores_catraca))
            futures.append(executor.submit(organizar_e_imprimir, "do time da casa", lista_torcedores_casa))
            futures.append(executor.submit(organizar_e_imprimir, "do time visitante", lista_torcedores_visitante))

            concurrent.futures.wait(futures)

    #complexidade O(2^N)
    def gerar_conjuntos_torcedores_casa(self):
        def gerar_combinacao(i):
            combinacao = []
            for j in range(self.num_catracas):
                if i & (1 << j):
                    combinacao.append(self.catracas[j].torcedores_casa)
                else:
                    combinacao.append("")
            return combinacao

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(gerar_combinacao, i) for i in range(2 ** self.num_catracas)]
            combinacoes = [f.result() for f in concurrent.futures.as_completed(futures)]

        print(combinacoes)


if __name__ == '__main__':
    # Caminho para o arquivo WAV
    audio_file = 'C:/Users/Marcos/Documents/labs/TrabCDA/trab2/cenario2/audio/ruido.wav'

    # Carregar o arquivo de áudio
    audio_data, sample_rate = sf.read(audio_file)

    # Convertendo o áudio para um array numérico
    audio_data = audio_data.astype(float)

    # Calcula a média dos valores absolutos dos dados de áudio
    audio_mean = np.mean(np.abs(audio_data))

    # Define uma chave baseada na média do áudio
    key = int(audio_mean * 1000)

    manager = CatracaManager(10, key)

    manager.criar_catracas()
    manager.gerar_numeros_catracas()

    # Desencriptar os valores antes de realizar outras operações
    manager.desencriptar(key)

    total_torcedores, total_casa, total_visitante = manager.calcular_total()
    manager.imprimir_total(total_torcedores, total_casa, total_visitante)
    manager.imprimir_catracas()
    manager.imprimir_ordem_crescente()
    manager.gerar_conjuntos_torcedores_casa()