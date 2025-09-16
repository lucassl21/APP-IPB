from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import datetime

# --- Modelos de Banco de Dados ---

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    senha: str
    nome_completo: Optional[str] = None
    estado_civil: Optional[bool] = None
    numero_filhos: Optional[int] = None
    telefone: Optional[str] = None
    cidade: Optional[str] = None
    bairro: Optional[str] = None
    rua: Optional[str] = None
    numero: Optional[str] = None
    cpf: str = Field(unique=True, index=True)
    tipo_usuario: Optional[str] = None
    
    solicitacoes: List["Solicitacao"] = Relationship(back_populates="usuario")

class Solicitacao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    data_solicitacao: datetime = Field(default_factory=datetime.now)
    tipo_solicitacao: str
    status: str
    descricao: str
    cpf_usuario: str
    
    usuario_id: Optional[int] = Field(default=None, foreign_key="user.id")
    usuario: Optional["User"] = Relationship(back_populates="solicitacoes")

# --- Modelos de Requisição (sem tabela) ---

class UserFirstStage(BaseModel):
    email: EmailStr
    cpf: str
    senha: str

class UserSecondStage(BaseModel):
    nome_completo: str
    estado_civil: bool
    numero_filhos: int
    telefone: Optional[str] = None
    cidade: str
    bairro: str
    rua: str
    numero: str

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class UserForgotPassword(BaseModel):
    email: EmailStr

class AdminLogin(BaseModel):
    email: EmailStr
    senha: str

class AdminForgotPassword(BaseModel):
    email: EmailStr

class AdminPasswordReset(BaseModel):
    codigo: str
    nova_senha: str

class TipoDoacao(str, Enum):
    dinheiro = "dinheiro"
    roupas_cobertas = "roupas_cobertas"
    alimentos = "alimentos"
    outros = "outros"

class TipoSolicitacao(str, Enum):
    doacao = "doacao"
    beneficio = "beneficio"
    oracao = "oracao"

class DoadorInfo(BaseModel):
    tipo_doacao: TipoDoacao
    descricao: str

class BeneficiarioInfo(BaseModel):
    historia_de_vida: str

class OracaoInfo(BaseModel):
    descricao: str

class UserTypeChoice(BaseModel):
    tipo_usuario: str

class StatusSolicitacao(str, Enum):
    andamento = "andamento"
    pendente = "pendente"
    concluido = "concluido"

class SolicitacaoUpdate(BaseModel):
    novo_status: StatusSolicitacao

class PasswordReset(BaseModel):
    token: str
    nova_senha: str