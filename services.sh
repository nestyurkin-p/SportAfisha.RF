#!/bin/bash

# Скрипт находит все файлы compose.yaml в директориях верхнего уровня, собирает
# их в массив и запускает docker compose с аргументами, переданными в скрипт
#
# Также запускает главный compose в корне проекта c переданными параметрами

# Проверяем, переданы ли аргументы
if [ $# -eq 0 ]; then
    echo "Использование: $0 <docker-compose-arguments>"
    echo "Пример: $0 up -d"
    exit 1
fi

# Находим все compose.yaml в директориях верхнего уровня
compose_files=(./compose.yaml $(find . -mindepth 2 -maxdepth 2 -name "compose.yaml" -print))

# Проверяем, найдены ли файлы
if [ ${#compose_files[@]} -eq 0 ]; then
    echo "compose.yaml файлы не найдены."
    exit 1
fi

# Итерируем по массиву и выполняем docker compose с переданными аргументами
for compose_file in "${compose_files[@]}"; do
    dir=$(dirname "$compose_file")
    echo "Запуск docker compose $* в директории $dir"
    (cd "$dir" && docker compose "$@")
done
