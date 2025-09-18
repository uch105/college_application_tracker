import sys
import os
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QComboBox, QDateEdit, QTextEdit, QMessageBox, QHeaderView,
                             QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtGui import QColor, QPainter, QPalette
from fuzzywuzzy import process, fuzz

class ProfessorAppDB:
    def __init__(self):
        #self.db_dir = '/home/uch/application_process/'
        #self.db_path = os.path.join(self.db_dir, 'professor_applications.db')
        self.db_path = 'professor_applications.db'
        self.init_db()
    
    def init_db(self):
        #if not os.path.exists(self.db_dir):
            #os.makedirs(self.db_dir)
        
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
    
    def search_applications(self, search_term, filters=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM applications WHERE 1=1'
        params = []
        
        # Add search term condition (fuzzy matching for professor email)
        if search_term:
            cursor.execute('SELECT id, professor_email FROM applications')
            all_emails = [(row[0], row[1]) for row in cursor.fetchall()]
            
            # Extract just the email strings for fuzzy matching
            email_strings = [email[1] for email in all_emails]
            
            # Get fuzzy matches
            matched_emails = process.extract(search_term, email_strings, limit=10, scorer=fuzz.partial_ratio)
            
            # Filter by threshold and get the IDs of matching records
            matched_ids = []
            for email, score in matched_emails:
                if score > 50:  # Threshold of 50
                    # Find the ID for this email
                    for id, em in all_emails:
                        if em == email:
                            matched_ids.append(id)
                            break
            
            if matched_ids:
                placeholders = ','.join(['?'] * len(matched_ids))
                query += f' AND id IN ({placeholders})'
                params.extend(matched_ids)
            else:
                # If no fuzzy matches, try exact match
                query += ' AND professor_email LIKE ?'
                params.append(f'%{search_term}%')
        
        # Add filter conditions
        if filters:
            for field, value in filters.items():
                if value:
                    query += f' AND {field}=?'
                    params.append(value)
        
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
        
        # If editing, populate fields with existing data
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
        # Skip the ID field (index 0) when populating
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

class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Applications")
        self.setModal(True)
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        # Status filter
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        self.status_all = QCheckBox("All")
        self.status_all.setChecked(True)
        self.status_pending = QCheckBox("Pending")
        self.status_done = QCheckBox("Done")
        status_layout.addWidget(self.status_all)
        status_layout.addWidget(self.status_pending)
        status_layout.addWidget(self.status_done)
        status_group.setLayout(status_layout)
        
        # Response filter
        response_group = QGroupBox("Response")
        response_layout = QVBoxLayout()
        self.response_all = QCheckBox("All")
        self.response_all.setChecked(True)
        self.response_no = QCheckBox("No")
        self.response_yes = QCheckBox("Yes")
        self.response_partial = QCheckBox("Partial")
        response_layout.addWidget(self.response_all)
        response_layout.addWidget(self.response_no)
        response_layout.addWidget(self.response_yes)
        response_layout.addWidget(self.response_partial)
        response_group.setLayout(response_layout)
        
        # University filter
        university_group = QGroupBox("University")
        university_layout = QVBoxLayout()
        self.university_filter = QLineEdit()
        self.university_filter.setPlaceholderText("Enter university name")
        university_layout.addWidget(self.university_filter)
        university_group.setLayout(university_layout)
        
        # Professor filter
        professor_group = QGroupBox("Professor")
        professor_layout = QVBoxLayout()
        self.professor_filter = QLineEdit()
        self.professor_filter.setPlaceholderText("Enter professor name")
        professor_layout.addWidget(self.professor_filter)
        professor_group.setLayout(professor_layout)
        
        layout.addWidget(status_group)
        layout.addWidget(response_group)
        layout.addWidget(university_group)
        layout.addWidget(professor_group)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        self.setLayout(layout)
    
    def get_filters(self):
        filters = {}
        
        # Status filter
        if not self.status_all.isChecked():
            if self.status_pending.isChecked():
                filters['status'] = 'pending'
            elif self.status_done.isChecked():
                filters['status'] = 'done'
        
        # Response filter
        if not self.response_all.isChecked():
            if self.response_no.isChecked():
                filters['response'] = 'no'
            elif self.response_yes.isChecked():
                filters['response'] = 'yes'
            elif self.response_partial.isChecked():
                filters['response'] = 'partial'
        
        # University filter
        university = self.university_filter.text().strip()
        if university:
            filters['university_name'] = university
        
        # Professor filter
        professor = self.professor_filter.text().strip()
        if professor:
            filters['professor_name'] = professor
        
        return filters

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professor Application Tracker")
        self.setGeometry(100, 100, 1400, 900)
        
        self.db = ProfessorAppDB()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Search and filter section
        search_filter_layout = QHBoxLayout()
        search_filter_layout.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by professor email...")
        self.search_input.textChanged.connect(self.search_applications)
        search_filter_layout.addWidget(self.search_input)
        
        self.filter_btn = QPushButton("Filter")
        self.filter_btn.clicked.connect(self.open_filter_dialog)
        search_filter_layout.addWidget(self.filter_btn)
        
        self.add_btn = QPushButton("Add New Application")
        self.add_btn.clicked.connect(self.open_create_dialog)
        search_filter_layout.addWidget(self.add_btn)
        
        layout.addLayout(search_filter_layout)
        
        # Table
        self.table = QTableWidget()
        # 12 columns (excluding ID) + 1 for actions
        self.table.setColumnCount(12)
        headers = ["Professor Name", "Professor Email", "University", "Program", 
                  "Country", "App Last Date", "Email Subject", "Email Body", 
                  "Email Send Date", "Status", "Response", "Actions"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Make the email body column wider
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Interactive)
        
        # Style the table
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        # Chart section
        chart_layout = QHBoxLayout()
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_layout.addWidget(self.chart_view)
        layout.addLayout(chart_layout)
        
        # Load initial data
        self.load_data()
    
    def load_data(self):
        data = self.db.get_all_applications()
        self.populate_table(data)
        self.update_chart()
    
    def populate_table(self, data):
        self.table.setRowCount(0)
        
        for row_num, row_data in enumerate(data):
            self.table.insertRow(row_num)
            
            # Start from index 1 to skip the ID column
            for col_num in range(1, len(row_data)):
                item = QTableWidgetItem(str(row_data[col_num]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_num, col_num-1, item)
            
            # Add edit and delete buttons in the last column
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
            QColor(65, 105, 225),   # Royal Blue
            QColor(220, 20, 60),    # Crimson
            QColor(46, 139, 87),    # Sea Green
            QColor(255, 140, 0),    # Dark Orange
            QColor(106, 90, 205),   # Slate Blue
            QColor(205, 92, 92),    # Indian Red
            QColor(0, 139, 139),    # Dark Cyan
            QColor(148, 0, 211),    # Dark Violet
            QColor(210, 105, 30),   # Chocolate
            QColor(70, 130, 180),   # Steel Blue
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
        search_term = self.search_input.text().strip()
        if not search_term:
            self.load_data()
            return
        
        data = self.db.search_applications(search_term, self.current_filters if hasattr(self, 'current_filters') else None)
        self.populate_table(data)
    
    def open_filter_dialog(self):
        dialog = FilterDialog(self)
        if dialog.exec_():
            self.current_filters = dialog.get_filters()
            self.search_applications()
    
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
            self.db.update_application(application_data[0], data)  # ID is at index 0
            self.load_data()
            QMessageBox.information(self, "Success", "Application updated successfully!")
    
    def delete_application(self, application_data):
        reply = QMessageBox.question(self, "Confirm Delete", 
                                    f"Are you sure you want to delete the application for {application_data[1]}?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.Yes:
            self.db.delete_application(application_data[0])  # ID is at index 0
            self.load_data()
            QMessageBox.information(self, "Success", "Application deleted successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Apply a simple style
    app.setStyle('Fusion')
    
    # Set a clean palette
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