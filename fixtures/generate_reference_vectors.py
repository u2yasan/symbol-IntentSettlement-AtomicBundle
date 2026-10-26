#!/usr/bin/env python3
"""Reference bytes for the DESIGN, not a Catapult implementation or a live CLI.

The private seeds below are intentionally public, disposable test material.
No network requests, announcements, accounts, or real funds are used.
Requires Python 3.10+ and cryptography. Run --check to verify checked-in JSON.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import struct
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HERE = Path(__file__).resolve().parent
INTENT_DOMAIN = b"SYMBOL_INTENT_ORDER_V1"
BUNDLE_DOMAIN = b"SYMBOL_ATOMIC_BUNDLE_ACTIONS_V1"
NETWORK = 0x98  # Test-format address only; synthetic genesis seed below.
GENERATION_SEED = bytes.fromhex("11" * 32)


def sha3(data: bytes) -> bytes:
    return hashlib.sha3_256(data).digest()


def public_bytes(key: Ed25519PrivateKey) -> bytes:
    return key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )


def symbol_address(public_key: bytes, network: int) -> bytes:
    ripemd = hashlib.new("ripemd160", sha3(public_key)).digest()
    prefix = bytes([network]) + ripemd
    return prefix + sha3(prefix)[:3]


def encode_order(public_key: bytes, nonce: bytes, give: int, get: int) -> bytes:
    assert len(public_key) == 32 and len(nonce) == 32
    address = symbol_address(public_key, NETWORK)
    data = (
        struct.pack("<BBHI", 1, NETWORK, 0, 0)
        + public_key
        + address
        + struct.pack(
            "<QQQQQ", 0x0123456789ABCDEF, give,
            0x023456789ABCDEF0, get, 7_200_000,
        )
        + nonce
    )
    assert len(data) == 136
    return data


def intent_vectors() -> dict:
    seed = bytes(range(32))
    key = Ed25519PrivateKey.from_private_bytes(seed)
    pub = public_bytes(key)
    nonce = bytes(range(32, 64))
    vectors = []
    for name, give, get in [
        ("basic_exact_exchange", 50, 1_000_000_000),
        ("u64_precision_encoding_only", (1 << 53) + 1, (1 << 64) - 1),
    ]:
        order = encode_order(pub, nonce, give, get)
        message = sha3(INTENT_DOMAIN) + GENERATION_SEED + order
        signature = key.sign(message)
        assert len(message) == 200 and len(signature) == 64
        key.public_key().verify(signature, message)
        tampered = bytearray(message)
        tampered[64 + 72] ^= 1
        try:
            key.public_key().verify(signature, bytes(tampered))
        except InvalidSignature:
            pass
        else:
            raise AssertionError("tampered amount unexpectedly verifies")
        vectors.append({
            "name": name,
            "fields": {
                "version": 1, "network": NETWORK, "flags": 0,
                "maker_public_key_hex": pub.hex(),
                "recipient_address_hex": symbol_address(pub, NETWORK).hex(),
                "recipient_address_base32": base64.b32encode(
                    symbol_address(pub, NETWORK)
                ).decode().rstrip("="),
                "give_mosaic_id_hex": "0123456789abcdef",
                "give_amount_decimal": str(give),
                "get_mosaic_id_hex": "023456789abcdef0",
                "get_amount_decimal": str(get),
                "valid_until_network_milliseconds_decimal": "7200000",
                "nonce_hex": nonce.hex(),
            },
            "canonical_order_bytes": len(order),
            "canonical_order_hex": order.hex(),
            "signing_message_bytes": len(message),
            "signing_message_hex": message.hex(),
            "order_id_sha3_256_hex": sha3(message).hex(),
            "maker_signature_ed25519_hex": signature.hex(),
            "cryptography_signature_check": "PASS",
            "native_catapult_cross_check": "NOT_RUN",
            "on_chain_acceptance": "NOT_RUN",
        })
    return {
        "schema": "symbol-intent-order-v1-design-fixtures",
        "purpose": "canonical_encoding_and_detached_signature_only",
        "warning": "PUBLIC DISPOSABLE TEST KEY; NOT A LIVE NETWORK FIXTURE",
        "public_test_private_seed_hex": seed.hex(),
        "network_generation_hash_seed_hex": GENERATION_SEED.hex(),
        "domain_utf8": INTENT_DOMAIN.decode(),
        "domain_hash_sha3_256_hex": sha3(INTENT_DOMAIN).hex(),
        "signature_mode": "Ed25519 over full 200 bytes; no prehash; no extra seed prepend",
        "vectors": vectors,
    }


def encode_frame(kind: int, index: int, payload: bytes) -> bytes:
    header = struct.pack("<HHHHII", kind, 1, 0, 0, index, len(payload))
    unpadded = header + payload
    frame = unpadded + bytes((-len(unpadded)) % 8)
    assert len(header) == 16 and len(frame) % 8 == 0
    return frame


def bundle_vector() -> dict:
    # Deliberately NOT valid EmbeddedTransfer or Aggregate bytes.
    # This fixture isolates framing, padding, ordering, and root calculation.
    payloads = [bytes.fromhex("0102030405"), bytes(range(32)), b"return/only/in/bundle"]
    frames = [encode_frame(i + 1, i, p) for i, p in enumerate(payloads)]
    stream = b"".join(frames)
    root_input = BUNDLE_DOMAIN + struct.pack("<II", 3, len(stream)) + stream
    root = sha3(root_input)
    reversed_stream = b"".join(
        encode_frame(i + 1, i, p) for i, p in enumerate(reversed(payloads))
    )
    reverse_root = sha3(
        BUNDLE_DOMAIN + struct.pack("<II", 3, len(reversed_stream)) + reversed_stream
    )
    assert root != reverse_root
    return {
        "schema": "symbol-atomic-action-root-v1-design-fixture",
        "purpose": "framing_and_hash_only_not_valid_transaction",
        "warning": "OPAQUE PAYLOADS: DO NOT ANNOUNCE; NO SOLVER OR P SIGNATURE IS PRESENT",
        "domain_ascii": BUNDLE_DOMAIN.decode(),
        "action_count": 3,
        "actions_size_bytes": len(stream),
        "actions": [{
            "kind": i + 1, "version": 1, "flags": 0, "reserved": 0,
            "index": i, "payload_length": len(p), "payload_hex": p.hex(),
            "frame_size_bytes": len(frames[i]), "frame_hex": frames[i].hex(),
        } for i, p in enumerate(payloads)],
        "action_stream_hex": stream.hex(),
        "root_preimage_hex": root_input.hex(),
        "actions_root_sha3_256_hex": root.hex(),
        "reordered_payload_root_sha3_256_hex": reverse_root.hex(),
        "native_catapult_cross_check": "NOT_RUN",
        "on_chain_acceptance": "NOT_RUN",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = {
        "intent-order-v1.json": intent_vectors(),
        "atomic-action-root-v1.json": bundle_vector(),
    }
    for name, data in outputs.items():
        encoded = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != encoded:
                raise SystemExit(f"MISMATCH: {name}")
            print(f"PASS: {name}")
        else:
            path.write_text(encoded, encoding="utf-8")
            print(f"WROTE: {name}")


if __name__ == "__main__":
    main()
