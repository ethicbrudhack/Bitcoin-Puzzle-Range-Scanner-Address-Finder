# 🧩 Bitcoin Puzzle Range Scanner & Address Finder

> ⚠️ **For Educational and Ethical Research Use Only**  
> This tool demonstrates **parallelized brute-force exploration** of Bitcoin key ranges (e.g., BTC Puzzle segments)  
> and **address generation verification** against a known address list.  
>  
> Use only in **controlled**, **authorized**, and **ethical** environments —  
> for example, analyzing cryptographic keyspaces or studying Bitcoin address generation.

---

## 🚀 Overview

This script generates random **private keys within a user-specified bit range**,  
derives corresponding **Bitcoin addresses** (Legacy, P2SH, and SegWit),  
and checks them against a list of known addresses (`adresy.txt`).

It uses:
- ⚙️ **Multiprocessing** for parallel scanning  
- 🧠 **Non-linear key jumps** for entropy variation  
- 🔎 **Address conversion and checksum validation**  
- 📊 **Real-time progress counter and memory usage stats**

---

## ✨ Features

| Feature | Description |
|----------|--------------|
| 💥 **BTC Puzzle compatible** | Works with any numeric bit range (e.g. 255–256) |
| 🔁 **Jump generator** | Random step increments across search range for non-linear traversal |
| 🧩 **Address derivation** | Generates Legacy (1...), P2SH (3...), and SegWit (bc1...) |
| ⚙️ **Parallel multiprocessing** | Multiple processes scanning simultaneously |
| 📈 **Real-time progress** | Live total counter & per-process logs |
| 💾 **Result logging** | Saves all found keys and addresses to `znalezioneBTC.txt` |
| 🧱 **CPU usage info** | Prints memory consumption for each worker |

---

## 📂 File Structure

| File | Description |
|------|-------------|
| `main.py` | Main scanner script |
| `adresy.txt` | File containing known Bitcoin addresses (one per line) |
| `znalezioneBTC.txt` | Output log for found results |
| `README.md` | Project documentation (this file) |

---

## ⚙️ Configuration

| Variable | Purpose |
|-----------|----------|
| `ADDRESS_FILE` | Path to address list file |
| `OUTPUT_FILE` | File where matches will be saved |
| `PROCESSES` | Number of parallel processes (default: 2) |
| `SHOW_GENERATED` | Option to print generated addresses (for debugging) |

**Dependencies**

pip install ecdsa base58 bech32 psutil


---

## 🧠 How It Works

### 1️⃣ Load Known Addresses  
Reads the `adresy.txt` file and loads all Bitcoin addresses into a shared dictionary for O(1) lookup.

```python
with open("adresy.txt") as f:
    addresses = {line.strip(): True for line in f if line[0] in ("1", "3", "b")}

2️⃣ Jump Generator

Generates pseudo-random private keys with irregular increments:

offset = random.randint(jump_range // 2, jump_range + jump_range // 2)
position = (position + offset) % (stop - start) + start


This avoids linear scanning and introduces entropy to the search.

3️⃣ Address Derivation

For each private key:

Creates an ECDSA public key

Computes:

Legacy address (prefix 1...)

P2SH address (prefix 3...)

SegWit address (prefix bc1...)

sk = ecdsa.SigningKey.from_secret_exponent(priv_key, curve=ecdsa.SECP256k1)
vk = sk.verifying_key
pubkey_bytes = b'\x04' + vk.to_string()


Checksum and encoding are done using SHA256, RIPEMD160, Base58, and Bech32 standards.

4️⃣ Parallel Search Process

Each worker scans independently in its assigned numeric range.
When an address match is found:

It prints the hit on-screen

Saves the private key and addresses to the output file

with open(OUTPUT_FILE, "a") as f:
    f.write(f"Private Key (HEX): {hex(priv_key)}\n")
    f.write(f"Legacy: {addr_legacy}\nP2SH: {addr_p2sh}\nSegWit: {addr_segwit}\n\n")

5️⃣ Real-Time Statistics

A background thread displays the total number of tested keys every second:

Total Addresses Checked: 1258042


Each process also reports every 100,000 keys with memory usage info.

🧾 Example Run
Wczytano 750000 adresów.
Podaj zakres do BTC Puzzle (np. 255–256):
Od bitu (np. 255): 255
Do bitu (np. 256): 256
🔎 Przeszukuję zakres od 57896044618658097711785492504343953926634992332820282019728792003956564819968 do 115792089237316195423570985008687907853269984665640564039457584007913129639936...
[0] 🔁 Sprawdzono 100000 kluczy... RAM: 142 MB
[1] 🔁 Sprawdzono 100000 kluczy... RAM: 138 MB
Total Addresses Checked: 245831

🧩 Core Components
Function	Description
load_addresses()	Loads Bitcoin addresses from file
jump_generator()	Produces pseudo-random private key jumps
private_key_to_addresses()	Derives Legacy, P2SH, and SegWit addresses
search_process()	Worker loop scanning for hits
print_counter()	Background thread showing total progress
⚡ Performance Tips

Increase PROCESSES to utilize all CPU cores.

Use smaller ranges for faster testing and debugging.

Store addresses in a SQLite or memory-mapped set for better lookup performance.

Disable SHOW_GENERATED for maximum speed.

Use SSD for faster logging and I/O.

🔒 Ethical & Legal Notice

This program is a research tool to study key distribution, randomness, and Bitcoin address generation.
It must not be used to search for or exploit private keys belonging to others.

You can:

Analyze cryptographic randomness.

Study Bitcoin address structure.

Learn multiprocessing and key generation concepts.

You must not:

Attempt unauthorized wallet recovery.

Use it against real user funds or external wallets.

Unauthorized scanning or brute-force of private keys is illegal and unethical.

🧰 Suggested Improvements

🧮 Add CLI interface for dynamic parameter input (argparse)

💾 Write results with timestamps and process IDs

⚙️ Use multiprocessing pools for better task balancing

🧱 Implement checkpoint save/resume between runs

🔧 Add performance profiling and auto-range scaling

🪪 License

MIT License
© 2025 — Author: [Ethicbrudhack]

💡 Summary

This project combines:

🔐 Bitcoin address generation

⚙️ Multiprocessing with shared memory

🧠 Jump-based private key exploration

📊 Real-time monitoring

to demonstrate keyspace traversal and HD address creation mechanics — safely and responsibly.

🧠 Understand cryptography. Respect its power. Use knowledge ethically.

BTC donation address: bc1q4nyq7kr4nwq6zw35pg0zl0k9jmdmtmadlfvqhr
