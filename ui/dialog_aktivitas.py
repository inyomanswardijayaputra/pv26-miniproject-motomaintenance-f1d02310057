

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit,
    QPushButton, QLabel, QDateEdit, QMessageBox,
    QFrame,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from logic.maintenance_logic import MaintenanceLogic

class DialogAktivitas(QDialog):
    def __init__(self, logic: MaintenanceLogic, parent=None, data: dict = None):
        super().__init__(parent)
        self.logic = logic
        self.edit_data = data 
        self.build_ui()
        if data:
            self.isi_form(data)

    def build_ui(self):
        judul = "Edit Aktivitas" if self.edit_data else "Tambah Aktivitas Harian"
        self.setWindowTitle(judul)
        self.setMinimumWidth(460)
        self.setObjectName("dialogAktivitas")

        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        header = QFrame()
        header.setObjectName("dialogHeader")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(24, 18, 24, 18)
        lbl_judul = QLabel(judul)
        lbl_judul.setObjectName("dialogTitle")
        lbl_sub = QLabel("Catat perjalanan dan konsumsi bensin hari ini")
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
        form_lay.addRow("Tanggal :", self.inp_tanggal)

        self.inp_jenis = QComboBox()
        self.inp_jenis.addItems(self.logic.JENIS_AKTIVITAS)
        self.inp_jenis.setObjectName("inputField")
        form_lay.addRow("Jenis Aktivitas :", self.inp_jenis)

        self.inp_jarak = QDoubleSpinBox()
        self.inp_jarak.setRange(0, 9_999_999)
        self.inp_jarak.setDecimals(1)
        self.inp_jarak.setSuffix("  KM")
        self.inp_jarak.setObjectName("inputField")
        form_lay.addRow("Jarak Tempuh:", self.inp_jarak)

        self.inp_liter = QDoubleSpinBox()
        self.inp_liter.setRange(0, 999)
        self.inp_liter.setDecimals(2)
        self.inp_liter.setSuffix("  L")
        self.inp_liter.setObjectName("inputField")
        form_lay.addRow("Liter Bensin:", self.inp_liter)

        self.inp_harga = QDoubleSpinBox()
        self.inp_harga.setRange(0, 9_999_999)
        self.inp_harga.setDecimals(0)
        self.inp_harga.setPrefix("Rp ")
        self.inp_harga.setSingleStep(1000)
        self.inp_harga.setObjectName("inputField")
        form_lay.addRow("Total Biaya Bensin:", self.inp_harga)

        self.inp_kondisi = QComboBox()
        self.inp_kondisi.addItems(self.logic.KONDISI_MESIN)
        self.inp_kondisi.setObjectName("inputField")
        form_lay.addRow("Kondisi Mesin:", self.inp_kondisi)

        self.inp_catatan = QTextEdit()
        self.inp_catatan.setPlaceholderText("Catatan tambahan (opsional)...")
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
        
        idx = self.inp_jenis.findText(data["jenis_aktivitas"])
        if idx >= 0:
            self.inp_jenis.setCurrentIndex(idx)
            
        self.inp_jarak.setValue(data["jarak_tempuh"])
        self.inp_liter.setValue(data["liter_bensin"])
        self.inp_harga.setValue(data["harga_bensin"])
        
        idx2 = self.inp_kondisi.findText(data["kondisi_mesin"])
        if idx2 >= 0:
            self.inp_kondisi.setCurrentIndex(idx2)
            
        self.inp_catatan.setPlainText(data.get("catatan", ""))

    def simpan(self):
        if self.inp_jarak.value() == 0 and self.inp_harga.value() == 0:
            QMessageBox.warning(
                self, "Validasi",
                "Masukkan minimal jarak tempuh atau biaya bensin.",
            )
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "tanggal": self.inp_tanggal.date().toString("yyyy-MM-dd"),
            "jenis_aktivitas": self.inp_jenis.currentText(),
            "jarak_tempuh": self.inp_jarak.value(),
            "liter_bensin": self.inp_liter.value(),
            "harga_bensin": self.inp_harga.value(),
            "kondisi_mesin": self.inp_kondisi.currentText(),
            "catatan": self.inp_catatan.toPlainText().strip(),
        }
