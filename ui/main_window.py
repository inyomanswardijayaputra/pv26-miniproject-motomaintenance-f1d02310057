import csv
import sqlite3
from PySide6.QtWidgets import (
    QComboBox, QDialog, QFrame, QMainWindow, QSpinBox, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
    QLabel, QFormLayout, QMessageBox, QHeaderView, QFileDialog, QSplitter, QTabWidget
)

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QFont, QColor

from logic.maintenance_logic import MaintenanceLogic
from ui.dialog_aktivitas import DialogAktivitas
from ui.dialog_maintenance import DialogMaintenance
from ui.panel_status import PanelStatus

NAMA = "I Nyoman Swardi Jaya Putra"
NIM = "F1D02310057"
NAMA_APP       = "MotoMaintenance"
DESKRIPSI_APP  = (
    "Aplikasi manajemen maintenance motor berbasis desktop. "
    "Mencatat aktivitas harian, konsumsi bensin, riwayat servis, "
    "dan memberikan peringatan jadwal perawatan motor."
)


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle(f"{NAMA_APP}")

        self.db = db
        self.logic = MaintenanceLogic(db)
        self.selected_id = None
        
        self.setup_ui()
        self.setup_menubar() 
        self.refresh_semua()
        
        self.lbl_nama = QLabel("I Nyoman Swardi Jaya Putra - F1D02310057")
        self.lbl_nama.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.statusBar().addPermanentWidget(self.lbl_nama)
        
        self.showMaximized()
    
    def setup_menubar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&File")
        exit_action = file_menu.addAction("Keluar")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        aktivitas_menu = menubar.addMenu("&Aktivitas")
        aktivitas_action = aktivitas_menu.addAction("Tambah Aktivitas")
        aktivitas_action.setShortcut("Ctrl+N")
        aktivitas_action.triggered.connect(self.tambah_aktivitas)

        maintenance_menu = menubar.addMenu("&Maintenance")
        maintenance_action = maintenance_menu.addAction("Tambah Maintenance")
        maintenance_action.triggered.connect(self.tambah_maintenance)
        maintenance_action.setShortcut("Ctrl+M")
        
        help_menu = menubar.addMenu("&Bantuan")
        about_action = help_menu.addAction("Tentang Aplikasi")
        about_action.triggered.connect(self.show_about)
        
        version_action = help_menu.addAction("Versi")
        version_action.triggered.connect(self.show_version)
    
    def setup_ui(self):
        self.main_container = QWidget()
        self.main_container.setObjectName("mainContainer")
        layout_utama = QVBoxLayout(self.main_container)
        layout_utama.setContentsMargins(16, 16, 16, 16)
        layout_utama.setSpacing(20) 
        
        self.status_maintenance = PanelStatus(self.logic)
        layout_utama.addWidget(self.status_maintenance)

        self.panel_aktivitas = QWidget()
        self.panel_aktivitas.setObjectName("tabAktivitas")
        lay_akt = QVBoxLayout(self.panel_aktivitas)
        lay_akt.setContentsMargins(0, 0, 0, 0)
        lay_akt.setSpacing(12)

        toolbar_akt = QHBoxLayout()
        lbl_akt = QLabel("Aktivitas Harian Motor")
        lbl_akt.setObjectName("tabSectionTitle")
        toolbar_akt.addWidget(lbl_akt)
        toolbar_akt.addStretch()

        btn_tambah_akt = QPushButton("Tambah")
        btn_tambah_akt.setObjectName("btnPrimary")
        btn_tambah_akt.clicked.connect(self.tambah_aktivitas)

        btn_edit_akt = QPushButton("Edit")
        btn_edit_akt.setObjectName("btnSecondary")
        btn_edit_akt.clicked.connect(self.edit_aktivitas)

        btn_hapus_akt = QPushButton("Hapus")
        btn_hapus_akt.setObjectName("btnDanger")
        btn_hapus_akt.clicked.connect(self.hapus_aktivitas)

        toolbar_akt.addWidget(btn_tambah_akt)
        toolbar_akt.addWidget(btn_edit_akt)
        toolbar_akt.addWidget(btn_hapus_akt)
        lay_akt.addLayout(toolbar_akt)

        self.tabel_aktivitas = QTableWidget()
        self.tabel_aktivitas.setObjectName("dataTable")
        self.tabel_aktivitas.setColumnCount(8)
        self.tabel_aktivitas.setHorizontalHeaderLabels([
            "ID", "Tanggal", "Jenis Aktivitas", "Jarak (km)",
            "Liter", "Biaya Bensin", "Kondisi Mesin", "Catatan",
        ])
        self.tabel_aktivitas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabel_aktivitas.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.tabel_aktivitas.setColumnWidth(0, 50)
        self.tabel_aktivitas.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabel_aktivitas.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabel_aktivitas.setAlternatingRowColors(True)
        self.tabel_aktivitas.verticalHeader().setVisible(False)
        self.tabel_aktivitas.doubleClicked.connect(self.edit_aktivitas)
        lay_akt.addWidget(self.tabel_aktivitas)

        layout_utama.addWidget(self.panel_aktivitas)

        self.panel_maintenance = QWidget()
        self.panel_maintenance.setObjectName("tabMaintenance")
        lay_maint = QVBoxLayout(self.panel_maintenance)
        lay_maint.setContentsMargins(0, 0, 0, 0)
        lay_maint.setSpacing(12)

        toolbar_maint = QHBoxLayout()
        lbl_maint = QLabel("Riwayat Maintenance Motor")
        lbl_maint.setObjectName("tabSectionTitle")
        toolbar_maint.addWidget(lbl_maint)
        toolbar_maint.addStretch()

        btn_tambah_maint = QPushButton("Tambah")
        btn_tambah_maint.setObjectName("btnPrimary")
        btn_tambah_maint.clicked.connect(self.tambah_maintenance)

        btn_edit_maint = QPushButton("Edit")
        btn_edit_maint.setObjectName("btnSecondary")
        btn_edit_maint.clicked.connect(self.edit_maintenance)

        btn_hapus_maint = QPushButton("Hapus")
        btn_hapus_maint.setObjectName("btnDanger")
        btn_hapus_maint.clicked.connect(self.hapus_maintenance)

        toolbar_maint.addWidget(btn_tambah_maint)
        toolbar_maint.addWidget(btn_edit_maint)
        toolbar_maint.addWidget(btn_hapus_maint)
        lay_maint.addLayout(toolbar_maint)

        self.tabel_maintenance = QTableWidget()
        self.tabel_maintenance.setObjectName("dataTable")
        self.tabel_maintenance.setColumnCount(7)
        self.tabel_maintenance.setHorizontalHeaderLabels([
            "ID", "Tanggal", "Jenis Maintenance", "KM Saat Itu",
            "Biaya", "Bengkel", "Catatan",
        ])
        self.tabel_maintenance.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabel_maintenance.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.tabel_maintenance.setColumnWidth(0, 50)
        self.tabel_maintenance.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabel_maintenance.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabel_maintenance.setAlternatingRowColors(True)
        self.tabel_maintenance.verticalHeader().setVisible(False)
        self.tabel_maintenance.doubleClicked.connect(self.edit_maintenance)
        lay_maint.addWidget(self.tabel_maintenance)
        
        layout_utama.addWidget(self.panel_maintenance)
        self.setCentralWidget(self.main_container)
        
    def refresh_semua(self):
        self.load_tabel_aktivitas()
        self.load_tabel_maintenance()
        self.status_maintenance.refresh()
        self.cek_peringatan_otomatis()
        
        ringkasan = self.logic.get_ringkasan_keuangan()
        self.statusBar().showMessage(f"Bensin: {self.logic.format_rupiah(ringkasan['bensin'])} ~ Maintenance: {self.logic.format_rupiah(ringkasan['maintenance'])} ~ Total: {self.logic.format_rupiah(ringkasan['total'])}")
        
    def load_tabel_aktivitas(self):
        data = self.db.get_semua_aktivitas()
        self.tabel_aktivitas.setRowCount(0)
        
        for row_data in data:
            r = self.tabel_aktivitas.rowCount()
            self.tabel_aktivitas.insertRow(r)
            
            vals = [
                str(row_data["id_aktivitas"]),
                row_data["tanggal"],
                row_data["jenis_aktivitas"],
                f"{row_data['jarak_tempuh']:.1f}",
                f"{row_data['liter_bensin']:.2f}",
                self.logic.format_rupiah(row_data["harga_bensin"]),
                row_data["kondisi_mesin"],
                row_data["catatan"] or "",
            ]
            
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter if c != 7 else Qt.AlignLeft | Qt.AlignVCenter)
                self.tabel_aktivitas.setItem(r, c, item)

            kondisi = row_data["kondisi_mesin"]
            if kondisi in ("Kasar", "Bermasalah"):
                for c in range(self.tabel_aktivitas.columnCount()):
                    self.tabel_aktivitas.item(r, c).setBackground(QColor("#fef2f2"))
            elif kondisi == "Perlu Dicek":
                for c in range(self.tabel_aktivitas.columnCount()):
                    self.tabel_aktivitas.item(r, c).setBackground(QColor("#fffbeb"))

    def load_tabel_maintenance(self):
        data = self.db.get_semua_maintenance()
        self.tabel_maintenance.setRowCount(0)
        for row_data in data:
            r = self.tabel_maintenance.rowCount()
            self.tabel_maintenance.insertRow(r)
            
            vals = [
                str(row_data["id_maintenance"]),
                row_data["tanggal"],
                row_data["jenis_maintenance"],
                f"{row_data['km_saat_itu']:,.1f}",
                self.logic.format_rupiah(row_data["biaya"]),
                row_data.get("bengkel", ""),
                row_data["catatan"] or "",
            ]
            
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter if c not in (2, 5) else Qt.AlignLeft | Qt.AlignVCenter)
                self.tabel_maintenance.setItem(r, c, item)
    
    def tambah_aktivitas(self):
        dlg = DialogAktivitas(self.logic, self)
        if dlg.exec() == QDialog.Accepted:
            self.db.tambah_aktivitas(dlg.get_data())
            self.refresh_semua()
            self.lbl_status.setText("Aktivitas berhasil ditambahkan.")

    def edit_aktivitas(self):
        row = self.tabel_aktivitas.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih baris yang ingin diedit.")
            return
        id_ = int(self.tabel_aktivitas.item(row, 0).text())
        data = self.db.get_aktivitas_by_id(id_)
        dlg = DialogAktivitas(self.logic, self, data=data)
        if dlg.exec() == QDialog.Accepted:
            self.db.update_aktivitas(id_, dlg.get_data())
            self.refresh_semua()
            self.lbl_status.setText("Aktivitas berhasil diperbarui.")

    def hapus_aktivitas(self):
        row = self.tabel_aktivitas.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih baris yang ingin dihapus.")
            return
        id_ = int(self.tabel_aktivitas.item(row, 0).text())
        tgl = self.tabel_aktivitas.item(row, 1).text()
        ret = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Hapus aktivitas tanggal {tgl}?\nTindakan ini tidak bisa dibatalkan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret == QMessageBox.Yes:
            self.db.hapus_aktivitas(id_)
            self.refresh_semua()
            self.lbl_status.setText("Aktivitas dihapus.")

    def tambah_maintenance(self):
        dlg = DialogMaintenance(self.logic, self)
        if dlg.exec() == QDialog.Accepted:
            self.db.tambah_maintenance(dlg.get_data())
            self.refresh_semua()
            self.lbl_status.setText("Riwayat maintenance berhasil ditambahkan.")

    def edit_maintenance(self):
        row = self.tabel_maintenance.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih baris yang ingin diedit.")
            return
        id_ = int(self.tabel_maintenance.item(row, 0).text())
        data = self.db.get_maintenance_by_id(id_)
        dlg = DialogMaintenance(self.logic, self, data=data)
        if dlg.exec() == QDialog.Accepted:
            self.db.update_maintenance(id_, dlg.get_data())
            self.refresh_semua()
            self.lbl_status.setText("Maintenance berhasil diperbarui.")

    def hapus_maintenance(self):
        row = self.tabel_maintenance.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih baris yang ingin dihapus.")
            return
        id_ = int(self.tabel_maintenance.item(row, 0).text())
        jenis = self.tabel_maintenance.item(row, 2).text()
        ret = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Hapus riwayat '{jenis}'?\nTindakan ini tidak bisa dibatalkan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret == QMessageBox.Yes:
            self.db.hapus_maintenance(id_)
            self.refresh_semua()
            self.lbl_status.setText("Riwayat maintenance dihapus.")

    def cek_peringatan_otomatis(self):
        statuses = self.logic.cek_semua_maintenance()
        kritis = [s for s in statuses if s.status in ("segera", "lewat")]
        if kritis:
            pesan = "\n".join(f"• {s.pesan}" for s in kritis)
            QMessageBox.warning(
                self,
                "Peringatan Maintenance",
                f"Motor membutuhkan perhatian:\n\n{pesan}",
            )

    def show_about(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Tentang Aplikasi")
        dlg.setObjectName("dialogTentang")
        dlg.setFixedWidth(420)

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        header = QFrame()
        header.setObjectName("dialogHeader")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(24, 20, 24, 20)
        lbl_app = QLabel(f"{NAMA_APP}")
        lbl_app.setObjectName("dialogTitle")
        h_lay.addWidget(lbl_app)
        lay.addWidget(header)

        body = QFrame()
        body.setObjectName("dialogBody")
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(24, 16, 24, 16)
        b_lay.setSpacing(10)

        info = [
            ("Aplikasi",   NAMA_APP),
            ("Deskripsi",  DESKRIPSI_APP),
            ("Nama",       NAMA),
            ("NIM",        NIM),
        ]
        for label, val in info:
            lbl_l = QLabel(f"<b>{label}</b>")
            lbl_l.setObjectName("tentangLabel")
            lbl_v = QLabel(val)
            lbl_v.setObjectName("tentangValue")
            lbl_v.setWordWrap(True)
            b_lay.addWidget(lbl_l)
            b_lay.addWidget(lbl_v)

        lay.addWidget(body)

        footer = QFrame()
        footer.setObjectName("dialogFooter")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(24, 14, 24, 14)
        f_lay.addStretch()
        btn_ok = QPushButton("Tutup")
        btn_ok.setObjectName("btnPrimary")
        btn_ok.clicked.connect(dlg.accept)
        f_lay.addWidget(btn_ok)
        lay.addWidget(footer)

        dlg.exec()

    def export_csv(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "Perpustakaan.csv", "CSV Files (*.csv)"
        )
        if not filepath:
            return
        
        try:
            data = self.db.ambil_semua()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Kode Buku', 'Judul Buku', 'Pengarang', 'Tahun', 'Stok', 'Kategori'])
                for r in data:
                    writer.writerow([
                        r['id'], r['kode_buku'], r['judul_buku'], 
                        r['pengarang'], r['tahun_terbit'], r['stok'], r['kategori']
                    ])
            QMessageBox.information(self, "Sukses", f"Export berhasil!\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_version(self):
        QMessageBox.information(self, "Versi", "Versi Aplikasi: 1.0.0 (Stable)\nBuild: 2026.04.25")