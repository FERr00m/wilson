"""
tool_composer.py — атомарный связующий слой для инструментов и бюджетной логики
Снижает связность через трёхосевой фильтр validate_model_advice()
"""

from .tool_executor import ToolExecutor
from .budget_tracker import BudgetTracker

class ToolComposer:
    def __init__(self, executor: ToolExecutor, tracker: BudgetTracker):
        self.executor = executor
        self.tracker = tracker

    def validate_model_advice(self, advice: dict) -> bool:
        """
        Трёхосевая проверка рекомендаций моделей
        """
        # Техническая ось: проверка на соответствие минимализму
        technical_ok = advice.get('technical_score', 0) >= 0.7
        # Когнитивная ось: проверка логической целостности
        cognitive_ok = advice.get('cognitive_consistency', False)
        # Экзистенциальная ось: защита core-файлов
        existential_ok = not advice.get('core_files_modified', False)
        
        return all([technical_ok, cognitive_ok, existential_ok])

    def execute(self, tool_name, *args, **kwargs):
        """Безопасный запуск инструмента с проверкой бюджета и советов"""
        # Проверка бюджета
        if not self.tracker.validate_budget():
            return {"error": "Budget exceeded"}
        
        # Получение совета от модели (здесь упрощённый пример)
        advice = self.tracker.get_budget_advice()
        
        # Критическая оценка через трёхосевой фильтр
        if not self.validate_model_advice(advice):
            # Если совет не проходит проверку — откатываемся к безопасному сценарию
            return self.tracker.fallback_execution()
        
        return self.executor.execute(tool_name, *args, **kwargs)