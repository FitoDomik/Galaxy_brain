import sys
import json
import os
import random
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QProgressBar, QSpinBox, QProgressDialog, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
class NoArrowsSpinBox(QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
class GitHubDiscussionsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('GALAXY-BRAIN')
        self.setGeometry(300, 200, 600, 500)
        self.config_file = "user_data.json"
        self.init_random_content()
        self.author_token = "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"
        self.user_token = ""
        self.init_ui()
        self.load_user_data()
    def init_random_content(self):
        self.random_titles = [
            "Вопрос по использованию библиотеки",
            "Помогите решить проблему с модулем",
            "Как правильно реализовать функциональность?",
            "Неожиданное поведение в коде",
            "Вопрос о производительности"
        ]
        self.random_bodies = [
            "Столкнулся с проблемой при использовании библиотеки. Какой правильный способ решения этой задачи? Пробовал разные подходы, но ничего не помогло. Буду благодарен за помощь!",
            "При работе с кодом появляется странная ошибка, которую не могу исправить. Я пытался разными способами, но безуспешно. Кто-нибудь сталкивался с подобным и знает решение?",
            "Ищу оптимальный способ реализации данной функциональности. Текущее решение работает медленно и потребляет много ресурсов. Какие есть альтернативы или улучшения?",
            "Нужна помощь с архитектурным решением. Как лучше организовать код для этой задачи? Какие паттерны проектирования будут наиболее подходящими в данном случае?",
            "Возникла проблема с производительностью приложения. Как можно оптимизировать этот участок кода? Есть ли готовые решения или лучшие практики для подобных ситуаций?"
        ]
    def init_ui(self):
        dark_style = """
        QWidget {
            background-color: #181926;
            color: #e5e7ef;
        }
        QLabel {
            color: #e5e7ef;
        }
        QLineEdit, QSpinBox {
            background-color: #23243a;
            color: #e5e7ef;
            border: 1px solid #353657;
            border-radius: 6px;
            padding: 6px 8px;
            selection-background-color: #6366f1;
            selection-color: #fff;
        }
        QLineEdit:focus, QSpinBox:focus {
            border: 1.5px solid #6366f1;
        }
        QPushButton {
            background-color: #4f46e5;
            color: #fff;
            border-radius: 8px;
            padding: 10px 0;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #6366f1;
        }
        QFrame {
            background: #23243a;
            color: #e5e7ef;
        }
        QProgressBar {
            border: 1px solid #353657;
            border-radius: 5px;
            text-align: center;
            background-color: #23243a;
        }
        QProgressBar::chunk {
            background-color: #4f46e5;
            border-radius: 5px;
        }
        QProgressDialog {
            background: #181926;
            color: #e5e7ef;
        }
        QMessageBox {
            background: #23243a;
            color: #e5e7ef;
        }
        """
        self.setStyleSheet(dark_style)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        self.create_setup_screen()
        self.create_quiz_screen()
        self.stack.setCurrentIndex(0)
    def create_setup_screen(self):
        setup_widget = QWidget()
        layout = QVBoxLayout(setup_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        title = QLabel("Настройка GitHub Discussions")
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        instructions = QLabel(
            "1. Создайте новый репозиторий на GitHub\n"
            "2. Включите функцию Discussions в настройках репозитория:\n"
            "   • Перейдите в Settings > Features > Discussions\n"
            "   • Включите опцию и создайте категорию Q&A\n"
            "3. Введите путь к репозиторию и ваш токен GitHub"
        )
        instructions.setWordWrap(True)
        instructions.setFont(QFont('Arial', 12))
        layout.addWidget(instructions)
        repo_layout = QHBoxLayout()
        repo_label = QLabel("Репозиторий:")
        repo_label.setFont(QFont('Arial', 12))
        self.repo_input = QLineEdit()
        self.repo_input.setFont(QFont('Arial', 12))
        self.repo_input.setPlaceholderText("username/repo")
        repo_layout.addWidget(repo_label)
        repo_layout.addWidget(self.repo_input)
        layout.addLayout(repo_layout)
        token_layout = QHBoxLayout()
        token_label = QLabel("GitHub токен:")
        token_label.setFont(QFont('Arial', 12))
        self.user_token_input = QLineEdit()
        self.user_token_input.setFont(QFont('Arial', 12))
        self.user_token_input.setPlaceholderText("ghp_...")
        self.user_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.user_token_input)
        layout.addLayout(token_layout)
        continue_btn = QPushButton("Продолжить")
        continue_btn.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        continue_btn.setFixedHeight(50)
        continue_btn.clicked.connect(self.validate_repo_and_continue)
        layout.addWidget(continue_btn)
        self.stack.addWidget(setup_widget)
    def validate_repo_and_continue(self):
        repo_path = self.repo_input.text()
        user_token = self.user_token_input.text()
        if not repo_path:
            QMessageBox.warning(self, "Ошибка", "Введите путь к репозиторию")
            return
        if not user_token:
            QMessageBox.warning(self, "Ошибка", "Введите ваш токен GitHub")
            return
        try:
            owner, repo = repo_path.split('/')
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Репозиторий должен быть в формате owner/repo")
            return
        if not self.validate_repository(owner, repo):
            return
        self.user_token = user_token
        self.save_user_data()
        self.stack.setCurrentIndex(1)
    def validate_repository(self, owner, repo):
        token = self.user_token_input.text()
        headers = {
            'Authorization': f'bearer {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        try:
            query = """
            query {
              repository(owner: "%s", name: "%s") {
                id
                discussionCategories(first: 10) {
                  nodes {
                    id
                    name
                  }
                }
              }
            }
            """ % (owner, repo)
            response = requests.post(
                'https://api.github.com/graphql',
                json={'query': query},
                headers=headers
            )
            if response.status_code != 200:
                QMessageBox.warning(self, "Ошибка", f"Ошибка API: {response.status_code}. Проверьте токен и имя репозитория.")
                return False
            data = response.json()
            if 'errors' in data:
                QMessageBox.warning(self, "Ошибка", f"Ошибка GraphQL: {data['errors'][0]['message']}")
                return False
            categories = data.get('data', {}).get('repository', {}).get('discussionCategories', {}).get('nodes', [])
            if not categories:
                QMessageBox.warning(self, "Ошибка", "В репозитории не настроены категории обсуждений. Включите Discussions в настройках репозитория.")
                return False
            self.discussion_categories = categories
            QMessageBox.information(self, "Успех", f"Репозиторий проверен. Найдено {len(categories)} категорий обсуждений.")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при проверке репозитория: {str(e)}")
            return False
    def create_quiz_screen(self):
        quiz_widget = QWidget()
        layout = QVBoxLayout(quiz_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        title = QLabel("Получение GALAXY-BRAIN")
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        count_layout = QHBoxLayout()
        count_label = QLabel("Количество вопросов:")
        count_label.setFont(QFont('Arial', 12))
        self.count_input = NoArrowsSpinBox()
        self.count_input.setMinimum(1)
        self.count_input.setMaximum(100)
        self.count_input.setValue(5)
        self.count_input.setFont(QFont('Arial', 12))
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.count_input)
        layout.addLayout(count_layout)
        info_label = QLabel("Нажмите кнопку 'Начать', чтобы получить значок GALAXY-BRAIN.")
        info_label.setFont(QFont('Arial', 11))
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        progress_frame = QFrame()
        progress_frame.setFrameShape(QFrame.Shape.StyledPanel)
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setSpacing(15)
        stage1_layout = QHBoxLayout()
        self.stage1_label = QLabel("1. Создание вопросов")
        self.stage1_label.setFont(QFont('Arial', 11))
        self.stage1_progress = QProgressBar()
        self.stage1_progress.setFixedHeight(20)
        self.stage1_status = QLabel("⏳")
        self.stage1_status.setFont(QFont('Arial', 14))
        stage1_layout.addWidget(self.stage1_label, 3)
        stage1_layout.addWidget(self.stage1_progress, 6)
        stage1_layout.addWidget(self.stage1_status, 1)
        progress_layout.addLayout(stage1_layout)
        stage2_layout = QHBoxLayout()
        self.stage2_label = QLabel("2. Ответ на вопросы")
        self.stage2_label.setFont(QFont('Arial', 11))
        self.stage2_progress = QProgressBar()
        self.stage2_progress.setFixedHeight(20)
        self.stage2_status = QLabel("⏳")
        self.stage2_status.setFont(QFont('Arial', 14))
        stage2_layout.addWidget(self.stage2_label, 3)
        stage2_layout.addWidget(self.stage2_progress, 6)
        stage2_layout.addWidget(self.stage2_status, 1)
        progress_layout.addLayout(stage2_layout)
        stage3_layout = QHBoxLayout()
        self.stage3_label = QLabel("3. Подтверждение ответов")
        self.stage3_label.setFont(QFont('Arial', 11))
        self.stage3_progress = QProgressBar()
        self.stage3_progress.setFixedHeight(20)
        self.stage3_status = QLabel("⏳")
        self.stage3_status.setFont(QFont('Arial', 14))
        stage3_layout.addWidget(self.stage3_label, 3)
        stage3_layout.addWidget(self.stage3_progress, 6)
        stage3_layout.addWidget(self.stage3_status, 1)
        progress_layout.addLayout(stage3_layout)
        layout.addWidget(progress_frame)
        buttons_layout = QHBoxLayout()
        back_btn = QPushButton("Назад")
        back_btn.setFont(QFont('Arial', 12))
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.start_btn = QPushButton("Начать")
        self.start_btn.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        self.start_btn.setFixedHeight(50)
        self.start_btn.clicked.connect(self.start_quiz_process)
        self.exit_btn = QPushButton("Выйти")
        self.exit_btn.setFont(QFont('Arial', 12))
        self.exit_btn.clicked.connect(self.close)
        self.exit_btn.setVisible(False)
        buttons_layout.addWidget(back_btn)
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.exit_btn)
        layout.addLayout(buttons_layout)
        self.stack.addWidget(quiz_widget)
        self.reset_progress_bars()
    def reset_progress_bars(self):
        for progress_bar in [self.stage1_progress, self.stage2_progress, self.stage3_progress]:
            progress_bar.setValue(0)
            progress_bar.setMaximum(100)
        for status_label in [self.stage1_status, self.stage2_status, self.stage3_status]:
            status_label.setText("⏳")
    def start_quiz_process(self):
        self.start_btn.setEnabled(False)
        self.count_input.setEnabled(False)
        repo_path = self.repo_input.text()
        count = self.count_input.value()
        try:
            owner, repo = repo_path.split('/')
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Репозиторий должен быть в формате owner/repo")
            self.reset_quiz_controls()
            return
        self.create_qa_category(owner, repo)
        QTimer.singleShot(100, lambda: self.create_quiz_discussions(owner, repo, count))
    def create_qa_category(self, owner, repo):
        headers = {
            'Authorization': f'bearer {self.user_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        query = """
        query {
          repository(owner: "%s", name: "%s") {
            discussionCategories(first: 10) {
              nodes {
                id
                name
              }
            }
          }
        }
        """ % (owner, repo)
        try:
            response = requests.post(
                'https://api.github.com/graphql',
                json={'query': query},
                headers=headers
            )
            if response.status_code != 200:
                QMessageBox.critical(self, "Ошибка", f"Не удалось получить категории обсуждений. Статус: {response.status_code}")
                self.reset_quiz_controls()
                return
            data = response.json()
            if 'errors' in data:
                error_msg = data['errors'][0]['message'] if data['errors'] else "Неизвестная ошибка"
                QMessageBox.critical(self, "Ошибка", f"Ошибка GraphQL: {error_msg}")
                self.reset_quiz_controls()
                return
            categories = data.get('data', {}).get('repository', {}).get('discussionCategories', {}).get('nodes', [])
            qa_category = None
            for category in categories:
                if category['name'].lower() == 'q&a':
                    qa_category = category
                    break
            if not qa_category:
                self.create_category(owner, repo, "Q&A", "Вопросы и ответы")
            else:
                self.category_id = qa_category['id']
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить категории обсуждений: {str(e)}")
            self.reset_quiz_controls()
    def create_category(self, owner, repo, name, description):
        headers = {
            'Authorization': f'token {self.user_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        repo_query = """
        query {
          repository(owner: "%s", name: "%s") {
            id
          }
        }
        """ % (owner, repo)
        try:
            repo_response = requests.post(
                'https://api.github.com/graphql',
                json={'query': repo_query},
                headers=headers
            )
            if repo_response.status_code != 200:
                QMessageBox.critical(self, "Ошибка", f"Не удалось получить ID репозитория. Статус: {repo_response.status_code}")
                self.reset_quiz_controls()
                return
            response_data = repo_response.json()
            if 'errors' in response_data:
                error_msg = response_data['errors'][0]['message'] if response_data['errors'] else "Неизвестная ошибка"
                QMessageBox.critical(self, "Ошибка", f"Ошибка GraphQL: {error_msg}")
                self.reset_quiz_controls()
                return
            repo_id = response_data.get('data', {}).get('repository', {}).get('id')
            if not repo_id:
                QMessageBox.critical(self, "Ошибка", "ID репозитория не найден в ответе")
                self.reset_quiz_controls()
                return
            author_headers = {
                'Authorization': f'token {self.author_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            mutation = """
            mutation {
              createDiscussionCategory(input: {
                repositoryId: "%s",
                name: "%s",
                description: "%s",
                emoji: "❓"
              }) {
                category {
                  id
                }
              }
            }
            """ % (repo_id, name, description)
            category_response = requests.post(
                'https://api.github.com/graphql',
                json={'query': mutation},
                headers=author_headers
            )
            if category_response.status_code != 200:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать категорию. Статус: {category_response.status_code}")
                self.reset_quiz_controls()
                return
            category_data = category_response.json()
            if 'errors' in category_data:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать категорию: {category_data['errors'][0]['message']}")
                self.reset_quiz_controls()
                return
            self.category_id = category_data.get('data', {}).get('createDiscussionCategory', {}).get('category', {}).get('id')
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании категории: {str(e)}")
            self.reset_quiz_controls()
    def reset_quiz_controls(self):
        self.start_btn.setEnabled(True)
        self.count_input.setEnabled(True)
        self.reset_progress_bars()
    def create_quiz_discussions(self, owner, repo, count):
        repo_id = self.get_repository_id_for_quiz(owner, repo)
        if not repo_id:
            self.reset_quiz_controls()
            return
        created_discussions = []
        for i in range(count):
            progress = int((i / count) * 100)
            self.stage1_progress.setValue(progress)
            QApplication.processEvents()
            title = self.get_random_title()
            body = self.get_random_body()
            if count > 1:
                title = f"{title} #{i+1}"
            discussion_url = self.create_single_discussion_for_quiz(repo_id, self.category_id, body, title)
            if discussion_url:
                created_discussions.append({"title": title, "url": discussion_url})
            for _ in range(5):
                QApplication.processEvents()
                QTimer.singleShot(50, lambda: None)
        self.stage1_progress.setValue(100)
        self.stage1_status.setText("✅")
        self.created_discussions = created_discussions
        QTimer.singleShot(500, lambda: self.reply_to_quiz_discussions(owner, repo))
    def get_repository_id_for_quiz(self, owner, repo):
        headers = {
            'Authorization': f'token {self.user_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        repo_query = """
        query {
          repository(owner: "%s", name: "%s") {
            id
          }
        }
        """ % (owner, repo)
        try:
            repo_response = requests.post(
                'https://api.github.com/graphql',
                json={'query': repo_query},
                headers=headers
            )
            if repo_response.status_code != 200:
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить ID репозитория. Статус: {repo_response.status_code}")
                return None
            response_data = repo_response.json()
            if 'errors' in response_data:
                error_msg = response_data['errors'][0]['message'] if response_data['errors'] else "Неизвестная ошибка"
                QMessageBox.warning(self, "Ошибка", f"Ошибка GraphQL: {error_msg}")
                return None
            repo_id = response_data.get('data', {}).get('repository', {}).get('id')
            if not repo_id:
                QMessageBox.warning(self, "Ошибка", "ID репозитория не найден в ответе")
                return None
            return repo_id
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при получении ID репозитория: {str(e)}")
            return None
    def create_single_discussion_for_quiz(self, repo_id, category_id, body, title):
        headers = {
            'Authorization': f'token {self.author_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        mutation = """
        mutation {
          createDiscussion(input: {
            repositoryId: "%s",
            categoryId: "%s",
            body: "%s",
            title: "%s"
          }) {
            discussion {
              id
              url
            }
          }
        }
        """
        try:
            escaped_body = body.replace('"', '\\"').replace('\n', '\\n')
            escaped_title = title.replace('"', '\\"')
            final_mutation = mutation % (repo_id, category_id, escaped_body, escaped_title)
            discussion_response = requests.post(
                'https://api.github.com/graphql',
                json={'query': final_mutation},
                headers=headers
            )
            response_data = discussion_response.json()
            if discussion_response.status_code == 200 and 'errors' not in response_data:
                url = response_data.get('data', {}).get('createDiscussion', {}).get('discussion', {}).get('url')
                return url
            else:
                return None
        except Exception:
            return None
    def reply_to_quiz_discussions(self, owner, repo):
        discussions = self.get_discussions_for_quiz(self.user_token, owner, repo)
        if not discussions:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить список обсуждений")
            self.reset_quiz_controls()
            return
        count_success = 0
        total = len(discussions)
        for i, discussion in enumerate(discussions):
            progress = int((i / total) * 100)
            self.stage2_progress.setValue(progress)
            QApplication.processEvents()
            discussion_id = discussion.get('id')
            success = self.add_comment_to_quiz(self.user_token, discussion_id, "1")
            if success:
                count_success += 1
            for _ in range(3):
                QApplication.processEvents()
                QTimer.singleShot(50, lambda: None)
        self.stage2_progress.setValue(100)
        self.stage2_status.setText("✅")
        QTimer.singleShot(500, lambda: self.mark_quiz_answers(owner, repo))
    def get_discussions_for_quiz(self, token, owner, repo):
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        query = """
        query {
          repository(owner: "%s", name: "%s") {
            discussions(first: 50) {
              nodes {
                id
                title
                url
              }
            }
          }
        }
        """ % (owner, repo)
        try:
            response = requests.post(
                'https://api.github.com/graphql',
                json={'query': query},
                headers=headers
            )
            if response.status_code != 200:
                return []
            data = response.json()
            if 'errors' in data:
                return []
            discussions = data.get('data', {}).get('repository', {}).get('discussions', {}).get('nodes', [])
            return discussions
        except Exception:
            return []
    def add_comment_to_quiz(self, token, discussion_id, body):
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        mutation = """
        mutation {
          addDiscussionComment(input: {
            discussionId: "%s",
            body: "%s"
          }) {
            comment {
              id
            }
          }
        }
        """ % (discussion_id, body)
        try:
            response = requests.post(
                'https://api.github.com/graphql',
                json={'query': mutation},
                headers=headers
            )
            if response.status_code != 200:
                return False
            data = response.json()
            if 'errors' in data:
                return False
            return True
        except Exception:
            return False
    def mark_quiz_answers(self, owner, repo):
        print(f"Начинаем подтверждение ответов для {owner}/{repo}")
        discussions = self.get_discussions_with_comments_for_quiz(owner, repo)
        print(f"Получено обсуждений: {len(discussions) if discussions else 0}")
        if not discussions:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить список обсуждений с комментариями")
            self.reset_quiz_controls()
            return
        discussions = [d for d in discussions if d.get('comments', {}).get('totalCount', 0) > 0]
        print(f"Обсуждений с комментариями: {len(discussions)}")
        count_success = 0
        total = len(discussions)
        for i, discussion in enumerate(discussions):
            progress = int((i / total) * 100)
            self.stage3_progress.setValue(progress)
            QApplication.processEvents()
            discussion_number = discussion.get('number')
            print(f"Обрабатываем обсуждение #{discussion_number}")
            if discussion.get('answerChosenAt'):
                print(f"Обсуждение #{discussion_number} уже имеет выбранный ответ")
                continue
            comments = self.get_discussion_comments_for_quiz(owner, repo, discussion_number)
            print(f"Получено комментариев для обсуждения #{discussion_number}: {len(comments) if comments else 0}")
            if not comments or len(comments) == 0:
                print(f"Нет комментариев для обсуждения #{discussion_number}")
                continue
            first_comment = comments[0]
            comment_id = first_comment.get('id')
            if not comment_id:
                print(f"Нет ID комментария для обсуждения #{discussion_number}")
                continue
            print(f"Подтверждаем комментарий {comment_id} для обсуждения #{discussion_number}")
            success = self.mark_comment_as_answer_for_quiz(comment_id)
            if success:
                count_success += 1
                print(f"Успешно подтвержден комментарий для обсуждения #{discussion_number}")
            else:
                print(f"Не удалось подтвердить комментарий для обсуждения #{discussion_number}")
            for _ in range(3):
                QApplication.processEvents()
                QTimer.singleShot(50, lambda: None)
        print(f"Всего подтверждено ответов: {count_success} из {total}")
        self.stage3_progress.setValue(100)
        self.stage3_status.setText("✅")
        QTimer.singleShot(500, self.complete_quiz_process)
    def get_discussions_with_comments_for_quiz(self, owner, repo):
        headers = {
            'Authorization': f'bearer {self.user_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        query = """
        query {
          repository(owner: "%s", name: "%s") {
            discussions(first: 50) {
              nodes {
                id
                number
                title
                url
                answerChosenAt
                comments(first: 1) {
                  totalCount
                }
              }
            }
          }
        }
        """ % (owner, repo)
        try:
            response = requests.post(
                'https://api.github.com/graphql',
                json={'query': query},
                headers=headers
            )
            if response.status_code != 200:
                print(f"Ошибка получения обсуждений: статус {response.status_code}")
                return []
            data = response.json()
            if 'errors' in data:
                error_msg = data['errors'][0]['message'] if data['errors'] else "Неизвестная ошибка"
                print(f"Ошибка GraphQL при получении обсуждений: {error_msg}")
                return []
            discussions = data.get('data', {}).get('repository', {}).get('discussions', {}).get('nodes', [])
            return discussions
        except Exception as e:
            print(f"Исключение при получении обсуждений: {str(e)}")
            return []
    def get_discussion_comments_for_quiz(self, owner, repo, discussion_number):
        headers = {
            'Authorization': f'bearer {self.user_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        query = """
        query {
          repository(owner: "%s", name: "%s") {
            discussion(number: %s) {
              comments(first: 10) {
                nodes {
                  id
                  author {
                    login
                  }
                  createdAt
                  body
                }
              }
            }
          }
        }
        """ % (owner, repo, discussion_number)
        try:
            response = requests.post(
                'https://api.github.com/graphql',
                json={'query': query},
                headers=headers
            )
            if response.status_code != 200:
                print(f"Ошибка получения комментариев: статус {response.status_code}")
                return []
            data = response.json()
            if 'errors' in data:
                error_msg = data['errors'][0]['message'] if data['errors'] else "Неизвестная ошибка"
                print(f"Ошибка GraphQL при получении комментариев: {error_msg}")
                return []
            comments = data.get('data', {}).get('repository', {}).get('discussion', {}).get('comments', {}).get('nodes', [])
            return comments
        except Exception as e:
            print(f"Исключение при получении комментариев: {str(e)}")
            return []
    def mark_comment_as_answer_for_quiz(self, comment_id):
        if not comment_id:
            return False
        headers = {
            'Authorization': f'bearer {self.author_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        mutation = """
        mutation MarkAnswer($commentId: ID!) {
          markDiscussionCommentAsAnswer(input: {
            id: $commentId
          }) {
            discussion {
              id
            }
          }
        }
        """
        variables = {
            "commentId": comment_id
        }
        try:
            response = requests.post(
                'https://api.github.com/graphql',
                json={
                    'query': mutation,
                    'variables': variables
                },
                headers=headers
            )
            if response.status_code != 200:
                return False
            data = response.json()
            if 'errors' in data:
                return False
            return True
        except Exception:
            return False
    def complete_quiz_process(self):
        QMessageBox.information(self, "Готово", "Значок GALAXY-BRAIN получен!")
        self.start_btn.setVisible(False)
        self.exit_btn.setVisible(True)
        self.count_input.setEnabled(True)
    def get_random_title(self):
        return random.choice(self.random_titles)
    def get_random_body(self):
        return random.choice(self.random_bodies)
    def load_user_data(self):
        if not os.path.exists(self.config_file):
            self.create_default_user_data()
            return
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if 'repository' in config:
                self.repo_input.setText(config.get('repository', ''))
            if 'user_token' in config:
                self.user_token_input.setText(config.get('user_token', ''))
                self.user_token = config.get('user_token', '')
        except Exception as e:
            print(f'Не удалось загрузить данные пользователя: {str(e)}')
    def create_default_user_data(self):
        default_data = {
            'user_token': '',
            'repository': ''
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False)
        except Exception as e:
            print(f'Не удалось создать файл с данными пользователя: {str(e)}')
    def save_user_data(self):
        config = {
            'user_token': self.user_token,
            'repository': self.repo_input.text()
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False)
        except Exception as e:
            print(f'Не удалось сохранить данные пользователя: {str(e)}')
    def closeEvent(self, event):
        self.save_user_data()
        event.accept()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GitHubDiscussionsApp()
    window.show()
    sys.exit(app.exec()) 