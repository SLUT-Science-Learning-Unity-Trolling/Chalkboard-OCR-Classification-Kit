from graphviz import Digraph

# Создаём диаграмму
dot = Digraph("AutoConspectsExtended", format="png")
dot.attr(rankdir="LR", bgcolor="mintcream", fontsize="12")

# Узлы
dot.node("Client", "Клиент\n(браузер / мобильное приложение)", shape="rect", style="filled", color="lightgreen")
dot.node("API", "API / Backend\n(FastAPI, Auth)", shape="rect", style="filled", color="palegreen")
dot.node("Queue", "Очередь задач\n(Celery, Redis/RabbitMQ)", shape="rect", style="filled", color="lightyellow")
dot.node("Processor", "Сервис обработки\n(OpenCV, img2latex,\nгенерация PDF)", shape="rect", style="filled", color="khaki")
dot.node("Storage", "Файловое хранилище\n(S3 / MinIO / локально)", shape="rect", style="filled", color="lightskyblue")
dot.node("DB", "База данных\n(пользователи, метаданные,\nссылки на файлы)", shape="rect", style="filled", color="lightgreen")

# Стрелки
dot.edge("Client", "API", label="Запрос (картинка)")
dot.edge("API", "Queue", label="Отправка задачи")
dot.edge("Queue", "Processor", label="Взятие задачи")
dot.edge("Processor", "Storage", label="Сохраняет PDF")
dot.edge("Processor", "DB", label="Метаданные, ссылка на файл")
dot.edge("API", "DB", label="Регистрация, аутентификация")
dot.edge("Client", "API", label="Запрос PDF", dir="both")
dot.edge("API", "Storage", label="Выдача PDF клиенту")

# Сохраняем и отображаем
output_path = "./diagram/outputs/tech_architecture_diagram"
dot.render(output_path, cleanup=True)
