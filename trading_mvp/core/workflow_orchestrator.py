#!/usr/bin/env python3
"""
Workflow Orchestrator: Ejecución determinista con fail-fast y logging estructurado

GARANTÍAS:
- Fail-fast: Si cualquier paso falla, se detiene la ejecución
- Logging completo: Cada paso queda registrado con timestamps
- No silent failures: Todos los errores son explícitos
- Datos frescos: Paso 0 garantiza noticias recientes antes de operar
"""

import os
import logging
import json
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Estados del workflow."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(Enum):
    """Tipos de pasos del workflow."""
    NEWS_EXTRACTION = "news_extraction"
    DATA_VALIDATION = "data_validation"
    TICKER_ANALYSIS = "ticker_analysis"
    AGGREGATION = "aggregation"
    DECISION_ENGINE = "decision_engine"
    ORDER_EXECUTION = "order_execution"
    PERSISTENCE = "persistence"


@dataclass
class WorkflowStep:
    """Registro de un paso del workflow."""
    step_id: str
    step_type: str
    status: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    input_data: Optional[Dict] = None
    output_data: Optional[Dict] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    metadata: Optional[Dict] = None

    def to_dict(self):
        """Convertir a dict para JSON serialization."""
        return asdict(self)


class WorkflowLogger:
    """Sistema de logging estructurado para ejecuciones."""

    def __init__(self, retention_hours: int = 72):
        """Initialize workflow logger.

        Args:
            retention_hours: Horas a retener logs (default: 72)
        """
        self.retention_hours = retention_hours
        self.log_dir = "logs/workflow_executions"
        os.makedirs(self.log_dir, exist_ok=True)

        # Crear logger específico
        self.logger = logging.getLogger("workflow_logger")
        self.logger.setLevel(logging.DEBUG)

        # File handler con rotación
        from logging.handlers import TimedRotatingFileHandler
        log_file = os.path.join(self.log_dir, "workflow.log")

        handler = TimedRotatingFileHandler(
            log_file,
            when='H',  # Rotar cada hora
            interval=1,
            backupCount=retention_hours  # Mantener 72 archivos
        )
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Console handler para visibility
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log_step_start(
        self,
        step_id: str,
        step_type: StepType,
        input_data: Dict = None
    ) -> WorkflowStep:
        """Registrar inicio de un paso.

        Args:
            step_id: Identificador único del paso
            step_type: Tipo de paso
            input_data: Datos de entrada

        Returns:
            WorkflowStep inicializado
        """
        step = WorkflowStep(
            step_id=step_id,
            step_type=step_type.value,
            status=WorkflowStatus.IN_PROGRESS.value,
            start_time=datetime.now().isoformat(),
            input_data=input_data,
            metadata={}
        )

        self.logger.info(f"🚀 STEP START: {step_type.value} [{step_id}]")
        if input_data:
            self.logger.debug(f"   Input: {json.dumps(input_data, indent=2, default=str)[:500]}")

        return step

    def log_step_complete(
        self,
        step: WorkflowStep,
        output_data: Dict = None
    ) -> WorkflowStep:
        """Registrar completado de un paso.

        Args:
            step: WorkflowStep actual
            output_data: Datos de salida

        Returns:
            WorkflowStep actualizado
        """
        step.status = WorkflowStatus.COMPLETED.value
        step.end_time = datetime.now().isoformat()
        step.output_data = output_data

        start_dt = datetime.fromisoformat(step.start_time)
        end_dt = datetime.fromisoformat(step.end_time)
        step.duration_seconds = (end_dt - start_dt).total_seconds()

        self.logger.info(
            f"✅ STEP COMPLETE: {step.step_type} [{step.step_id}] "
            f"({step.duration_seconds:.2f}s)"
        )
        if output_data:
            self.logger.debug(f"   Output: {json.dumps(output_data, indent=2, default=str)[:500]}")

        return step

    def log_step_failure(
        self,
        step: WorkflowStep,
        error: Exception,
        context: Dict = None
    ) -> WorkflowStep:
        """Registrar falla de un paso.

        Args:
            step: WorkflowStep actual
            error: Excepción ocurrida
            context: Contexto adicional

        Returns:
            WorkflowStep marcado como fallido
        """
        import traceback

        step.status = WorkflowStatus.FAILED.value
        step.end_time = datetime.now().isoformat()
        step.error_message = str(error)
        step.error_traceback = traceback.format_exc()
        step.metadata = context or {}

        start_dt = datetime.fromisoformat(step.start_time)
        end_dt = datetime.fromisoformat(step.end_time)
        step.duration_seconds = (end_dt - start_dt).total_seconds()

        self.logger.error(
            f"❌ STEP FAILED: {step.step_type} [{step.step_id}] "
            f"({step.duration_seconds:.2f}s)"
        )
        self.logger.error(f"   Error: {step.error_message}")
        self.logger.debug(f"   Traceback:\n{step.error_traceback}")

        return step

    def save_execution_log(self, execution_id: str, steps: List[WorkflowStep]):
        """Guardar log completo de ejecución a disco.

        Args:
            execution_id: ID único de la ejecución
            steps: Lista de pasos ejecutados
        """
        log_file = os.path.join(
            self.log_dir,
            f"execution_{execution_id}.json"
        )

        execution_log = {
            'execution_id': execution_id,
            'start_time': steps[0].start_time if steps else None,
            'end_time': steps[-1].end_time if steps else None,
            'total_duration_seconds': sum(
                s.duration_seconds for s in steps if s.duration_seconds
            ),
            'total_steps': len(steps),
            'completed_steps': len([s for s in steps if s.status == WorkflowStatus.COMPLETED.value]),
            'failed_steps': len([s for s in steps if s.status == WorkflowStatus.FAILED.value]),
            'steps': [s.to_dict() for s in steps]
        }

        with open(log_file, 'w') as f:
            json.dump(execution_log, f, indent=2, default=str)

        self.logger.info(f"💾 Execution log saved: {log_file}")

    def cleanup_old_logs(self):
        """Eliminar logs más antiguos que retention_hours."""
        cutoff = datetime.now() - timedelta(hours=self.retention_hours)

        for filename in os.listdir(self.log_dir):
            if filename.startswith('execution_') and filename.endswith('.json'):
                filepath = os.path.join(self.log_dir, filename)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))

                if file_mtime < cutoff:
                    os.remove(filepath)
                    self.logger.info(f"🗑️  Cleaned up old log: {filename}")


class WorkflowOrchestrator:
    """Orquestador de workflow con fail-fast y logging completo."""

    def __init__(self, retention_hours: int = 72):
        """Initialize workflow orchestrator.

        Args:
            retention_hours: Horas a retener logs
        """
        self.workflow_logger = WorkflowLogger(retention_hours)
        self.execution_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.steps: List[WorkflowStep] = []

    def execute_step(
        self,
        step_type: StepType,
        step_function: Callable,
        step_id: str = None,
        input_data: Dict = None,
        fail_fast: bool = True
    ) -> Dict:
        """Ejecutar un paso con logging y error handling.

        Args:
            step_type: Tipo de paso
            step_function: Función a ejecutar (debe retornar Dict)
            step_id: ID único (auto-generado si no provisto)
            input_data: Datos de entrada para la función
            fail_fast: Si True, lanza excepción en caso de error

        Returns:
            Dict con output_data

        Raises:
            Exception: Si fail_fast=True y el paso falla
        """
        if not step_id:
            step_id = f"{step_type.value}_{len(self.steps)+1}"

        # Registrar inicio
        step = self.workflow_logger.log_step_start(
            step_id=step_id,
            step_type=step_type,
            input_data=input_data
        )

        try:
            # Ejecutar función
            if input_data:
                output_data = step_function(**input_data)
            else:
                output_data = step_function()

            # Validar output
            if not isinstance(output_data, dict):
                raise ValueError(
                    f"Step function must return dict, got {type(output_data)}"
                )

            # Validar éxito explícito
            if output_data.get('success') is False:
                error_msg = output_data.get('error', 'Unknown error')
                raise ValueError(f"Step returned success=False: {error_msg}")

            # Registrar completado
            step = self.workflow_logger.log_step_complete(
                step=step,
                output_data=output_data
            )
            self.steps.append(step)

            return output_data

        except Exception as e:
            # Registrar falla
            step = self.workflow_logger.log_step_failure(
                step=step,
                error=e,
                context={'input_data': input_data}
            )
            self.steps.append(step)

            # Guardar log parcial
            self.workflow_logger.save_execution_log(
                self.execution_id,
                self.steps
            )

            if fail_fast:
                # CRÍTICO: Detener ejecución inmediatamente
                self.workflow_logger.logger.error(
                    f"🛑 WORKFLOW ABORTED at step: {step_type.value}"
                )
                raise
            else:
                # Retornar output con error
                return {
                    'success': False,
                    'error': str(e),
                    'step_id': step_id,
                    'traceback': step.error_traceback
                }

    def finalize_execution(self):
        """Finalizar ejecución y guardar log completo."""
        self.workflow_logger.save_execution_log(
            self.execution_id,
            self.steps
        )
        self.workflow_logger.cleanup_old_logs()

        # Resumen
        completed = len([s for s in self.steps if s.status == WorkflowStatus.COMPLETED.value])
        failed = len([s for s in self.steps if s.status == WorkflowStatus.FAILED.value])

        self.workflow_logger.logger.info(
            f"📊 WORKFLOW COMPLETE: {completed} steps completed, {failed} failed"
        )


def create_workflow_orchestrator(retention_hours: int = 72) -> WorkflowOrchestrator:
    """Factory function para crear orquestador.

    Args:
        retention_hours: Horas a retener logs (default: 72)

    Returns:
        WorkflowOrchestrator configurado
    """
    return WorkflowOrchestrator(retention_hours=retention_hours)
