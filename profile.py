import json
import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QHBoxLayout, QTextEdit, QCheckBox, QPushButton, QListWidget, QMessageBox, QComboBox, QDialog
)


class AboutProgram(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AboutProgram")
        self.resize(700, 100)

        layout_about = QVBoxLayout(self)
        self.label_about = QLabel(
            "О программе:\n"
            "Task Manager позволяет добавить вашу задачу в общий список и указать информацию о ней.\n"
            "Можно удалить задачу из списка кликнув по ней и нажав на кнопку удалить.\n"
            "Также можно удалить все задачи из списка нажав на кнопку 'Очистить все задачи'.\n"
            "\n"
            "Автор:\n"
            "Савченков Ярослав"
        )
        layout_about.addWidget(self.label_about)


def show_about():
    dialog = AboutProgram()
    dialog.exec()


def format_task(task: dict):
    notify = "Да" if task['notify'] else "Нет"
    important = "Да" if task['important'] else "Нет"
    return (f"{task['name']}: ({task['desc']})\n Приоритет: {task['priority']}\n "
            f"Отправить уведомление: {notify}\n Важное: {important}")


class TaskManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task Manager")
        self.resize(800, 600)
        self.tasks = []

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        self.dialog_button = QPushButton("О программе")
        main_layout.addWidget(self.dialog_button)
        self.dialog_button.clicked.connect(show_about)

        self.dialog_button.setStyleSheet("""
            QPushButton { background-color: #161617; color: white; }
        """)

        task_name_layout = QHBoxLayout()
        text_task_name = QLabel("Название задачи:")
        self.task_name_input = QLineEdit()
        task_name_layout.addWidget(text_task_name)
        task_name_layout.addWidget(self.task_name_input)
        main_layout.addLayout(task_name_layout)

        desc_task_layout = QVBoxLayout()
        text_desc_task = QLabel("Описание:")
        self.task_desc_input = QTextEdit()
        desc_task_layout.addWidget(text_desc_task)
        desc_task_layout.addWidget(self.task_desc_input)
        main_layout.addLayout(desc_task_layout)

        self.priority_label = QLabel("Приоритет:")
        main_layout.addWidget(self.priority_label)
        self.priority = QComboBox()
        self.priority.addItems(["-","Низкий", "Средний", "Высокий"])
        main_layout.addWidget(self.priority)

        self.is_important = QCheckBox("Важное")
        self.is_notify = QCheckBox("Отправить уведомление")
        main_layout.addWidget(self.is_important)
        main_layout.addWidget(self.is_notify)

        self.create_button = QPushButton("Создать задачу")
        main_layout.addWidget(self.create_button)
        self.create_button.clicked.connect(self.create_task)

        self.create_button.setStyleSheet("""
            QPushButton { background-color: #543200; color: white; }
            QPushButton:hover { background-color: brown; }
            QPushButton:pressed { background-color: green; }
        """)

        self.task_list = QListWidget()
        self.load_tasks()
        main_layout.addWidget(self.task_list)

        status_layout = QHBoxLayout()
        text_status = QLabel("Задачи: ")
        self.status = QLabel(str(self.task_list.count()))
        status_layout.addWidget(text_status)
        status_layout.addWidget(self.status)
        main_layout.addLayout(status_layout)

        delete_layout = QHBoxLayout()
        self.del_task_button = QPushButton("Удалить выбранную задачу")
        delete_layout.addWidget(self.del_task_button)
        self.del_task_button.clicked.connect(self.delete_task)
        self.clear_button = QPushButton("Очистить все задачи")
        delete_layout.addWidget(self.clear_button)
        self.clear_button.clicked.connect(self.clear_tasks)
        main_layout.addLayout(delete_layout)

        self.del_task_button.setStyleSheet("""
            QPushButton { background-color: maroon; color: white; }
        """)

        self.clear_button.setStyleSheet("""
                    QPushButton { background-color: green; color: white; }
        """)


    def create_task(self):
        name_task = self.task_name_input.text().strip()

        if not name_task:
            QMessageBox.warning(self, "Ошибка", "Введите название задачи")
            return

        desc_task = self.task_desc_input.toPlainText().strip()
        priority = self.priority.currentText()
        notify = self.is_notify.isChecked()
        important = self.is_important.isChecked()

        self.tasks.append({"name": name_task, "desc": desc_task, "priority": priority, "notify": notify, "important": important})
        self.save_tasks()

        self.task_name_input.clear()
        self.task_desc_input.clear()
        self.priority.setCurrentIndex(0)
        self.is_important.setChecked(False)
        self.is_notify.setChecked(False)

        self.task_list.addItem(format_task(self.tasks[-1]))
        self.status.setText(str(self.task_list.count()))


    def clear_tasks(self):
        if self.task_list.count() == 0:
            return

        answer = QMessageBox.question(self, "Подтверждение", "Удалить все задачи?")

        if answer == QMessageBox.StandardButton.Yes:
            self.task_list.clear()
            self.status.setText(str(self.task_list.count()))
            self.tasks.clear()
            self.save_tasks()


    def delete_task(self):
        item = self.task_list.currentItem()

        if item is None:
            return

        answer = QMessageBox.question(self, "Подтверждение", "Удалить выбранную задачу?")

        if answer == QMessageBox.StandardButton.Yes:
            row = self.task_list.row(item)
            self.task_list.takeItem(row)
            self.status.setText(str(self.task_list.count()))
            self.tasks.pop(row)
            self.save_tasks()


    def load_tasks(self):
        try:
            with open("tasks.json", "r", encoding="utf-8") as f:
                tasks = json.load(f)
                self.tasks = tasks
        except FileNotFoundError:
            self.tasks = []
        for task in self.tasks:
            self.task_list.addItem(format_task(task))


    def save_tasks(self):
        try:
            with open("tasks.json", "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=4)
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить задачи: {e}")


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QWidget { background-color: #282829; }
        QLabel {color: white; }
        QCheckBox { color: white; }
        QComboBox { color: white; }
        QTextEdit { background-color: grey; }
        QLineEdit { background-color: grey; }
        QListWidget { background-color: grey; }
    """)

    window = TaskManagerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()