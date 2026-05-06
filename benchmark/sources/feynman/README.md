# Feynman Challenge Ciphers

This source contains Feynman Challenge Ciphers #2 and #3 as solved-probable Track-B benchmark records based on codewarrior0's 2023 claimed solutions. They were previously staged as disputed unsolved records; they were promoted because the claimed plaintexts, partial alphabets, word-level alternation, and word-reversal rule re-encipher to the ciphertext with only tiny documented exception/mapping residue.

The claimed solution method uses two monoalphabetic substitutions, alternating by word, with even-length words reversed. The first word of each sentence or poetry line starts with alphabet 1. Alphabet/key parameters are stored in `known_cipher_parameters` and must not be exposed in blind/standard context.
