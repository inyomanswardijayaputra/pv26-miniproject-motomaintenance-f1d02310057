"""
ui/dialog_maintenance.py
Dialog form tambah/edit riwayat maintenance motor
Separation of Concerns: UI Layer (Dialog)
"""

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit,
    QPushButton, QLabel, QDateEdit, QMessageBox, QFrame,
)
from PySide6.QtCore import Qt, QDate
from logic.maintenance_logic import MaintenanceLogic


JENIS_MAINTENANCE = [
    "Ganti Oli Mesin",
    "Ganti Oli Gardan",
    "Ganti Ban",
    "Ganti Kampas Rem",
    "Servis Karburator / Injeksi",
    "Tune Up",
    "Ganti Busi",
    "Ganti Rantai",
    "Pengecekan Rem",
    "Lainnya",
]


class DialogMaintenance(QDialog):
    def __init__(self, logic: MaintenanceLogic, parent=None, data: dict = None):
        super().__init__(parent)
        self.logic = logic
        self.edit_data = data
        self.build_ui()
        if data:
            self.isi_form(data)

    def build_ui(self):
        judul = "Edit Riwayat Maintenance" if self.edit_data else "Tambah Riwayat Maintenance"
        self.setWindowTitle(judul)
        self.setMinimumWidth(480)
        self.setObjectName("dialogMaintenance")

        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        header = QFrame()
        header.setObjectName("dialogHeader")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(24, 18, 24, 18)
        lbl_judul = QLabel(judul)
        lbl_judul.setObjectName("dialogTitle")
        lbl_sub = QLabel("Catat riwayat perawatan dan servis motor")
        lbl_sub.setObjectName("dialogSubtitle")
        h_lay.addWidget(lbl_judul)
        h_lay.addWidget(lbl_sub)
        root.addWidget(header)

        body = QFrame()
        body.setObjectName("dialogBody")
        form_lay = QFormLayout(body)
        form_lay.setContentsMargins(24, 20, 24, 20)
        form_lay.setSpacing(12)
        form_lay.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.inp_tanggal = QDateEdit()
        self.inp_tanggal.setCalendarPopup(True)
        self.inp_tanggal.setDate(QDate.currentDate())
        self.inp_tanggal.setObjectName("inputField")
        form_lay.addRow("Tanggal:", self.inp_tanggal)

        self.inp_jenis = QComboBox()
        self.inp_jenis.addItems(JENIS_MAINTENANCE)
        self.inp_jenis.setObjectName("inputField")
        form_lay.addRow("Jenis Maintenance:", self.inp_jenis)

        self.inp_km = QDoubleSpinBox()
        self.inp_km.setRange(0, 9_999_999)
        self.inp_km.setDecimals(1)
        self.inp_km.setSuffix("  km")
        self.inp_km.setObjectName("inputField")
        form_lay.addRow("KM Saat Ini:", self.inp_km)

        self.inp_biaya = QDoubleSpinBox()
        self.inp_biaya.setRange(0, 99_999_999)
        self.inp_biaya.setDecimals(0)
        self.inp_biaya.setPrefix("Rp ")
        self.inp_biaya.setSingleStep(5000)
        self.inp_biaya.setObjectName("inputField")
        form_lay.addRow("Biaya:", self.inp_biaya)

        self.inp_bengkel = QLineEdit()
        self.inp_bengkel.setPlaceholderText("Nama bengkel / mekanik...")
        self.inp_bengkel.setObjectName("inputField")
        form_lay.addRow("Bengkel / Mekanik:", self.inp_bengkel)

        self.inp_catatan = QTextEdit()
        self.inp_catatan.setPlaceholderText("Detail pekerjaan atau catatan tambahan...")
        self.inp_catatan.setFixedHeight(72)
        self.inp_catatan.setObjectName("inputTextEdit")
        form_lay.addRow("Catatan:", self.inp_catatan)

        root.addWidget(body)

        footer = QFrame()
        footer.setObjectName("dialogFooter")
        btn_lay = QHBoxLayout(footer)
        btn_lay.setContentsMargins(24, 14, 24, 14)
        btn_lay.addStretch()

        self.btn_batal = QPushButton("Batal")
        self.btn_batal.setObjectName("btnSecondary")
        self.btn_batal.clicked.connect(self.reject)

        self.btn_simpan = QPushButton("Simpan")
        self.btn_simpan.setObjectName("btnPrimary")
        self.btn_simpan.setDefault(True)
        self.btn_simpan.clicked.connect(self.simpan)

        btn_lay.addWidget(self.btn_batal)
        btn_lay.addWidget(self.btn_simpan)
        root.addWidget(footer)

    def isi_form(self, data: dict):
        self.inp_tanggal.setDate(QDate.fromString(data["tanggal"], "yyyy-MM-dd"))
        idx = self.inp_jenis.findText(data["jenis_maintenance"])
        if idx >= 0:
            self.inp_jenis.setCurrentIndex(idx)
        self.inp_km.setValue(data["km_saat_itu"])
        self.inp_biaya.setValue(data["biaya"])
        self.inp_bengkel.setText(data.get("bengkel", ""))
        self.inp_catatan.setPlainText(data.get("catatan", ""))

    def simpan(self):
        if self.inp_biaya.value() == 0:
            ret = QMessageBox.question(
                self, "Konfirmasi",
                "Biaya diisi Rp 0. Lanjutkan menyimpan?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if ret == QMessageBox.No:
                return
        self.accept()

    def get_data(self) -> dict:
        return {
            "tanggal": self.inp_tanggal.date().toString("yyyy-MM-dd"),
            "jenis_maintenance": self.inp_jenis.currentText(),
            "km_saat_itu": self.inp_km.value(),
            "biaya": self.inp_biaya.value(),
            "bengkel": self.inp_bengkel.text().strip(),
            "catatan": self.inp_catatan.toPlainText().strip(),
        }
