"""
🔗 BLOCKCHAIN SECURITY SYSTEM FOR MEDICAL RECORDS
==================================================
Immutable, tamper-proof blockchain for prescription storage
Author: Enhanced Medical System
Version: 2.0
"""

import hashlib
import json
import time
import os
from datetime import datetime

# File paths
BLOCKCHAIN_FILE = "blockchain_data.json"
BACKUP_FILE = "blockchain_backup.json"
LOG_FILE = "blockchain_log.txt"

# ========== BLOCKCHAIN CORE FUNCTIONS ==========

def load_chain():
    """
    Load blockchain from file
    Creates new chain if file doesn't exist
    """
    if not os.path.exists(BLOCKCHAIN_FILE):
        print("📝 Creating new blockchain...")
        return []
    try:
        with open(BLOCKCHAIN_FILE, "r") as f:
            chain = json.load(f)
        print(f"✅ Loaded blockchain with {len(chain)} blocks")
        return chain
    except Exception as e:
        print(f"❌ Error loading blockchain: {e}")
        return []

def save_chain(chain):
    """
    Save blockchain to file with automatic backup
    """
    try:
        # Create backup of existing blockchain
        if os.path.exists(BLOCKCHAIN_FILE):
            with open(BLOCKCHAIN_FILE, "r") as f:
                old_data = f.read()
            with open(BACKUP_FILE, "w") as f:
                f.write(old_data)
            print("💾 Backup created")
        
        # Save new chain
        with open(BLOCKCHAIN_FILE, "w") as f:
            json.dump(chain, f, indent=4)
        
        print(f"✅ Blockchain saved: {len(chain)} blocks")
        
        # Log the save operation
        log_operation(f"Blockchain saved with {len(chain)} blocks")
        
        return True
    except Exception as e:
        print(f"❌ Error saving blockchain: {e}")
        return False

def create_hash(data):
    """
    Create SHA-256 hash from data
    Most secure cryptographic hash function
    """
    return hashlib.sha256(data.encode()).hexdigest()

def create_genesis_block():
    """
    Create the first block (Genesis Block) of the blockchain
    """
    timestamp = time.time()
    genesis_block = {
        "index": 0,
        "patient_id": "GENESIS",
        "doctor_id": "SYSTEM",
        "treatment": "Blockchain initialized",
        "timestamp": timestamp,
        "time_readable": time.ctime(timestamp),
        "previous_hash": "0" * 64,
        "hash": create_hash(f"0|GENESIS|SYSTEM|init|{'0'*64}|{timestamp}"),
        "is_valid": True,
        "block_type": "GENESIS"
    }
    return genesis_block

# ========== RECORD MANAGEMENT ==========

def add_record(patient_id, doctor_id, treatment):
    """
    🔒 Add new medical record to blockchain
    
    Each block contains:
    - Index (block number)
    - Patient ID
    - Doctor ID
    - Treatment details
    - Timestamp
    - Previous block hash
    - Current block hash
    
    Returns: record hash (unique identifier)
    """
    print(f"\n{'='*60}")
    print(f"🔗 Adding new block to blockchain")
    print(f"{'='*60}")
    
    chain = load_chain()
    
    # Create genesis block if this is first record
    if len(chain) == 0:
        genesis = create_genesis_block()
        chain.append(genesis)
        print("✨ Genesis block created")
    
    # Get previous hash
    previous_hash = chain[-1]["hash"]
    timestamp = time.time()
    block_index = len(chain)
    
    # Create comprehensive data string for hashing
    data = f"{block_index}|{patient_id}|{doctor_id}|{treatment}|{previous_hash}|{timestamp}"
    record_hash = create_hash(data)
    
    # Create new block
    block = {
        "index": block_index,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "treatment": treatment,
        "timestamp": timestamp,
        "time_readable": time.ctime(timestamp),
        "date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        "previous_hash": previous_hash,
        "hash": record_hash,
        "is_valid": True,
        "block_type": "MEDICAL_RECORD"
    }
    
    # Add to chain
    chain.append(block)
    
    # Save
    if save_chain(chain):
        print(f"✅ Block #{block_index} added successfully")
        print(f"🔑 Hash: {record_hash[:16]}...")
        print(f"👤 Patient: {patient_id}")
        print(f"👨‍⚕️ Doctor: {doctor_id}")
        print(f"{'='*60}\n")
        
        # Log operation
        log_operation(f"Block added - Index: {block_index}, Patient: {patient_id}, Doctor: {doctor_id}")
    else:
        print("❌ Failed to save block")
    
    return record_hash

# ========== VERIFICATION FUNCTIONS ==========

def verify_chain():
    """
    🔐 Verify entire blockchain integrity
    
    Checks:
    1. Genesis block validity
    2. Hash chain linkage
    3. Individual block hash correctness
    
    Returns: True if valid, False if tampered
    """
    print(f"\n{'='*60}")
    print(f"🔍 Verifying Blockchain Integrity")
    print(f"{'='*60}")
    
    chain = load_chain()
    
    if not chain:
        print("✅ Empty blockchain is valid")
        return True
    
    # Check genesis block
    if chain[0]["previous_hash"] != "0" * 64:
        print("❌ Genesis block invalid!")
        return False
    
    print(f"📊 Total blocks: {len(chain)}")
    
    # Verify each block
    for i in range(1, len(chain)):
        current_block = chain[i]
        previous_block = chain[i-1]
        
        print(f"Checking block #{i}...", end=" ")
        
        # Check if previous hash matches
        if current_block["previous_hash"] != previous_block["hash"]:
            print(f"❌ FAILED")
            print(f"   Previous hash mismatch at block {i}")
            print(f"   Expected: {previous_block['hash'][:16]}...")
            print(f"   Got: {current_block['previous_hash'][:16]}...")
            return False
        
        # Verify hash calculation
        data = f"{current_block['index']}|{current_block['patient_id']}|{current_block['doctor_id']}|{current_block['treatment']}|{current_block['previous_hash']}|{current_block['timestamp']}"
        recalculated_hash = create_hash(data)
        
        if recalculated_hash != current_block["hash"]:
            print(f"❌ FAILED")
            print(f"   Hash mismatch at block {i}")
            print(f"   Expected: {current_block['hash'][:16]}...")
            print(f"   Calculated: {recalculated_hash[:16]}...")
            return False
        
        print(f"✅")
    
    print(f"{'='*60}")
    print(f"✅ Blockchain is VALID and SECURE")
    print(f"🔒 All {len(chain)} blocks verified")
    print(f"{'='*60}\n")
    
    log_operation(f"Blockchain verified - {len(chain)} blocks OK")
    return True

def detect_tampering():
    """
    🚨 Detect any tampering attempts in blockchain
    Returns list of tampered blocks with details
    """
    chain = load_chain()
    tampered_blocks = []
    
    for i in range(1, len(chain)):
        current_block = chain[i]
        previous_block = chain[i-1]
        
        # Verify hash
        data = f"{current_block['index']}|{current_block['patient_id']}|{current_block['doctor_id']}|{current_block['treatment']}|{current_block['previous_hash']}|{current_block['timestamp']}"
        recalculated_hash = create_hash(data)
        
        if recalculated_hash != current_block["hash"]:
            tampered_blocks.append({
                "block_index": i,
                "reason": "Hash mismatch",
                "expected": recalculated_hash,
                "actual": current_block["hash"]
            })
        
        if current_block["previous_hash"] != previous_block["hash"]:
            tampered_blocks.append({
                "block_index": i,
                "reason": "Previous hash mismatch",
                "expected": previous_block["hash"],
                "actual": current_block["previous_hash"]
            })
    
    return tampered_blocks

# ========== QUERY FUNCTIONS ==========

def get_record_by_hash(record_hash):
    """
    📋 Retrieve specific record from blockchain by hash
    """
    chain = load_chain()
    for block in chain:
        if block["hash"] == record_hash:
            return block
    return None

def get_patient_records(patient_id):
    """
    👤 Get all records for a specific patient
    """
    chain = load_chain()
    records = [block for block in chain if block.get("patient_id") == patient_id]
    print(f"📋 Found {len(records)} records for patient {patient_id}")
    return records

def get_doctor_records(doctor_id):
    """
    👨‍⚕️ Get all records created by a doctor
    """
    chain = load_chain()
    records = [block for block in chain if block.get("doctor_id") == doctor_id]
    print(f"📋 Found {len(records)} records by doctor {doctor_id}")
    return records

def get_recent_records(count=10):
    """
    📅 Get most recent records
    """
    chain = load_chain()
    return chain[-count:] if len(chain) >= count else chain

# ========== STATISTICS & ANALYTICS ==========

def get_chain_stats():
    """
    📊 Get comprehensive blockchain statistics
    """
    chain = load_chain()
    
    if not chain:
        return {
            "total_blocks": 0,
            "is_valid": True,
            "first_block": None,
            "last_block": None,
            "total_patients": 0,
            "total_doctors": 0,
            "genesis_block": None
        }
    
    # Collect unique IDs
    patients = set()
    doctors = set()
    
    for block in chain:
        if block.get("block_type") != "GENESIS":
            patients.add(block.get("patient_id"))
            doctors.add(block.get("doctor_id"))
    
    stats = {
        "total_blocks": len(chain),
        "is_valid": verify_chain(),
        "first_block": chain[0].get("time_readable") if chain else None,
        "last_block": chain[-1].get("time_readable") if chain else None,
        "total_patients": len(patients),
        "total_doctors": len(doctors),
        "genesis_block": chain[0] if chain else None,
        "chain_size_kb": os.path.getsize(BLOCKCHAIN_FILE) / 1024 if os.path.exists(BLOCKCHAIN_FILE) else 0
    }
    
    return stats

def print_chain_stats():
    """
    📊 Print detailed blockchain statistics
    """
    stats = get_chain_stats()
    
    print(f"\n{'='*60}")
    print(f"📊 BLOCKCHAIN STATISTICS")
    print(f"{'='*60}")
    print(f"Total Blocks: {stats['total_blocks']}")
    print(f"Validity: {'✅ VALID' if stats['is_valid'] else '❌ INVALID'}")
    print(f"Total Patients: {stats['total_patients']}")
    print(f"Total Doctors: {stats['total_doctors']}")
    print(f"First Block: {stats['first_block']}")
    print(f"Last Block: {stats['last_block']}")
    print(f"Chain Size: {stats['chain_size_kb']:.2f} KB")
    print(f"{'='*60}\n")

# ========== BACKUP & RECOVERY ==========

def export_chain(filepath):
    """
    💾 Export blockchain to a file
    """
    chain = load_chain()
    try:
        with open(filepath, "w") as f:
            json.dump(chain, f, indent=4)
        print(f"✅ Blockchain exported to {filepath}")
        return True
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False

def rollback_to_backup():
    """
    ⏮️ Restore blockchain from backup
    """
    if not os.path.exists(BACKUP_FILE):
        print("❌ No backup file found")
        return False
    
    try:
        with open(BACKUP_FILE, "r") as f:
            backup_data = f.read()
        
        with open(BLOCKCHAIN_FILE, "w") as f:
            f.write(backup_data)
        
        print("✅ Blockchain restored from backup")
        log_operation("Blockchain restored from backup")
        return True
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        return False

# ========== LOGGING ==========

def log_operation(message):
    """
    📝 Log blockchain operations
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
    except:
        pass  # Silent fail for logging

# ========== TESTING & DEMO ==========

if __name__ == "__main__":
    print("🔗 Blockchain Medical Records System")
    print("=" * 60)
    
    # Demo
    print("\n📋 DEMO: Adding sample records...")
    
    # Add some test records
    hash1 = add_record("P001", "D001", "Fever|Paracetamol")
    hash2 = add_record("P002", "D001", "Cold|Amoxicillin")
    hash3 = add_record("P001", "D002", "Diabetes|Metformin")
    
    # Verify
    verify_chain()
    
    # Show stats
    print_chain_stats()
    
    print("\n✅ Blockchain system ready!")
    print("=" * 60)