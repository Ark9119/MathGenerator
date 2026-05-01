import pytest
from ..algoritm.main_algoritm import main, generate_all_examples


@pytest.fixture
def valid_kwargs():
    """Фикстура с валидными настройками"""
    return {
        'number_of_numbers': 2,
        'znak_operacii': ['+'],      # Лучше передавать список знаков
        'number_of_examples': 5,     # Меньше примеров для скорости тестов
        'rules': ['not_negative'],   # Обязательно список!
        'min_number': 0,
        'max_number': 10
    }


# 1️⃣ Тест бизнес-логики (рекомендуемый подход)
def test_generate_examples_respects_rules(valid_kwargs):
    """Проверяем, что генератор создаёт
    нужное количество примеров и соблюдает правила
    """
    examples, answers = generate_all_examples(
        valid_kwargs['number_of_numbers'],
        valid_kwargs['znak_operacii'],
        valid_kwargs['number_of_examples'],
        valid_kwargs['rules'],
        valid_kwargs['min_number'],
        valid_kwargs['max_number']
    )

    # Проверяем количество
    assert len(examples) == valid_kwargs['number_of_examples']
    assert len(answers) == valid_kwargs['number_of_examples']

    # Проверяем правило not_negative
    if 'not_negative' in valid_kwargs['rules']:
        for ans in answers:
            assert isinstance(
                ans, (int, float)
            ), f"Ответ должен быть числом, получено: {type(ans)}"
            assert ans >= 0, f"Нарушено правило not_negative. Ответ: {ans}"


# 2️⃣ Тест функции main (побочные эффекты + файлы)
def test_main_creates_correct_files(valid_kwargs, tmp_path, monkeypatch):
    """Проверяем, что main создаёт файлы в нужном формате"""
    # Перенаправляем рабочую директорию во временную папку pytest
    monkeypatch.chdir(tmp_path)

    # Вызываем main с распаковкой словаря
    main(**valid_kwargs)

    # Проверяем создание файлов
    assert (tmp_path / "examples.txt").exists()
    assert (tmp_path / "answers.txt").exists()
    assert (tmp_path / "examples.docx").exists()
    assert (tmp_path / "answers.docx").exists()

    # Проверяем содержимое текстовых файлов
    examples_text = (tmp_path / "examples.txt").read_text(encoding="utf-8")
    lines = [line for line in examples_text.strip().split("\n") if line.strip()]
    assert len(lines) == valid_kwargs['number_of_examples']

    # Проверяем формат строк (должны начинаться с "1) ", "2) " и т.д.)
    for i, line in enumerate(lines, 1):
        assert line.startswith(
            f"{i}) "
        ), f"Неверный формат строки примера: {line}"
