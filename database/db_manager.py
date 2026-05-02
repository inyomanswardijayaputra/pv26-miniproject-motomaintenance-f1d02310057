import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='data_motomaintenance.db'):
        self.db_name = db_name
        self.initialize()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aktivitas (
                    id_aktivitas INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT NOT NULL,
                    jenis_aktivitas TEXT NOT NULL,
                    jarak_tempuh REAL DEFAULT 0,
                    liter_bensin REAL DEFAULT 0,
                    harga_bensin REAL DEFAULT 0,
                    kondisi_mesin TEXT DEFAULT 'Baik',
                    catatan TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maintenance (
                    id_maintenance INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT NOT NULL,
                    jenis_maintenance TEXT NOT NULL,
                    km_saat_itu REAL DEFAULT 0,
                    biaya REAL DEFAULT 0,
                    bengkel TEXT DEFAULT '',
                    catatan TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS konfigurasi (
                    id_konfigurasi INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama_parameter TEXT UNIQUE NOT NULL,
                    nilai REAL NOT NULL,
                    satuan TEXT DEFAULT 'km'
                )
            """)

            defaults = [
                ("batas_ganti_oli_mesin", 3000, "km"),
                ("batas_ganti_oli_gardan", 8000, "km"),
                ("batas_ganti_ban", 20000, "km"),
                ("batas_ganti_kampas_rem", 10000, "km"),
            ]
            for nama, nilai, satuan in defaults:
                cursor.execute("""
                    INSERT OR IGNORE INTO konfigurasi (nama_parameter, nilai, satuan)
                    VALUES (?, ?, ?)
                """, (nama, nilai, satuan))

            conn.commit()

    def tambah_aktivitas(self, data: dict) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO aktivitas
                    (tanggal, jenis_aktivitas, jarak_tempuh, liter_bensin,
                     harga_bensin, kondisi_mesin, catatan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data["tanggal"], data["jenis_aktivitas"], data["jarak_tempuh"],
                data["liter_bensin"], data["harga_bensin"], data["kondisi_mesin"],
                data["catatan"]
            ))
            conn.commit()
            return cursor.lastrowid

    def get_semua_aktivitas(self) -> list:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM aktivitas ORDER BY tanggal DESC, created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_aktivitas_by_id(self, id_aktivitas: int) -> dict | None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM aktivitas WHERE id_aktivitas = ?", (id_aktivitas,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_aktivitas(self, id_aktivitas: int, data: dict):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE aktivitas SET
                    tanggal=?, jenis_aktivitas=?, jarak_tempuh=?,
                    liter_bensin=?, harga_bensin=?, kondisi_mesin=?, catatan=?
                WHERE id_aktivitas=?
            """, (
                data["tanggal"], data["jenis_aktivitas"], data["jarak_tempuh"],
                data["liter_bensin"], data["harga_bensin"], data["kondisi_mesin"],
                data["catatan"], id_aktivitas
            ))
            conn.commit()

    def hapus_aktivitas(self, id_aktivitas: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM aktivitas WHERE id_aktivitas = ?", (id_aktivitas,))
            conn.commit()

    def tambah_maintenance(self, data: dict) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO maintenance
                    (tanggal, jenis_maintenance, km_saat_itu, biaya,
                     bengkel, catatan)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data["tanggal"], data["jenis_maintenance"], data["km_saat_itu"],
                data["biaya"], data["bengkel"], data["catatan"]
            ))
            conn.commit()
            return cursor.lastrowid

    def get_semua_maintenance(self) -> list:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM maintenance ORDER BY tanggal DESC, created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_maintenance_by_id(self, id_maintenance: int) -> dict | None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM maintenance WHERE id_maintenance = ?", (id_maintenance,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_maintenance(self, id_maintenance: int, data: dict):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE maintenance SET
                    tanggal=?, jenis_maintenance=?, km_saat_itu=?,
                    biaya=?, bengkel=?, catatan=?
                WHERE id_maintenance=?
            """, (
                data["tanggal"], data["jenis_maintenance"], data["km_saat_itu"],
                data["biaya"], data["bengkel"], data["catatan"], id_maintenance
            ))
            conn.commit()

    def hapus_maintenance(self, id_maintenance: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM maintenance WHERE id_maintenance = ?", (id_maintenance,))
            conn.commit()

    def get_total_km(self) -> float:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    MAX(jarak_tempuh) - MIN(jarak_tempuh) 
                FROM aktivitas 
                WHERE jarak_tempuh > 0
            """)
            result = cursor.fetchone()[0]
            return result if result is not None else 0.0

    def get_total_pengeluaran_bensin(self, bulan: str = None) -> float:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if bulan:
                cursor.execute("""
                    SELECT COALESCE(SUM(harga_bensin), 0) FROM aktivitas
                    WHERE strftime('%Y-%m', tanggal) = ?
                """, (bulan,))
            else:
                cursor.execute("SELECT COALESCE(SUM(harga_bensin), 0) FROM aktivitas")
            return cursor.fetchone()[0]

    def get_total_pengeluaran_maintenance(self, bulan: str = None) -> float:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if bulan:
                cursor.execute("""
                    SELECT COALESCE(SUM(biaya), 0) FROM maintenance
                    WHERE strftime('%Y-%m', tanggal) = ?
                """, (bulan,))
            else:
                cursor.execute("SELECT COALESCE(SUM(biaya), 0) FROM maintenance")
            return cursor.fetchone()[0]

    def get_km_sejak_maintenance_terakhir(self, jenis: str) -> float:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT km_saat_itu FROM maintenance
                WHERE jenis_maintenance = ?
                ORDER BY tanggal DESC, id_maintenance DESC LIMIT 1
            """, (jenis,))
            row = cursor.fetchone()

            if row:
                odo_maintenance_terakhir = row[0]
                
                odo_sekarang = self.get_odometer()
                
                return max(0.0, odo_sekarang - odo_maintenance_terakhir)
            else:
                total_km = self.get_total_km()
                return float(total_km)

    def get_konfigurasi(self) -> dict:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nama_parameter, nilai FROM konfigurasi")
            return {row[0]: row[1] for row in cursor.fetchall()}

    def get_pengeluaran_per_bulan(self) -> list:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bulan, SUM(bensin) as bensin, SUM(maint) as maint
                FROM (
                    SELECT strftime('%Y-%m', tanggal) as bulan,
                           SUM(harga_bensin) as bensin, 0 as maint
                    FROM aktivitas GROUP BY bulan
                    UNION ALL
                    SELECT strftime('%Y-%m', tanggal) as bulan,
                           0 as bensin, SUM(biaya) as maint
                    FROM maintenance GROUP BY bulan
                )
                GROUP BY bulan ORDER BY bulan DESC LIMIT 12
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_odometer(self) -> float:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(jarak_tempuh) FROM aktivitas")
            return cursor.fetchone()[0]