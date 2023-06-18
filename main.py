import random;
import concurrent.futures;
import threading;
import soundfile as sf
import numpy as np

# Caminho para o arquivo WAV
audio_file = 'C:/Users/Marcos/Documents/labs/TrabCDA/trab2/cenario2/audio/ruido.wav'

# Carregar o arquivo de áudio
audio_data, sample_rate = sf.read(audio_file)

# Convertendo o áudio para um array numérico
audio_data = audio_data.astype(float)

def gerar_numeros_audio(audio_data, num_numbers):
    # Calcula a média dos valores absolutos dos dados de áudio
    audio_mean = np.mean(np.abs(audio_data))

    # Define uma semente baseada na média do áudio
    seed = int(audio_mean * 10000000000000000000)

    # Inicializa o gerador de números pseudoaleatórios
    random.seed(seed)

    # Gera os números aleatórios
    random_numbers = [random.random() for _ in range(num_numbers)]
    # Multiplica pela escala e converte para int
    scaled_numbers = list(map(lambda x: int(x * 1000), random_numbers))  
    # Limita os valores entre 0 e 1000
    clipped_numbers = np.clip(scaled_numbers, 0, 1000)  

    return clipped_numbers

# Função de complexidade constante O(1)
def gerar_numeros(torcedores):
    torcedores_casa = random.randint(0, int(torcedores))
    torcedores_rival = int(torcedores) - torcedores_casa

    return torcedores_casa, torcedores_rival

# Função de complexidade constante O(1)
def criar_catraca (a):
    b, c = gerar_numeros(a)
    catraca = [int(a), b, c]

    return catraca

# Função de complexidade constante O(1)
def gerar_numeros_threads(num_threads):
    numeros = gerar_numeros_audio(audio_data, num_threads)
    catracas = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for i in range(num_threads):
            future = executor.submit(criar_catraca, numeros[i])
            catracas.append(future.result())
    return catracas

# Função de complexidade linear O(N)
def calcular_total(lista):
    total_torcedores = 0
    total_casa = 0
    total_visitante = 0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Define a função que será executada para cada item da lista
        def calcular(item):
            nonlocal total_torcedores, total_casa, total_visitante
            total_torcedores += item[0]
            total_casa += item[1]
            total_visitante += item[2]

        # Submete a função "calcular" para ser executada em paralelo para cada item da lista
        futures = [executor.submit(calcular, item) for item in lista]

        # Aguarda a conclusão de todas as execuções
        concurrent.futures.wait(futures)

    return total_torcedores, total_casa, total_visitante

# Função de complexidade constante O(1)
def imprimir_total(total_torcedores, total_casa, total_visitante):
    print(f"Total de torcedores: {total_torcedores}")
    print(f"Total de torcedores do time da casa: {total_casa}")
    print(f"Total de torcedores do time de fora: {total_visitante}")

# Função de complexidade linear O(N)
def imprimir_catraca(lista):
    semaforo = threading.Semaphore(1)  # cria um semáforo para controlar o acesso à seção de impressão
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Define a função que será executada para cada item da lista
        def imprimir(item):
            semaforo.acquire()  # aguarda acesso ao semáforo
            print(f"Catraca {lista.index(item) + 1}")
            print(f"Torcedores: {item[0]}")
            print(f"Torcedores do time da casa: {item[1]}")
            print(f"Torcedores do time de fora: {item[2]}")
            semaforo.release()  # libera o semáforo para a próxima thread

        # Submete a função "imprimir" para ser executada em paralelo para cada item da lista
        futures = [executor.submit(imprimir, item) for item in lista]

        # Aguarda a conclusão de todas as execuções
        concurrent.futures.wait(futures)

# Função de complexidade quadrática O(N^2)
def organizar_ordem(lista):
    n = len(lista)
    
    for i in range(n):
        for j in range(0, n-i-1):
            if lista[j] > lista[j+1]:
                lista[j], lista[j+1] = lista[j+1], lista[j]
    
    return lista

# Função de complexidade linear O(N)
def imprimir_ordem_crescente(lista):
    lista_torcedores_catraca = []
    lista_torcedores_casa = []
    lista_torcedores_visitante = []

    for item in lista:
        lista_torcedores_catraca.append(item[0])
        lista_torcedores_casa.append(item[1])
        lista_torcedores_visitante.append(item[2])

    semaforo = threading.Semaphore(1) # cria um semáforo para controlar o acesso à seção de impressão

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Define a função que será executada para cada lista
        def organizar_e_imprimir(tipo, lista):
            semaforo.acquire() # aguarda acesso ao semáforo
            print(f"Ordem crescente do total de torcedores {tipo} por catraca: ")
            print(organizar_ordem(lista))
            semaforo.release() # libera o semáforo para a próxima thread

        # Submete a função "organizar_e_imprimir" para ser executada em paralelo para cada lista
        futures = []
        futures.append(executor.submit(organizar_e_imprimir, "geral", lista_torcedores_catraca))
        futures.append(executor.submit(organizar_e_imprimir, "do time da casa", lista_torcedores_casa))
        futures.append(executor.submit(organizar_e_imprimir, "do time visitante", lista_torcedores_visitante))

        # Aguarda a conclusão de todas as execuções
        concurrent.futures.wait(futures)

# Função de complexidade exponencial O(2^N)
def gerar_conjuntos_torcedores_casa(lista):
    n = len(lista)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Define a função que será executada para cada lista
        def gerar_combinacao(i):
            combinacao = []
            for j in range(n):
                if i & (1 << j):
                    combinacao.append(lista[j][1])
                else:
                    combinacao.append("")
            return combinacao
        # Submete a função "gerar_combinacao" para ser executada em paralelo para cada valor de i
        futures = [executor.submit(gerar_combinacao, i) for i in range(2**n)]

        # Aguarda a conclusão de todas as execuções e adiciona as combinações geradas à lista "combinacoes"
        combinacoes = [f.result() for f in concurrent.futures.as_completed(futures)]

    print(combinacoes)

if __name__ == '__main__':
    lista_geral = gerar_numeros_threads(10)
    
    total_torcedores, total_casa, total_visitante = calcular_total(lista_geral)
    imprimir_total(total_torcedores, total_casa, total_visitante)
    imprimir_catraca(lista_geral)
    imprimir_ordem_crescente(lista_geral)
    gerar_conjuntos_torcedores_casa(lista_geral)