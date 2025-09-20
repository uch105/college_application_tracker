import sys
import os
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QComboBox, QDateEdit, QTextEdit, QMessageBox, QHeaderView,
                             QDialog, QDialogButtonBox, QFormLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtGui import QColor, QPainter, QPalette

class ProfessorAppDB:
    def __init__(self):
        self.db_path = 'professor_applications.db'
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_name TEXT NOT NULL,
                professor_email TEXT NOT NULL,
                university_name TEXT NOT NULL,
                program_name TEXT NOT NULL,
                country_name TEXT NOT NULL,
                application_last_date TEXT NOT NULL,
                email_subject TEXT,
                email_body TEXT,
                email_send_date TEXT,
                status TEXT DEFAULT 'pending',
                response TEXT DEFAULT 'no'
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_all_applications(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM applications')
        data = cursor.fetchall()
        conn.close()
        return data
        
    def get_response_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count all non-empty responses
        cursor.execute("SELECT COUNT(*) FROM applications WHERE response IS NOT NULL AND response != ''")
        total = cursor.fetchone()[0]

        # Count all 'yes' responses
        cursor.execute("SELECT COUNT(*) FROM applications WHERE LOWER(response) = 'yes'")
        yes_count = cursor.fetchone()[0]

        conn.close()
        return yes_count, total
    
    def add_application(self, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO applications 
            (professor_name, professor_email, university_name, program_name, country_name,
             application_last_date, email_subject, email_body, email_send_date, status, response)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
        conn.close()
    
    def update_application(self, app_id, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE applications 
            SET professor_name=?, professor_email=?, university_name=?, program_name=?, country_name=?,
                application_last_date=?, email_subject=?, email_body=?, email_send_date=?, status=?, response=?
            WHERE id=?
        ''', (*data, app_id))
        conn.commit()
        conn.close()
    
    def delete_application(self, app_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM applications WHERE id=?', (app_id,))
        conn.commit()
        conn.close()
    
    def search_applications(self, search_terms):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = 'SELECT * FROM applications WHERE 1=1'
        params = []

        for field, value in search_terms.items():
            if value:
                st = value.strip().lower()
                like = f"%{st}%"
                query += f" AND LOWER({field}) LIKE ?"
                params.append(like)

        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        return data
    
    def get_country_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT country_name, COUNT(*) FROM applications GROUP BY country_name')
        data = cursor.fetchall()
        conn.close()
        return data

class ApplicationDialog(QDialog):
    def __init__(self, parent=None, application_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add Application" if not application_data else "Edit Application")
        self.application_data = application_data
        self.setMinimumWidth(500)
        
        layout = QFormLayout()
        
        self.professor_name = QLineEdit()
        self.professor_email = QLineEdit()
        self.university_name = QLineEdit()
        self.program_name = QLineEdit()
        self.country_name = QLineEdit()
        
        self.application_last_date = QDateEdit()
        self.application_last_date.setCalendarPopup(True)
        self.application_last_date.setDate(QDate.currentDate())
        
        self.email_subject = QLineEdit()
        
        self.email_body = QTextEdit()
        self.email_body.setMaximumHeight(100)
        
        self.email_send_date = QDateEdit()
        self.email_send_date.setCalendarPopup(True)
        self.email_send_date.setDate(QDate.currentDate())
        
        self.status = QComboBox()
        self.status.addItems(["pending", "done"])
        
        self.response = QComboBox()
        self.response.addItems(["no", "yes", "partial"])
        
        layout.addRow("Professor Name:", self.professor_name)
        layout.addRow("Professor Email:", self.professor_email)
        layout.addRow("University Name:", self.university_name)
        layout.addRow("Program Name:", self.program_name)
        layout.addRow("Country Name:", self.country_name)
        layout.addRow("Application Last Date:", self.application_last_date)
        layout.addRow("Email Subject:", self.email_subject)
        layout.addRow("Email Body:", self.email_body)
        layout.addRow("Email Send Date:", self.email_send_date)
        layout.addRow("Status:", self.status)
        layout.addRow("Response:", self.response)
        
        if application_data:
            self.populate_fields()
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)
    
    def populate_fields(self):
        self.professor_name.setText(self.application_data[1])
        self.professor_email.setText(self.application_data[2])
        self.university_name.setText(self.application_data[3])
        self.program_name.setText(self.application_data[4])
        self.country_name.setText(self.application_data[5])
        self.application_last_date.setDate(QDate.fromString(self.application_data[6], "yyyy-MM-dd"))
        self.email_subject.setText(self.application_data[7])
        self.email_body.setText(self.application_data[8])
        self.email_send_date.setDate(QDate.fromString(self.application_data[9], "yyyy-MM-dd"))
        self.status.setCurrentText(self.application_data[10])
        self.response.setCurrentText(self.application_data[11])
    
    def get_data(self):
        return (
            self.professor_name.text(),
            self.professor_email.text(),
            self.university_name.text(),
            self.program_name.text(),
            self.country_name.text(),
            self.application_last_date.date().toString("yyyy-MM-dd"),
            self.email_subject.text(),
            self.email_body.toPlainText(),
            self.email_send_date.date().toString("yyyy-MM-dd"),
            self.status.currentText(),
            self.response.currentText()
        )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professor Application Tracker")
        self.setGeometry(100, 100, 1400, 900)
        
        self.db = ProfessorAppDB()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Search section
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.search_professor = QLineEdit()
        self.search_professor.setPlaceholderText("Search by Professor Name...")
        self.search_professor.textChanged.connect(self.search_applications)
        search_layout.addWidget(self.search_professor)
        
        self.search_email = QLineEdit()
        self.search_email.setPlaceholderText("Search by Professor Email...")
        self.search_email.textChanged.connect(self.search_applications)
        search_layout.addWidget(self.search_email)
        
        self.search_university = QLineEdit()
        self.search_university.setPlaceholderText("Search by University...")
        self.search_university.textChanged.connect(self.search_applications)
        search_layout.addWidget(self.search_university)
        
        self.search_program = QLineEdit()
        self.search_program.setPlaceholderText("Search by Program...")
        self.search_program.textChanged.connect(self.search_applications)
        search_layout.addWidget(self.search_program)
        
        self.search_country = QLineEdit()
        self.search_country.setPlaceholderText("Search by Country...")
        self.search_country.textChanged.connect(self.search_applications)
        search_layout.addWidget(self.search_country)
        
        self.add_btn = QPushButton("Add New Application")
        self.add_btn.clicked.connect(self.open_create_dialog)
        search_layout.addWidget(self.add_btn)
        
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        headers = ["Professor Name", "Professor Email", "University", "Program", 
                  "Country", "App Last Date", "Email Subject", "Email Body", 
                  "Email Send Date", "Status", "Response", "Actions"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Interactive)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Chart section
        chart_layout = QHBoxLayout()
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_layout.addWidget(self.chart_view)
        layout.addLayout(chart_layout)
        
        self.load_data()
        
    def load_data(self):
        data = self.db.get_all_applications()
        self.populate_table(data)
        self.update_chart()

        # --- Update header for Response ---
        yes_count, total_count = self.db.get_response_stats()
        header = self.table.horizontalHeaderItem(10)  # column index of Response
        if header:
            header.setText(f"Response ({yes_count}/{total_count})")
    
    def populate_table(self, data):
        self.table.setRowCount(0)
        
        for row_num, row_data in enumerate(data):
            self.table.insertRow(row_num)
            
            for col_num in range(1, len(row_data)):
                item = QTableWidgetItem(str(row_data[col_num]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_num, col_num-1, item)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, r=row_data: self.edit_application(r))
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, r=row_data: self.delete_application(r))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_widget.setLayout(actions_layout)
            
            self.table.setCellWidget(row_num, 11, actions_widget)
    
    def update_chart(self):
        country_data = self.db.get_country_stats()
        
        series = QPieSeries()
        colors = [
            QColor(65, 105, 225), QColor(220, 20, 60), QColor(46, 139, 87),
            QColor(255, 140, 0), QColor(106, 90, 205), QColor(205, 92, 92),
            QColor(0, 139, 139), QColor(148, 0, 211), QColor(210, 105, 30),
            QColor(70, 130, 180),
        ]
        
        for i, (country, count) in enumerate(country_data):
            slice = QPieSlice(f"{country} ({count})", count)
            slice.setColor(colors[i % len(colors)])
            slice.setLabelVisible(True)
            series.append(slice)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Applications by Country")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        self.chart_view.setChart(chart)
    
    def search_applications(self):
        search_terms = {
            "professor_name": self.search_professor.text(),
            "professor_email": self.search_email.text(),
            "university_name": self.search_university.text(),
            "program_name": self.search_program.text(),
            "country_name": self.search_country.text(),
        }
        data = self.db.search_applications(search_terms)
        self.populate_table(data)
    
    def open_create_dialog(self):
        dialog = ApplicationDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            self.db.add_application(data)
            self.load_data()
            QMessageBox.information(self, "Success", "Application added successfully!")
    
    def edit_application(self, application_data):
        dialog = ApplicationDialog(self, application_data)
        if dialog.exec_():
            data = dialog.get_data()
            self.db.update_application(application_data[0], data)
            self.load_data()
            QMessageBox.information(self, "Success", "Application updated successfully!")
    
    def delete_application(self, application_data):
        reply = QMessageBox.question(self, "Confirm Delete", 
                                    f"Are you sure you want to delete the application for {application_data[1]}?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.Yes:
            self.db.delete_application(application_data[0])
            self.load_data()
            QMessageBox.information(self, "Success", "Application deleted successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
