from graphviz import Digraph

dot = Digraph("BusinessLogic", format="png")
dot.attr(rankdir="TB", bgcolor="mintcream", fontsize="12")

# Узлы
dot.node("Start", "Пользователь загружает фото\n(доски / презентации)", shape="ellipse", style="filled", color="lightgreen")
dot.node("Auth", "Авторизация / регистрация", shape="diamond", style="filled", color="palegreen")
dot.node("QueueTask", "Формирование задачи\nна обработку", shape="rect", style="filled", color="lightyellow")
dot.node("Processing", "Обработка изображения:\n- OpenCV: выделение текста\n- img2latex: формулы\n- OCR: текст\n- Сбор в конспект", shape="rect", style="filled", color="khaki")
dot.node("PDFGen", "Генерация PDF конспекта", shape="rect", style="filled", color="khaki")
dot.node("Save", "Сохранение результата\n(файл + метаданные)", shape="rect", style="filled", color="lightskyblue")
dot.node("Notify", "Уведомление пользователя\nо готовности", shape="rect", style="filled", color="lightblue")
dot.node("Download", "Пользователь скачивает PDF", shape="ellipse", style="filled", color="lightgreen")

# Стрелки
dot.edge("Start", "Auth", label="Проверка пользователя")
dot.edge("Auth", "QueueTask", label="OK")
dot.edge("QueueTask", "Processing", label="Передача задачи")
dot.edge("Processing", "PDFGen", label="Результат обработки")
dot.edge("PDFGen", "Save", label="Сохранение")
dot.edge("Save", "Notify", label="Ссылка на PDF")
dot.edge("Notify", "Download", label="Запрос PDF")

# Сохраняем
output_path = "./diagram/outputs/business_logic_diagram"
dot.render(output_path, cleanup=True)
