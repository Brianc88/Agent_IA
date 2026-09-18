"""
Modelos de dominio — representan conceptos de negocio puros.
Usan Pydantic porque estos datos cruzan fronteras: vienen de SQL Server
y del LLM, y salen hacia el LLM como resultados.
"""

from enum import Enum

from pydantic import BaseModel, Field


class NivelRiesgo(str, Enum):
    SOLO_LECTURA = "solo_lectura"
    ESCRITURA = "escritura"


class EstadoIndicador(str, Enum):
    BORRADOR = "borrador"
    APROBADO = "aprobado"
    OBSOLETO = "obsoleto"


class ParametroIndicador(BaseModel):
    nombre: str
    tipo_dato: str
    requerido: bool
    orden: int
    ejemplo: str | None = None


class Indicador(BaseModel):
    id: int
    nombre_sp: str
    descripcion: str
    nivel_riesgo: NivelRiesgo
    estado: EstadoIndicador
    timeout_segundos: int
    max_filas_retorno: int
    ejemplos_preguntas: list[str] = Field(default_factory=list)
    parametros: list[ParametroIndicador] = Field(default_factory=list)

    def es_ejecutable(self) -> bool:
        """Regla de negocio: solo se puede ejecutar si está aprobado."""
        return self.estado == EstadoIndicador.APROBADO