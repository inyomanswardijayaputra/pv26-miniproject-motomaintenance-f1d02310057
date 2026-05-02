from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt
from logic.maintenance_logic import MaintenanceLogic, StatusMaintenance

class KartuStatus(QFrame):

    STATUS_COLORS = {
        "aman":      "#22c55e",
        "perhatian": "#f1f50b",
        "segera":    "#ef9f44",
        "lewat":     "#ed3a3a",
    }

    def __init__(self, status: StatusMaintenance, parent=None):
        super().__init__(parent)
        self.setObjectName("kartuStatus")
        self._build(status)

    def _build(self, s: StatusMaintenance):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(6)

        top = QHBoxLayout()
        lbl_nama = QLabel(s.label)
        lbl_nama.setObjectName("statusNama")

        lbl_persen = QLabel(f"{s.persen:.0f}%")
        lbl_persen.setObjectName("statusPersen")
        color = self.STATUS_COLORS.get(s.status, "#1a1a1a")
        lbl_persen.setStyleSheet(f"color: {color}; font-weight: 700;")

        top.addWidget(lbl_nama)
        top.addStretch()
        top.addWidget(lbl_persen)
        lay.addLayout(top)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(int(s.persen))
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        bar.setObjectName(f"progressBar_{s.status}")
        lay.addWidget(bar)

        lbl_km = QLabel(f"{s.km_sejak_terakhir:.0f} / {s.batas_km:.0f} km")
        lbl_km.setObjectName("statusKm")
        lay.addWidget(lbl_km)

        lbl_pesan = QLabel(s.pesan)
        lbl_pesan.setObjectName("statusPesan")
        lbl_pesan.setWordWrap(True)
        lay.addWidget(lbl_pesan)

class PanelStatus(QWidget):

    def __init__(self, logic: MaintenanceLogic, parent=None):
        super().__init__(parent)
        self.logic = logic
        self.setObjectName("panelStatus")
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        header = QFrame()
        header.setObjectName("panelHeader")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(16, 10, 16, 5)

        lbl_title = QLabel("Status Kesehatan Motor")
        lbl_title.setObjectName("panelTitle")
        h_lay.addWidget(lbl_title)

        self.lbl_total_km = QLabel("Total KM: —")
        self.lbl_total_km.setObjectName("panelSubinfo")
        h_lay.addWidget(self.lbl_total_km)
        root.addWidget(header)

        self.container_kartu = QWidget()
        self.container_kartu.setObjectName("statusContainer")
        
        self.lay_kartu = QHBoxLayout(self.container_kartu)
        self.lay_kartu.setContentsMargins(12, 5, 12, 12)
        self.lay_kartu.setSpacing(10)
        
        root.addWidget(self.container_kartu)
        
    def refresh(self):
        total_km = self.logic.db.get_total_km() or 0 
        self.lbl_total_km.setText(f"Total KM Tercatat: {total_km:,.1f} km")

        while self.lay_kartu.count() > 0:
            item = self.lay_kartu.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        statuses = self.logic.cek_semua_maintenance()
        for s in statuses:
            kartu = KartuStatus(s)
         
            self.lay_kartu.addWidget(kartu)
