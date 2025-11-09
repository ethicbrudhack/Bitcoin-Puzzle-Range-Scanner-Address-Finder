import hashlib
import base58
import random
import os
import sys
import multiprocessing
import ecdsa
from bech32 import bech32_encode, convertbits
import psutil
import time
import threading

ADDRESS_FILE = "adresy.txt"
OUTPUT_FILE = "znalezioneBTC.txt"
SHOW_GENERATED = True
PROCESSES = 2  # dostosuj do CPU

# === 1. Wczytanie adresów ===
def load_addresses():
    if not os.path.exists(ADDRESS_FILE):
        print(f"Błąd: Brak pliku {ADDRESS_FILE}!")
        sys.exit(1)

    addresses = {}
    with open(ADDRESS_FILE, "r", encoding="utf-8") as file:
        for line in file:
            address = line.strip().split()[0]
            if address.startswith(("1", "3", "bc1")):
                addresses[address] = True

    print(f"Wczytano {len(addresses)} adresów.")
    return addresses

# === 2. Generowanie klucza z nieregularnymi skokami ===
def jump_generator(start, stop, jump_range):
    position = random.randint(start, stop)
    while True:
        offset = random.randint(jump_range // 2, jump_range + jump_range // 2)
        position = (position + offset) % (stop - start) + start
        yield position

# === 3. Konwersja klucza prywatnego na adresy ===
def private_key_to_addresses(private_key):
    sk = ecdsa.SigningKey.from_secret_exponent(private_key, curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    pubkey_bytes = b'\x04' + vk.to_string()

    # Legacy (1...)
    ripemd160 = hashlib.new('ripemd160', hashlib.sha256(pubkey_bytes).digest()).digest()
    extended = b'\x00' + ripemd160
    checksum = hashlib.sha256(hashlib.sha256(extended).digest()).digest()[:4]
    legacy_address = base58.b58encode(extended + checksum).decode()

    # P2SH (3...)
    extended_p2sh = b'\x05' + ripemd160
    checksum_p2sh = hashlib.sha256(hashlib.sha256(extended_p2sh).digest()).digest()[:4]
    p2sh_address = base58.b58encode(extended_p2sh + checksum_p2sh).decode()

    # SegWit (bc1...)
    hrp = "bc"
    data = convertbits(ripemd160, 8, 5, True)
    segwit_address = bech32_encode(hrp, data)

    return legacy_address, p2sh_address, segwit_address

# === 4. Proces wyszukiwania ===
def search_process(a, b, target_addresses, counter, process_id, lock):
    local_counter = 0
    proc = psutil.Process(os.getpid())
    jump_range = (b - a) // 10
    key_gen = jump_generator(a, b, jump_range)

    while True:
        priv_key = next(key_gen)
        addr_legacy, addr_p2sh, addr_segwit = private_key_to_addresses(priv_key)

        if (addr_legacy in target_addresses or
            addr_p2sh in target_addresses or
            addr_segwit in target_addresses):

            # Pokazujemy tylko adres na konsoli
            print(f"Found Address: {addr_legacy}")
            print(f"Found Address: {addr_p2sh}")
            print(f"Found Address: {addr_segwit}")
            print("-" * 50)

            # Zapisujemy do pliku z HEX kluczem prywatnym i adresami
            with open(OUTPUT_FILE, "a") as f:
                f.write(f"Private Key (HEX): {hex(priv_key)}\n")
                f.write(f"Legacy: {addr_legacy}\nP2SH: {addr_p2sh}\nSegWit: {addr_segwit}\n\n")

        local_counter += 1

        # Synchronizujemy dostęp do licznika
        with lock:
            counter.value += 1  # Zwiększamy licznik globalny

        if local_counter % 100000 == 0:
            print(f"[{process_id}] 🔁 Sprawdzono {counter.value} kluczy... RAM: {proc.memory_info().rss // 1024 ** 2} MB")

# === 5. Niezależny licznik w osobnym wątku ===
def print_counter(counter, lock):
    while True:
        with lock:
            print(f"Total Addresses Checked: {counter.value}", end='\r')
        time.sleep(1)  # Aktualizacja licznika co 1 sekundę

# === 6. Uruchomienie skryptu ===
if __name__ == "__main__":
    raw_addresses = load_addresses()

    print("Podaj zakres do BTC Puzzle (np. 255–256):")
    start_bit = int(input("Od bitu (np. 255): "))
    end_bit = int(input("Do bitu (np. 256): "))
    a = 2 ** start_bit
    b = 2 ** end_bit

    print(f"🔎 Przeszukuję zakres od {a} do {b}...")

    # Menedżer dla wspólnego licznika i zbioru adresów
    manager = multiprocessing.Manager()
    shared_addresses = manager.dict(raw_addresses)
    counter = multiprocessing.Value('i', 0)  # Licznik globalny
    lock = multiprocessing.Lock()  # Blokada do synchronizacji dostępu

    processes = []
    found_addresses = manager.list()  # Zbiór znalezionych adresów (jeśli chcesz zapisać wszystkie)

    # Uruchomienie wątku licznika
    counter_thread = threading.Thread(target=print_counter, args=(counter, lock))
    counter_thread.daemon = True
    counter_thread.start()

    # Uruchomienie procesów
    for i in range(PROCESSES):
        p = multiprocessing.Process(target=search_process, args=(a, b, shared_addresses, counter, i, lock))
        processes.append(p)
        p.start()

    # Czekaj na zakończenie procesów
    for p in processes:
        p.join()

    print(f"Total addresses checked: {counter.value}")
