from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from passlib.context import CryptContext
from sqlmodel import SQLModel, create_engine, Session, select
import uuid
from models import (
    User,
    UserFirstStage,
    UserSecondStage,
    UserLogin,
    UserForgotPassword,
    AdminLogin,
    AdminForgotPassword,
    AdminPasswordReset,
    TipoDoacao,
    TipoSolicitacao,
    DoadorInfo,
    BeneficiarioInfo,
    OracaoInfo,
    UserTypeChoice,
    Solicitacao,
    StatusSolicitacao,
    SolicitacaoUpdate,
    PasswordReset
)

# --- Configurações do Banco de Dados ---

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- Lógica de Segurança e Senha ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- Simulação de Dados em Memória ---
# ALERTA: Mantenha esta senha em sigilo.
# Substitua o e-mail e a senha abaixo pelos seus dados de administrador.
admin_email_padrao = "admin@igreja.com"
admin_senha_padrao = get_password_hash("senha123")
senha_recuperacao: Dict[str, str] = {}

# --- Informação da Igreja ---
chave_pix_igreja = "CNPJ 22.191.725/0001-47 (Ccla De Pitangui E Regiao Ltda)"

# --- Configuração da Aplicação ---

app = FastAPI()

# Configuração do CORS para permitir a conexão do frontend
origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://seu-app-do-netlify.netlify.app", # SUBSTITUA PELA SUA URL REAL DO NETLIFY
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- Endpoints de Cadastro em Duas Etapas ---

@app.post("/users/register-first-stage")
def register_first_stage(user_data: UserFirstStage, session: Session = Depends(get_session)):
    cpf = user_data.cpf.replace('.', '').replace('-', '')
    
    user_existente = session.exec(select(User).where(User.cpf == cpf)).first()
    if user_existente:
        raise HTTPException(status_code=400, detail="Já existe um cadastro com este CPF.")
    
    hashed_password = get_password_hash(user_data.senha)
    
    temp_user_data = user_data.model_dump()
    temp_user_data["senha"] = hashed_password
    temp_user_data["cpf"] = cpf
    temp_user = User(**temp_user_data)
    
    session.add(temp_user)
    session.commit()
    session.refresh(temp_user)
    
    return {"message": "Primeira etapa concluída. Prossiga para o cadastro completo usando o seu CPF."}

@app.post("/users/register-second-stage/{cpf}")
def register_second_stage(cpf: str, user_data: UserSecondStage, session: Session = Depends(get_session)):
    cpf = cpf.replace('.', '').replace('-', '')
    
    user_to_update = session.exec(select(User).where(User.cpf == cpf)).first()
    if not user_to_update:
        raise HTTPException(status_code=404, detail="Usuário não encontrado. Por favor, complete a primeira etapa do cadastro.")
        
    for key, value in user_data.model_dump().items():
        setattr(user_to_update, key, value)
    
    session.add(user_to_update)
    session.commit()
    session.refresh(user_to_update)

    return {"message": "Cadastro concluído com sucesso!", "user": user_to_update}

# --- Endpoints de Usuário Comum ---

@app.post("/users/login")
def user_login(user_login: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == user_login.email)).first()
    
    if user and verify_password(user_login.senha, user.senha):
        return {"message": "Login bem-sucedido!", "cpf_usuario": user.cpf}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas"
    )

@app.post("/users/forgot-password")
def user_forgot_password(forgot_password: UserForgotPassword, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == forgot_password.email)).first()
    if user:
        recovery_token = str(uuid.uuid4())
        senha_recuperacao[user.email] = recovery_token
        print(f"Token de recuperação para {user.email}: {recovery_token}")
        return {"message": "Um token para redefinir a senha foi enviado para o seu e-mail."}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="E-mail não encontrado."
    )

@app.post("/users/reset-password")
def user_reset_password(reset_data: PasswordReset, session: Session = Depends(get_session)):
    user_email_list = [email for email, token in senha_recuperacao.items() if token == reset_data.token]
    
    if not user_email_list:
        raise HTTPException(status_code=400, detail="Token de recuperação inválido ou expirado.")
    
    user_email = user_email_list[0]
    user = session.exec(select(User).where(User.email == user_email)).first()
    
    if user:
        hashed_password = get_password_hash(reset_data.nova_senha)
        user.senha = hashed_password
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        del senha_recuperacao[user_email]
        return {"message": "Senha alterada com sucesso."}
    
    raise HTTPException(status_code=404, detail="Usuário não encontrado.")

@app.post("/users/choose-role/{cpf}")
def choose_user_role(cpf: str, role_choice: UserTypeChoice, session: Session = Depends(get_session)):
    cpf = cpf.replace('.', '').replace('-', '')
    
    user = session.exec(select(User).where(User.cpf == cpf)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if role_choice.tipo_usuario not in ["doador", "beneficiario", "oracao"]:
        raise HTTPException(status_code=400, detail="Escolha de papel inválida. Use 'doador', 'beneficiario' ou 'oracao'.")

    user.tipo_usuario = role_choice.tipo_usuario
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"message": "Papel do usuário definido com sucesso.", "tipo_usuario": user.tipo_usuario}

# --- Endpoints de Administrador ---

@app.post("/admin/login")
def admin_login(admin_login: AdminLogin):
    if admin_login.email == admin_email_padrao and verify_password(admin_login.senha, admin_senha_padrao):
        return {"message": "Login de administrador bem-sucedido!"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais de administrador inválidas."
    )

@app.post("/admin/forgot-password")
def admin_forgot_password(forgot_password: AdminForgotPassword):
    if forgot_password.email == admin_email_padrao:
        recovery_token = str(uuid.uuid4())
        senha_recuperacao[forgot_password.email] = recovery_token
        print(f"Código de recuperação para o administrador: {recovery_token}")
        return {"message": "Um código para redefinir a senha foi enviado para o e-mail do administrador."}
    
    raise HTTPException(status_code=404, detail="E-mail de administrador não encontrado.")

@app.post("/admin/reset-password")
def admin_reset_password(reset_data: AdminPasswordReset):
    global admin_senha_padrao
    if senha_recuperacao.get(admin_email_padrao) == reset_data.codigo:
        admin_senha_padrao = get_password_hash(reset_data.nova_senha)
        del senha_recuperacao[admin_email_padrao]
        return {"message": "Senha do administrador alterada com sucesso."}

    raise HTTPException(status_code=400, detail="Código de recuperação inválido.")

@app.get("/admin/doadores")
def get_doadores_info(session: Session = Depends(get_session)):
    doadores = session.exec(select(User).where(User.tipo_usuario == "doador")).all()
    return doadores

@app.get("/admin/beneficiarios")
def get_beneficiarios_info(session: Session = Depends(get_session)):
    beneficiarios = session.exec(select(User).where(User.tipo_usuario == "beneficiario")).all()
    return beneficiarios

@app.get("/admin/solicitacoes", response_model=List[Solicitacao])
def get_all_solicitacoes(session: Session = Depends(get_session)):
    solicitacoes = session.exec(select(Solicitacao)).all()
    return solicitacoes

@app.put("/admin/solicitacao/{solicitacao_id}/status", response_model=Solicitacao)
def update_solicitacao_status(
    solicitacao_id: int, 
    update_data: SolicitacaoUpdate, 
    session: Session = Depends(get_session)
):
    solicitacao = session.exec(select(Solicitacao).where(Solicitacao.id == solicitacao_id)).first()
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    
    solicitacao.status = update_data.novo_status
    
    session.add(solicitacao)
    session.commit()
    session.refresh(solicitacao)
    
    return solicitacao

# --- Endpoints Adicionais (para doadores e beneficiários) ---

@app.post("/users/doador-info/{cpf}")
def doador_info(cpf: str, doador_data: DoadorInfo, session: Session = Depends(get_session)):
    cpf = cpf.replace('.', '').replace('-', '')
    user = session.exec(select(User).where(User.cpf == cpf)).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    solicitacao = Solicitacao(
        tipo_solicitacao=TipoSolicitacao.doacao,
        descricao=f"Doação de {doador_data.tipo_doacao}: {doador_data.descricao}",
        cpf_usuario=cpf,
        usuario=user,
        status=StatusSolicitacao.pendente
    )
    session.add(solicitacao)
    session.commit()
    session.refresh(solicitacao)

    return {"message": "Informações de doador salvas com sucesso."}

@app.post("/users/beneficiario-info/{cpf}")
def beneficiario_info(cpf: str, beneficiario_data: BeneficiarioInfo, session: Session = Depends(get_session)):
    cpf = cpf.replace('.', '').replace('-', '')
    user = session.exec(select(User).where(User.cpf == cpf)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    solicitacao = Solicitacao(
        tipo_solicitacao=TipoSolicitacao.beneficio,
        descricao=f"Solicitação de ajuda: {beneficiario_data.historia_de_vida}",
        cpf_usuario=cpf,
        usuario=user,
        status=StatusSolicitacao.pendente
    )
    session.add(solicitacao)
    session.commit()
    session.refresh(solicitacao)
    
    return {"message": "Informações de beneficiário salvas com sucesso."}

@app.post("/users/oracao-info/{cpf}")
def oracao_info(cpf: str, oracao_data: OracaoInfo, session: Session = Depends(get_session)):
    cpf = cpf.replace('.', '').replace('-', '')
    user = session.exec(select(User).where(User.cpf == cpf)).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    solicitacao = Solicitacao(
        tipo_solicitacao=TipoSolicitacao.oracao,
        descricao=f"Pedido de oração: {oracao_data.descricao}",
        cpf_usuario=cpf,
        usuario=user,
        status=StatusSolicitacao.pendente
    )
    session.add(solicitacao)
    session.commit()
    session.refresh(solicitacao)

    return {"message": "Seu pedido de oração foi enviado com sucesso e será recebido por nossa equipe."}

# --- Endpoints de Visualização ---

@app.get("/users/historico/{cpf}", response_model=List[Solicitacao])
def get_historico_usuario(cpf: str, session: Session = Depends(get_session)):
    cpf = cpf.replace('.', '').replace('-', '')
    historico = session.exec(select(Solicitacao).where(Solicitacao.cpf_usuario == cpf)).all()
    
    if not historico:
        raise HTTPException(status_code=404, detail="Nenhuma solicitação encontrada para este usuário.")
    
    return historico

@app.get("/users/", response_model=List[User])
def get_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users
    
@app.get("/igreja/pix")
def get_pix_igreja():
    return {"chave_pix": chave_pix_igreja}