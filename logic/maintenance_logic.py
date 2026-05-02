from dataclasses import dataclass, field
from datetime import datetime
from database.db_manager import DatabaseManager


@dataclass
class StatusMaintenance:
    jenis: str
    label: str
    km_sejak_terakhir: float
    batas_km: float
    persen: float
    status: str   
    pesan: str


@dataclass
class RingkasanKeuangan:
    bulan: str
    total_bensin: float
    total_maintenance: float
    total: float


class MaintenanceLogic:
    JENIS_MAINTENANCE = [
        ("Ganti Oli Mesin",   "batas_ganti_oli_mesin"),
        ("Ganti Oli Gardan",  "batas_ganti_oli_gardan"),
        ("Ganti Ban",         "batas_ganti_ban"),
        ("Ganti Kampas Rem",  "batas_ganti_kampas_rem"),
    ]

    JENIS_AKTIVITAS = [
        "Perjalanan Harian",
        "Perjalanan Luar Kota",
        "Belanja / Keperluan",
        "Antar Jemput",
        "Touring",
        "Lainnya",
    ]

    KONDISI_MESIN = [
        "Baik",
        "Sedikit Kasar",
        "Kasar",
        "Perlu Dicek",
        "Bermasalah",
    ]

    def __init__(self, db: DatabaseManager):
        self.db = db

    def cek_semua_maintenance(self) -> list[StatusMaintenance]:
        config = self.db.get_konfigurasi()
        hasil = []
        for label, param in self.JENIS_MAINTENANCE:
            batas = config.get(param, 0)
            km_sejak = self.db.get_km_sejak_maintenance_terakhir(label)
            persen = (km_sejak / batas * 100) if batas > 0 else 0

            if persen >= 100:
                status = "lewat"
                pesan = f"MELEWATI BATAS! Segera lakukan {label}."
            elif persen >= 85:
                status = "segera"
                pesan = f"Sisa {batas - km_sejak:.0f} km — segera jadwalkan {label}."
            elif persen >= 60:
                status = "perhatian"
                pesan = f"Sisa {batas - km_sejak:.0f} km — perhatikan {label}."
            else:
                status = "aman"
                pesan = f"Sisa {batas - km_sejak:.0f} km — {label} normal."

            hasil.append(StatusMaintenance(
                jenis=label,
                label=label,
                km_sejak_terakhir=km_sejak,
                batas_km=batas,
                persen=min(persen, 100),
                status=status,
                pesan=pesan,
            ))
        return hasil

    def ada_peringatan(self) -> bool:
        return any(
            s.status in ("segera", "lewat")
            for s in self.cek_semua_maintenance()
        )

    def get_ringkasan_keuangan(self, bulan: str = None) -> dict:
        if bulan is None:
            bulan = datetime.now().strftime("%Y-%m")
        bensin = self.db.get_total_pengeluaran_bensin(bulan)
        maint = self.db.get_total_pengeluaran_maintenance(bulan)
        return {
            "bulan": bulan,
            "bensin": bensin,
            "maintenance": maint,
            "total": bensin + maint,
        }

    def get_ringkasan_bulanan_list(self) -> list[RingkasanKeuangan]:
        rows = self.db.get_pengeluaran_per_bulan()
        return [
            RingkasanKeuangan(
                bulan=r["bulan"],
                total_bensin=r["bensin"] or 0,
                total_maintenance=r["maint"] or 0,
                total=(r["bensin"] or 0) + (r["maint"] or 0),
            )
            for r in rows
        ]

    def format_rupiah(self, nilai: float) -> str:
        return f"Rp {nilai:,.0f}".replace(",", ".")

    def format_km(self, nilai: float) -> str:
        return f"{nilai:,.1f} km".replace(",", ".")

