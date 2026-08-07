import sqlite3
import os

DB_PATH = "lab_inventory.db"

def init_db():
    # Connect to SQLite database (will be created if it does not exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop tables if they exist to allow clean re-initialization
    cursor.execute("DROP TABLE IF EXISTS inventory")
    cursor.execute("DROP TABLE IF EXISTS synthesis_procedures")

    # Create inventory table
    cursor.execute("""
    CREATE TABLE inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compound_name TEXT NOT NULL,
        formula TEXT NOT NULL,
        cas_number TEXT NOT NULL,
        quantity_g REAL NOT NULL,
        purity REAL NOT NULL,
        location TEXT NOT NULL,
        hazard_ghs TEXT NOT NULL
    )
    """)

    # Create synthesis_procedures table
    cursor.execute("""
    CREATE TABLE synthesis_procedures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_compound TEXT NOT NULL,
        reagents_required TEXT NOT NULL,
        procedure_steps TEXT NOT NULL,
        safety_precautions TEXT NOT NULL
    )
    """)

    # Seed data for inventory
    inventory_data = [
        ("Salicylic acid", "C7H6O3", "69-72-7", 500.0, 99.0, "Cabinet A, Shelf 2", "H302 (Harmful if swallowed), H318 (Causes serious eye damage)"),
        ("Acetic anhydride", "C4H6O3", "108-24-7", 1000.0, 98.0, "Flammables Cabinet, Shelf 1", "H226 (Flammable liquid), H302 (Harmful if swallowed), H314 (Causes severe skin burns), H330 (Fatal if inhaled)"),
        ("p-Aminophenol", "C6H7NO", "123-30-8", 250.0, 98.0, "Cabinet B, Shelf 3", "H302+H332 (Harmful if swallowed or inhaled), H341 (Suspected of causing genetic defects), H410 (Very toxic to aquatic life)"),
        ("Aspirin", "C9H8O4", "50-78-2", 100.0, 99.5, "Storage Room 1, Shelf A", "H302 (Harmful if swallowed), H315 (Causes skin irritation), H319 (Causes serious eye irritation)"),
        ("Acetaminophen", "C8H9NO2", "103-90-2", 150.0, 99.0, "Storage Room 1, Shelf B", "H302 (Harmful if swallowed), H315 (Causes skin irritation), H317 (May cause allergic skin reaction)")
    ]

    cursor.executemany("""
    INSERT INTO inventory (compound_name, formula, cas_number, quantity_g, purity, location, hazard_ghs)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, inventory_data)

    # Seed data for synthesis_procedures
    synthesis_data = [
        (
            "Aspirin",
            "Salicylic acid, Acetic anhydride, Phosphoric acid (85%), Distilled water, Ice",
            "1. Weigh 2.0 g of salicylic acid and place in an Erlenmeyer flask.\n"
            "2. Add 5.0 mL of acetic anhydride and 5 drops of 85% phosphoric acid.\n"
            "3. Heat the mixture in a warm water bath (75-80°C) for 10-15 minutes with occasional swirling.\n"
            "4. Carefully add 2 mL of distilled water to decompose excess acetic anhydride.\n"
            "5. Remove from water bath, add 40 mL of ice-cold water, and chill in an ice bath to precipitate product.\n"
            "6. Collect acetylsalicylic acid crystals using Buchner funnel suction filtration and wash with cold water.\n"
            "7. Recrystallize from ethanol/water and dry.",
            "Work in a fume hood. Acetic anhydride is a strong irritant and lachrymator. Handle concentrated phosphoric acid with care. Wear nitrile gloves, safety goggles, and lab coat."
        ),
        (
            "Acetaminophen",
            "p-Aminophenol, Acetic anhydride, Distilled water, Ice",
            "1. Weigh 1.5 g of p-aminophenol and suspend in 5.0 mL of distilled water in an Erlenmeyer flask.\n"
            "2. Warm gently while stirring until dissolved/suspended.\n"
            "3. Slowly add 2.0 mL of acetic anhydride while swirling.\n"
            "4. Heat in a boiling water bath for 10 minutes until reaction is complete.\n"
            "5. Cool flask in an ice bath to induce crystallization of acetaminophen.\n"
            "6. Collect crude crystals by vacuum filtration using a Buchner funnel and wash with ice-cold water.\n"
            "7. Recrystallize from hot water and dry.",
            "Work in a fume hood. p-Aminophenol is toxic and absorbed through skin. Acetic anhydride fumes are hazardous. Wear eye protection, gloves, and lab coat at all times."
        )
    ]

    cursor.executemany("""
    INSERT INTO synthesis_procedures (target_compound, reagents_required, procedure_steps, safety_precautions)
    VALUES (?, ?, ?, ?)
    """, synthesis_data)

    conn.commit()
    conn.close()
    print(f"Successfully initialized {DB_PATH} with inventory and synthesis_procedures tables and seed data.")

if __name__ == "__main__":
    init_db()
